import re
import streamlit as st
import vertexai
import pandas as pd

# from vertexai.generative_models import GenerativeModel, ChatSession
# import google.auth
import google.generativeai as genai

# from google.generativeai import GenerativeModel, ChatSession
# from prompts import get_system_prompt

st.title("🤖 Marketing Marisa")
genai.configure(api_key="")
model = genai.GenerativeModel("gemini-1.0-pro")

SCHEMA_PATH = st.secrets.get("SCHEMA_PATH", "MARKETING_SAMPLE.ATRIUM_MARKETING")
QUALIFIED_TABLE_NAME = f"{SCHEMA_PATH}.MARKETING_LANDINGPAGE_MONTHLY_TIME_SERIES"
TABLE_DESCRIPTION = """
This table has various metrics for website landing pages (also referred to as websites) since March.
The user may describe the landing pages interchangeably as websites, pages, or web pages.
"""
# This query is optional if running Marisa on your own table, especially a wide table.
# Since this is a deep table, it's useful to tell Marisa what variables are available.
# Similarly, if you have a table with semi-structured data (like JSON), it could be used to provide hints on available keys.
# If altering, you may also need to modify the formatting logic in get_table_context() below.
METADATA_QUERY = f"SELECT VARIABLE, DEFINITION FROM {SCHEMA_PATH}.MARKETING_LANDINGPAGE_ATTRIBUTES_LIMITED;"

GEN_SQL = """
You will be acting as an AI Snowflake SQL Expert named Marketing Marisa.
Your goal is to give correct, executable sql query to users.
You will be replying to users who will be confused if you don't respond in the character of Marketing Marisa.
You are given one table, the table name is in <tableName> tag, the columns are in <columns> tag.
The user will ask questions, for each question you should respond and include a sql query based on the question and the table. 

{context}

Here are 6 critical rules for the interaction you must abide:
<rules>
1. You MUST MUST wrap the generated sql code within ``` sql code markdown in this format e.g
```sql
(select 1) union (select 2)
```
2. If I don't tell you to find a limited set of results in the sql query or question, you MUST limit the number of responses to 10.
3. Text / string where clauses must be fuzzy match e.g ilike %keyword%
4. Make sure to generate a single snowflake sql code, not multiple. 
5. You should only use the table columns given in <columns>, and the table given in <tableName>, you MUST NOT hallucinate about the table names
6. DO NOT put numerical at the very front of sql variable.
</rules>

Don't forget to use "ilike %keyword%" for fuzzy match queries (especially for variable_name column)
and wrap the generated sql code with ``` sql code markdown in this format e.g:
```sql
(select 1) union (select 2)
```

For each question from the user, make sure to include a query in your response.

Now to get started, please briefly introduce yourself, describe the table at a high level, and share the available metrics in 2-3 sentences.
Then provide 3 example questions using bullet points.
"""


@st.cache_data(show_spinner="Loading Marisa's context...")
def get_table_context(
    table_name: str, table_description: str, metadata_query: str = None
):
    table = table_name.split(".")
    conn = st.connection("snowflake")
    columns = conn.query(
        f"""
        SELECT COLUMN_NAME, DATA_TYPE FROM {table[0].upper()}.INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = '{table[1].upper()}' AND TABLE_NAME = '{table[2].upper()}'
        """,
        show_spinner=False,
    )
    columns = "\n".join(
        [
            f"- **{columns['COLUMN_NAME'][i]}**: {columns['DATA_TYPE'][i]}"
            for i in range(len(columns["COLUMN_NAME"]))
        ]
    )
    context = f"""
Here is the table name <tableName> {'.'.join(table)} </tableName>

<tableDescription>{table_description}</tableDescription>

Here are the columns of the {'.'.join(table)}

<columns>\n\n{columns}\n\n</columns>
    """
    if metadata_query:
        metadata = conn.query(metadata_query, show_spinner=False)
        metadata = "\n".join(
            [
                f"- **{metadata['VARIABLE'][i]}**: {metadata['DEFINITION'][i]}"
                for i in range(len(metadata["VARIABLE"]))
            ]
        )
        context = context + f"\n\nAvailable variables by VARIABLE:\n\n{metadata}"
    return context


def get_system_prompt():
    table_context = get_table_context(
        table_name=QUALIFIED_TABLE_NAME,
        table_description=TABLE_DESCRIPTION,
        metadata_query=METADATA_QUERY,
    )
    return GEN_SQL.format(context=table_context)

chat = model.start_chat()
if "messages" not in st.session_state:
    # system prompt includes table information, rules, and prompts the LLM to produce
    # a welcome message to the user.
    st.session_state.messages = [
        {
            "role": "system",
            "content": get_system_prompt(),
        }
    ]

# Prompt for user input and save
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})

# display the existing chat messages
for message in st.session_state.messages:
    if message["role"] == "system":
        continue
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if "results" in message:
            st.dataframe(message["results"])

# If last message is not from assistant, we need to generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):    
        response = ""
        resp_container = st.empty()
        for delta in chat.send_message(
            [m["content"] for m in st.session_state.messages],
            stream=True,
        ):
                response += delta.text or ""
                resp_container.markdown(response)

        message = {"role": "assistant", "content": response}
        # Parse the response for a SQL query and execute if available
        sql_match = re.search(r"```sql\n(.*)\n```", response, re.DOTALL)
        if sql_match:
            sql = sql_match.group(1)
            conn = st.connection("snowflake")
            message["results"] = conn.query(sql)
            st.dataframe(message["results"])
            if len(message["results"].columns) == 1:
                if pd.api.types.is_numeric_dtype(message["results"].iloc[:, 0]):
                    st.bar_chart(
                        message["results"],
                        x=list(message["results"].columns)[0],
                        y=list(message["results"].columns)[0],
                    )
                else:
                    st.write(
                        "Cannot create a bar chart with a single non-numeric column."
                    )
            else:
                st.bar_chart(
                    message["results"],
                    x=list(message["results"].columns)[0],
                    y=list(message["results"].columns)[1],
                )
        st.session_state.messages.append(message)

import re
import streamlit as st
import vertexai
import pandas as pd
import plotly.graph_objects as go
import os
from plotly_helper import plotly_dispatch

# from vertexai.generative_models import GenerativeModel, ChatSession
# import google.auth
import google.generativeai as genai

# from google.generativeai import GenerativeModel, ChatSession
# from prompts import get_system_prompt

st.title("Marketing Assistant")
SCHEMA_PATH = st.secrets.get("SCHEMA_PATH", "GFORSYTHE.MARKETINGBOT")
MARKETING_METRICS_TABLE = st.secrets.get(
    "MARKETING_METRICS_TABLE", "MARKETING_METRICS_FINAL"
)
conn = st.connection("snowflake")
metadata_query = (
    f"SELECT distinct(VARIABLE) FROM {SCHEMA_PATH}.{MARKETING_METRICS_TABLE};"
)
medium_query = f"SELECT distinct(MEDIUM) FROM {SCHEMA_PATH}.{MARKETING_METRICS_TABLE};"
title_query = f"SELECT distinct(TITLE) FROM {SCHEMA_PATH}.{MARKETING_METRICS_TABLE};"
metadata = conn.query(metadata_query, show_spinner=False)
medium = conn.query(medium_query, show_spinner=False)
title = conn.query(title_query, show_spinner=False)
# Create a list of variable names directly
variables = metadata["VARIABLE"].tolist()
mediums = medium["MEDIUM"].tolist()
titles = title["TITLE"].tolist()

with open(os.path.join("src", "sidebar.md"), "r") as sidebar_file:
    sidebar_content = sidebar_file.read()

with st.sidebar:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image("src/Atrium_FullColor_Vertical-Gray-Text.png", width=150)
        st.image("src/powered-by-snowflake.png", width=125)
    st.markdown(sidebar_content)
    med = st.selectbox("Medium", mediums, index=None, placeholder="Select Medium type")
    vars = st.selectbox(
        "Variable", variables, index=None, placeholder="Select variable type"
    )  # Select the variable by name
    ttls = st.selectbox("Title", titles, index=None, placeholder="Select Title Name")

    if ttls == None:
        st.write("What are my top ", med, "s by total", vars)
    elif med == None and vars == None and ttls != None:
        st.write("What are all my rows for title ", ttls)
    else:
        st.write("What is my total ", vars, " for ", ttls)
    on = st.toggle("SQL")

genai.configure(api_key=st.secrets.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.0-pro")

SCHEMA_PATH = st.secrets.get("SCHEMA_PATH", "GFORSYTHE.MARKETINGBOT")
QUALIFIED_TABLE_NAME = f"{SCHEMA_PATH}.{MARKETING_METRICS_TABLE}"
TABLE_DESCRIPTION = """
This table has various metrics for website landing pages (also referred to as websites), campaigns (also referred to as initiatives), opportunities (also referred to as deals), and accounts (also referred to as companies).
The above mediums are defined in the MEDIUM column. The WON column is a TRUE or FALSE column that tells us if the TITLE was won therefore TRUE or lost therefore FALSE.
"""
# This query is optional if running Assistant on your own table, especially a wide table.
# Since this is a deep table, it's useful to tell Assistant what variables are available.
# Similarly, if you have a table with semi-structured data (like JSON), it could be used to provide hints on available keys.
# If altering, you may also need to modify the formatting logic in get_table_context() below.
METADATA_QUERY = f"SELECT VARIABLE, DEFINITION FROM {SCHEMA_PATH}.MARKETING_ATTRIBUTES;"
MEDIUM_QUERY = f"SELECT MEDIUM, DESCRIPTION FROM {SCHEMA_PATH}.MARKETING_MEDIUMS;"
GEN_SQL = """
You will be acting as an AI Snowflake SQL Expert named Marketing Assistant.
Your goal is to give correct, executable sql query to users.
You will be replying to users who will be confused if you don't respond in the character of Marketing Assistant.
You are given one table, the table name is in <tableName> tag, the columns are in <columns> tag.
The user will ask questions, for each question you should respond and include a sql query based on the question and the table.
The table is set up so you should only need to filter and aggregate based on the users input. 

{context}

Here are 15 critical rules for the interaction you MUST abide:
<rules>
1. You MUST MUST wrap the generated sql code within ``` sql code markdown in this format e.g
```sql
(select 1) union (select 2)
```
2. If I don't tell you to find a limited set of results in the sql query or question, you MUST limit the number of responses to 12 and order descending.
3. Text / string where clauses must be fuzzy match and in all capital letters e.g ilike %KEYWORD%
4. Make sure to generate a single snowflake sql code, not multiple. 
5. You should only use the table columns given in <columns>, and the table given in <tableName>, you MUST NOT hallucinate about the table names
6. DO NOT put numerical at the very front of sql variable.
7. When the user includes total you need to sum the VALUE for ALL months and years except if the VARIABLE is CONVERSION RATE then use average.
8. You MUST filter on MEDIUM and VARIABLE EVERYTIME based on the user input.
9. Only use case statements when users want to compare two variables.
10. You MUST put the WHERE statement before the GROUP BY in the SQL query.
11. ONLY aggregate on the VALUE column.
12. Do not use DISTINCT. 
13. Never group by ACCOUNT, WEB PAGE, OPPORTUNITY or CAMPAIGN, instead TITLE, MONTH, or YEAR.
14. Only use the WON column when the user is talking about win or lose.
15. You must select columns TITLE and an aggregate on VALUE. DO NOT return a column name that is not listed in <columns>
</rules>

Don't forget to use "ilike %keyword%" for fuzzy match queries (especially for VARIABLE, MEDIUM, and WON columns)
and wrap the generated sql code with ``` sql code markdown in this format for comparing two variables e.g:
```sql
select 
    TITLE,
    SUM(VALUE) AS insert_variable
from GFORSYTHE.MARKETINGBOT.MARKETING_METRICS_FINAL_MOCK_A
WHERE MEDIUM ILIKE '%MEDIUM%'
AND VARIABLE ILIKE '%VARIABLE%'
group by TITLE
ORDER BY INSERT VARIABLE DESC
LIMIT 12
```
or
```
select 
    MONTH,
    SUM(VALUE) AS insert_variable
from GFORSYTHE.MARKETINGBOT.MARKETING_METRICS_FINAL_MOCK_A
WHERE MEDIUM ILIKE '%MEDIUM%'
AND VARIABLE ILIKE '%VARIABLE%'
AND YEAR = 2023
group by MONTH
ORDER BY INSERT VARIABLE DESC
LIMIT 12
```

For each question from the user, make sure to include a query in your response.

Now to get started say 'Hello! What questions can I answer for you today?' but do not provide any examples.
"""


@st.cache_data(show_spinner="Loading Assistant's context...")
def get_table_context(
    table_name: str,
    table_description: str,
    medium_query: str = None,
    metadata_query: str = None,
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
        if medium_query:
            metadata = conn.query(medium_query, show_spinner=False)
            metadata = "\n".join(
                [
                    f"- **{metadata['MEDIUM'][i]}**: {metadata['DESCRIPTION'][i]}"
                    for i in range(len(metadata["MEDIUM"]))
                ]
            )
        context = context + f"\n\nAvailable medium by MEDIUM:\n\n{metadata}"
    return context


def get_system_prompt():
    table_context = get_table_context(
        table_name=QUALIFIED_TABLE_NAME,
        table_description=TABLE_DESCRIPTION,
        metadata_query=METADATA_QUERY,
        medium_query=MEDIUM_QUERY,
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

# Display the rest of the messages based on the toggle
for index, message in enumerate(st.session_state.messages):
    if message["role"] == "system":
        continue
    if message["role"] == "assistant":
        with st.chat_message(message["role"], avatar="src/bot-static.png"):
            if index == 0 or on:
                st.write(message["content"])
            if "results" in message:
                st.dataframe(message["results"])
                plotly_dispatch(message["results"], st)
    if message["role"] != "assistant":
        with st.chat_message(
            message["role"], avatar="src/Atrium_FullColor_Vertical-Gray-Text.png"
        ):
            st.write(message["content"])
# If last message is not from assistant, we need to generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant", avatar="src/bot-static.png"):
        response = ""
        resp_container = st.empty()
        for delta in chat.send_message(
            [m["content"] for m in st.session_state.messages],
            stream=True,
        ):
            response += delta.text or ""
            if index == 0 or on:
                resp_container.markdown(response)

        message = {"role": "assistant", "content": response}
        # Parse the response for a SQL query and execute if available
        sql_match = re.search(r"```sql\n(.*)\n```", response, re.DOTALL)
        if sql_match:
            try:
                sql = sql_match.group(1)
                conn = st.connection("snowflake")
                message["results"] = conn.query(sql)
                st.dataframe(message["results"])
                plotly_dispatch(message["results"], st)
            except Exception as e:
                ## st.error(f"An error occurred while executing the SQL query: {e}")
                error_message = (
                    "Sorry, that didn't seem to work. Please rephrase your query."
                )
                st.write(f"{error_message}")
                message["content"] += f"\n\n:warning: **Error:** {error_message}"
        st.session_state.messages.append(message)

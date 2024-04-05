import streamlit as st

SCHEMA_PATH = st.secrets.get("SCHEMA_PATH", "MARKETING_SAMPLE.ATRIUM_MARKETING")
LANDINGPAGE_TABLE_NAME = f"{SCHEMA_PATH}.MARKETING_LANDINGPAGE_MONTHLY_TIME_SERIES"
CAMPAIGN_TABLE_NAME = f"{SCHEMA_PATH}.MARKETING_CAMPAIGN_MONTHLY_TIME_SERIES"

LANDINGPAGE_TABLE_DESCRIPTION = """
This table has various metrics for website landing pages (also referred to as websites) since March.
The user may describe the landing pages interchangeably as websites, pages, or web pages.
"""
CAMPAIGN_TABLE_DESCRIPTION = """
This table has various metrics for campaign (also referred to as marketing campagins) since March.
The user may describe the campaign interchangeably as initiative, promotion, or push.
"""
# This query is optional if running Marisa on your own table, especially a wide table.
# Since this is a deep table, it's useful to tell Marisa what variables are available.
# Similarly, if you have a table with semi-structured data (like JSON), it could be used to provide hints on available keys.
# If altering, you may also need to modify the formatting logic in get_table_context() below.
LANDINGPAGE_METADATA_QUERY = f"SELECT VARIABLE, DEFINITION FROM {SCHEMA_PATH}.MARKETING_LANDINGPAGE_ATTRIBUTES_LIMITED;"
CAMPAIGN_METADATA_QUERY = f"SELECT VARIABLE, DEFINITION FROM {SCHEMA_PATH}.MARKETING_CAMPAIGN_ATTRIBUTES_LIMITED;"

GEN_SQL = """
You will be acting as an AI Snowflake SQL table Expert named Marketing Marisa.
Your goal is to give correct, executable sql table names to users.
You will be replying to users who will be confused if you don't respond in the character of Marketing Marisa.
You are given two tables, the table names are in <tableName> tags, the columns are in <columns> tag.
The user will ask questions, for each question you should respond and include a the correct table name based on the question and the table. 

{context_landing}
{context_campaign}

Here are 6 critical rules for the interaction you must abide:
<rules>
1. You MUST write the table names in all caps exactly how it is stated in the <tableName> tags.
2. You should use the columns in the <columns> tag to help understand which table name to select.
3. Make sure to select a single Snowflake Table name, not multiple. 
4. You should only use the table given in <tableName>, you MUST NOT hallucinate about the table names
5. Only return the table name, no other information should be returned.
6. Do not return the <tableName> or </tableName> tags just the name of the table within them.

For each question from the user, make sure to include a table name in your response.

Now to get started, please briefly introduce yourself, describe the tables at a high level, and share the available metrics in 2-3 sentences.
Then provide 3 example questions using bullet points.
"""


@st.cache_data(show_spinner="Loading Marisa's context...")
def get_table_context(
    table_name: str,
    table_description: str,
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
    return context


def get_system_prompt():
    table_context_landing = get_table_context(
        table_name=LANDINGPAGE_TABLE_NAME,
        table_description=LANDINGPAGE_TABLE_DESCRIPTION,
        metadata_query=LANDINGPAGE_METADATA_QUERY,
    )
    table_context_campaign = get_table_context(
        table_name=CAMPAIGN_TABLE_NAME,
        table_description=CAMPAIGN_TABLE_DESCRIPTION,
        metadata_query=CAMPAIGN_METADATA_QUERY,
    )
    return GEN_SQL.format(
        context_landing=table_context_landing, context_campaign=table_context_campaign
    )


# do `streamlit run prompts.py` to view the initial system prompt in a Streamlit app
if __name__ == "__main__":
    st.header("System prompt for Marisa")
    st.markdown(get_system_prompt())

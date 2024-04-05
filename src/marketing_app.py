from google.cloud import aiplatform
import vertexai
from vertexai.generative_models import GenerativeModel, ChatSession
import re
import streamlit as st
from prompts import get_system_prompt

st.title("☃️ Marketing Marisa")

# Initialize the chat messages history
project_id = "quantum-backup-415716"
location = "us-central1"
vertexai.init(project=project_id, location=location)
model = GenerativeModel("gemini-1.0-pro")
chat = model.start_chat()
if "messages" not in st.session_state:
    # system prompt includes table information, rules, and prompts the LLM to produce
    # a welcome message to the user.
    st.session_state.messages = [{"role": "system", "content": get_system_prompt()}]

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

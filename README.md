# MarketingBot

A chatbot built on the Gemini API to write SQL queries based on user input and then connection to Snowflake to run the queries.

## Description

The purpose of our project is to create a chatbot that marketing teams with minimal sql coding can ask the Chatbot questions about the data and the chatbot can do the sql writing for them. The chatbot utilizes the Gemini API and the Gemini-1.0-Pro model to take in the user's questions and return SQL queries. Before the SQl queries we have set the context to the Chatbot by giving it guidelines on how to generate the SQL as well as what table name to reference within the SQL query. Once the Gemini model has written the SQL query it is pushed to be run via a Snowflake connection. The Snowflake connection returns a dataframe and if applicable a bar chart in a streamlit app.

## Getting Started

### Dependencies

- Gemini Access specifically to the Google Cloud platform
- Google CLI or API key
- Snowflake Account with appropriate access to query the data

### Installing

- Clone repo
- Set up Snowflake connection in secrets.toml
- Set up API Key or default credentials via Google CLI (currently set up through Google CLI)
- Create a conda environment

```
conda create --name <ENV_NAME>
```

- Activate conda environment

```
conda activate <ENV_NAME>
```

- Install requirements to conda environment
  '''
  pip install -r requirements.txt
  '''

### Executing program

- Swap out Google Cloud project name in marketing_app.py
- Run the below in the command line

```
streamlit run src/marketing_bot.py
```

## Authors

Based off this Snowflake Quickstart: https://github.com/Snowflake-Labs/sfguide-frosty-llm-chatbot-on-streamlit-snowflake
Maddie Fuchs

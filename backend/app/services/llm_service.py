import google.generativeai as genai
import os
from dotenv import load_dotenv
import re

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def generate_sql_with_gemini(prompt: str) -> str:
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text.strip()


def clean_sql_query(sql_query: str, column_names=None) -> str:
    sql_query = sql_query.strip()

    # Extraer solo el contenido entre backticks si existe
    match = re.search(r"```(?:sql)?(.*?)```", sql_query, re.DOTALL | re.IGNORECASE)
    if match:
        sql_query = match.group(1).strip()

    if sql_query.lower().startswith("sql"):
        sql_query = sql_query[3:].strip()

    # Reject if it contains Python code or keywords
    forbidden = [
        "def ",
        "python",
        "return ",
        ":",
        '"""',
        "'''",
        "import ",
        "pandas",
        "DataFrame",
    ]
    if any(bad in sql_query.lower() for bad in forbidden):
        raise ValueError("The generated response is not a valid SQL query.")

    # Block dangerous commands at the beginning of the line
    pattern = r"^\s*(drop|delete|update|insert|alter|create|replace)\b"
    if re.search(pattern, sql_query, re.IGNORECASE | re.MULTILINE):
        raise ValueError("Forbidden SQL command detected.")

    # Validate columns
    if column_names and not any(col in sql_query for col in column_names):
        raise ValueError("Your question is out of scope for the available data.")

    return sql_query

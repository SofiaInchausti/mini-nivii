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


def clean_sql_query1(sql_query: str) -> str:
    sql_query = sql_query.strip()
    if sql_query.startswith("```"):
        sql_query = sql_query.split("```", 1)[1] if "```" in sql_query else sql_query
    sql_query = (
        sql_query.replace("sql", "", 1).strip()
        if sql_query.startswith("sql")
        else sql_query
    )
    sql_query = sql_query.replace("```", "").strip()

    return sql_query


def clean_sql_query(sql_query: str, column_names=None) -> str:
    sql_query = sql_query.strip()

    # Extraer solo el contenido entre backticks si existe
    match = re.search(r"```(?:sql)?(.*?)```", sql_query, re.DOTALL | re.IGNORECASE)
    if match:
        sql_query = match.group(1).strip()

    # Eliminar 'sql' solo si está al principio
    if sql_query.lower().startswith("sql"):
        sql_query = sql_query[3:].strip()

    # Rechazar si contiene código Python o palabras clave
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

    # Bloquear comandos peligrosos al inicio de línea
    pattern = r"^\s*(drop|delete|update|insert|alter|create|replace)\b"
    if re.search(pattern, sql_query, re.IGNORECASE | re.MULTILINE):
        raise ValueError("Forbidden SQL command detected.")

    # Validar columnas (opcional)
    if column_names and not any(col in sql_query for col in column_names):
        raise ValueError("Your question is out of scope for the available data.")

    return sql_query

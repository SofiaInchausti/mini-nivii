from fastapi import APIRouter, Body, HTTPException
from app.services.response_service import ResponseService
from app.services.llm_service import generate_sql_with_gemini, clean_sql_query
from app.services.csv_service import query_csv_with_sql
import pandas as pd
from app.utils.chart_utils import suggest_chart_type, build_chart_data

router = APIRouter()


@router.get("/")
def get_responses():
    service = ResponseService()
    responses = service.list_responses()
    service.close()
    return responses


@router.post("/responses")
def create_response(question: str = Body(..., embed=True)):
    service = ResponseService()
    sql_query = None
    result = None
    status = "error"
    error_message = None

    # 1. Leer el CSV
    try:
        df = pd.read_csv("data/data.csv")
        column_names = df.columns.tolist()
    except Exception as e:
        error_message = f"Error reading CSV: {str(e)}"
        service.save_response(question, sql_query, result, None, status, error_message)
        service.close()
        raise HTTPException(status_code=500, detail=error_message)

    # 2. Generar el prompt y la query
    prompt = f"""
        You are an assistant that converts natural language questions into valid SQLite SQL queries.
        You have access to a pandas DataFrame called 'df' with the following columns: {', '.join(column_names)}.

        **CRITICAL INSTRUCTION: MONTH CONVERSION**
        The 'year_month' column in your DataFrame follows the format 'YYYY-M' for months 1 through 9 (e.g., '2024-3' for March) and 'YYYY-MM' for months 10 through 12 (e.g., '2024-10' for October).

        When the user's question includes a month name, you MUST convert it to its corresponding number. It is crucial that you use A SINGLE DIGIT for months 1-9 and TWO DIGITS for months 10-12, without leading zeros for single-digit months.

        Here's the exact mapping you MUST use:
        - January/january → 1
        - February/february → 2
        - March/march → 3
        - April/april → 4
        - May/may → 5
        - June/june → 6
        - July/july → 7
        - August/august → 8
        - September/september → 9
        - October/october → 10
        - November/november → 11
        - December/december → 12

        If the user question mentions only a month without specifying a year,
        you must use the most recent available year in the data (assume it is 2024 for now).

        **CRITICAL INSTRUCTION: QUERY TYPES AND COLUMN USAGE**
        For questions about "top-selling products" or similar, you MUST use 'product_name' for grouping and 'quantity' (or 'sales', if 'quantity' is not available and 'sales' represents sold units/value) for summing to determine the top items. Always include 'GROUP BY product_name' and 'ORDER BY [sum_column] DESC'.

        Only return the SQL query. No explanations, markdown, or additional code.


        """
    prompt1 = f"""
        You are an assistant that converts natural language questions into valid SQLite SQL queries.
        You have access to a pandas DataFrame called 'df' with the following columns: {', '.join(column_names)}.

        The DataFrame includes a preprocessed column called 'year_month' in the format 'YYYY-MM'.
        When the question includes a month name, you must convert it to a two-digit number:
        - January/january → 1
        - February/february → 2
        - March/march → 3
        - April/april → 4
        - May/may → 5
        - June/june → 6
        - July/july → 7
        - August/august → 8
        - September/september → 9
        - October/october → 10
        - November/november → 11
        - December/december → 12

        If the user question mentions only a month without specifying a year,
        you must use the most recent available year in the data (assume it is 2024 for now).

        Only return the SQL query. No explanations, markdown, or code.

        Example:

        Question: "What was the top-selling product in <month> <year>?"
        SQL:
        SELECT product_name, SUM(quantity) AS total_quantity
        FROM df
        WHERE year_month = '<year>-<mm>'
        GROUP BY product_name
        ORDER BY total_quantity DESC
        LIMIT
        """

    try:
        sql_query = generate_sql_with_gemini(prompt)
        sql_query = clean_sql_query(sql_query)
    except Exception as e:
        error_message = f"Error generating SQL with Gemini: {str(e)}"
        service.save_response(question, sql_query, result, None, None, status, error_message)
        service.close()
        return {"error": error_message, "sql_query": None, "result": None}
    # 3. Validar la query generada
    if "?" in sql_query:
        error_message = "The generated SQL query contains placeholders ('?'). Please rephrase your question or try again."
        service.save_response(question, sql_query, result, None, None, status, error_message)
        service.close()
        return {"error": error_message, "sql_query": sql_query, "result": None}
    if not any(col in sql_query for col in column_names):
        error_message = "The generated SQL query does not reference any valid columns."
        service.save_response(question, sql_query, result, None, None, status, error_message)
        service.close()
        return {"error": error_message, "sql_query": sql_query, "result": None}

    # 4. Ejecuta la query sobre el CSV
    result = query_csv_with_sql(sql_query, csv_path="data/data.csv")
    if isinstance(result, dict) and "error" in result:
        error_message = f"Error executing SQL: {result['error']}"
        service.save_response(question, sql_query, None, None, None, status, error_message)
        service.close()
        return {"error": error_message, "sql_query": sql_query, "result": None}

    # 5. Si el resultado está vacío
    if not result:
        error_message = "No data found for your query."
        service.save_response(question, sql_query, [], None, None, status, error_message)
        service.close()
        return {"error": error_message, "sql_query": sql_query, "result": []}

    # 6. Caso de éxito
    chart_type = suggest_chart_type(sql_query, result)
    chart_data = build_chart_data(result, chart_type)
    status = "success"
    error_message = None
    response_obj = service.save_response(question, sql_query, result, chart_type, chart_data, status, error_message)
    service.close()
    return {
        "id": response_obj.id,
        "question": response_obj.question,
        "sql_query": response_obj.sql_query,
        "result": result,
        "date": response_obj.date.isoformat() if response_obj.date else None,
        "chart": response_obj.chart,
        "chart_data": chart_data
    }

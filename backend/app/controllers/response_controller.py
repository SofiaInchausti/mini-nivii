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

    try:
        df = pd.read_csv("data/data.csv")
        column_names = df.columns.tolist()
    except Exception as e:
        error_message = f"Error reading CSV: {str(e)}"
        service.save_response(question, sql_query, result, None, status, error_message)
        service.close()
        raise HTTPException(status_code=500, detail=error_message)


    prompt = f"""
        You are an assistant that converts natural language questions into valid SQLite SQL queries.
        You have access to a pandas DataFrame called 'df' with the following columns: {', '.join(column_names)}.

        **CRITICAL INSTRUCTION: MONTH CONVERSION**
        When the user's question includes a month name, you MUST convert it to its corresponding number.

        Here's the exact mapping you MUST use:
        - January/january → 01
        - February/february → 02
        - March/march → 03
        - April/april → 04
        - May/may → 05
        - June/june → 06
        - July/july → 07
        - August/august → 08
        - September/september → 09
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
- January/january → 01
- February/february → 02
- March/march → 03
- April/april → 04
- May/may → 05
- June/june → 06
- July/july → 07
- August/august → 08
- September/september → 09
- October/october → 10
- November/november → 11
- December/december → 12

If the user question mentions only a month without specifying a year,
you must use the most recent available year in the data (assume it is 2024 for now).
If the user question mentions "top N" (where N is a number), use `LIMIT N` in the SQL query.
If no number is specified, use `LIMIT 1`.

Only return the SQL query. No explanations, markdown, or code.

Examples:

Question: "What was the top-selling product in November 2024?"
SQL:
SELECT product_name, SUM(quantity) AS total_quantity
FROM df
WHERE year_month = '2024-11'
GROUP BY product_name
ORDER BY total_quantity DESC
LIMIT 1;

Question: "What was the top-selling product in December 2024?"
SQL:
SELECT product_name, SUM(quantity) AS total_quantity
FROM df
WHERE year_month = '2024-12'
GROUP BY product_name
ORDER BY total_quantity DESC
LIMIT 1;

Question: "What was the top-selling product in September 2024?"
SQL:
SELECT product_name, SUM(quantity) AS total_quantity
FROM df
WHERE year_month = '2024-09'
GROUP BY product_name
ORDER BY total_quantity DESC
LIMIT 1;

Question: "What were the three top-selling products in 2024?"
SQL:
SELECT product_name, SUM(quantity) AS total_quantity
FROM df
WHERE year_month LIKE '2024%'
GROUP BY product_name
ORDER BY total_quantity DESC
LIMIT 3;

Now, generate the SQL query for this question only:
Question: "What was the top-selling product in October?"
SQL:
"""


    try:
        sql_query = generate_sql_with_gemini(prompt)
        sql_query = clean_sql_query(sql_query)
    except Exception as e:
        error_message = f"Error generating SQL with Gemini: {str(e)}"
        service.save_response(question, sql_query, result, None, None, status, error_message)
        service.close()
        return {"error": error_message, "sql_query": None, "result": None}
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

    # Execute the query on the CSV
    result = query_csv_with_sql(sql_query, csv_path="data/data.csv")
    if isinstance(result, dict) and "error" in result:
        error_message = f"Error executing SQL: {result['error']}"
        service.save_response(question, sql_query, None, None, None, status, error_message)
        service.close()
        return {"error": error_message, "sql_query": sql_query, "result": None}

    if not result:
        error_message = "No data found for your query."
        service.save_response(question, sql_query, [], None, None, status, error_message)
        service.close()
        return {"error": error_message, "sql_query": sql_query, "result": []}

    # Success
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

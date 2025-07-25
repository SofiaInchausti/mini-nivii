# app/services/csv_service.py
import pandas as pd
from pandasql import sqldf
import traceback


def query_csv_with_sql(sql_query, csv_path="data/data.csv"):
    try:
        df = pd.read_csv(csv_path)
        # ✅ Convierte fecha desde MM/DD/YYYY
        df["date"] = pd.to_datetime(df["date"], format="%m/%d/%Y", errors="coerce")

        # ✅ Agrega columna auxiliar para SQLite
        df["year_month"] = df["date"].dt.strftime("%Y-%m")
        df["day"] = df["date"].dt.day
        df["year"] = df["date"].dt.year
        df["month"] = df["date"].dt.month

        result_df = sqldf(sql_query, {"df": df})

        return result_df.to_dict(orient="records")
    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}

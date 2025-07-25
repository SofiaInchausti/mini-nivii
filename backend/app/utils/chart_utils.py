def suggest_chart_type(sql_query: str, result: list) -> str:
    sql_lower = sql_query.lower()
    if "group by" in sql_lower:
        return "bar"
    if "count(" in sql_lower or "sum(" in sql_lower:
        return "bar"
    if "date" in sql_lower or "time" in sql_lower or "year_month" in sql_lower:
        return "line"
    if len(result) == 1 and len(result[0]) == 2:
        return "pie"
    return "table"

def build_chart_data(result, chart_type):
    if not result or not isinstance(result, list) or not result or not isinstance(result[0], dict):
        return None

    if chart_type == "bar":
        # Verifica que las claves existan
        if "product_name" in result[0] and "total_quantity" in result[0]:
            labels = [item["product_name"] for item in result if "product_name" in item]
            data = [item["total_quantity"] for item in result if "total_quantity" in item]
            return {
                "labels": labels,
                "datasets": [
                    {
                        "label": "Sales",
                        "data": data,
                        "backgroundColor": ["#60a5fa", "#34d399", "#fbbf24", "#f87171"][:len(labels)]
                    }
                ]
            }
    # Puedes agregar más tipos de gráficos aquí
    return None

import pytest
from app.services.llm_service import clean_sql_query
from app.utils.chart_utils import suggest_chart_type


def test_clean_sql_query_valid():
    sql = "SELECT * FROM df;"
    assert clean_sql_query(sql) == sql


def test_clean_sql_query_forbidden():
    with pytest.raises(ValueError):
        clean_sql_query("DROP TABLE df;")


def test_suggest_chart_type_bar():
    sql = "SELECT product, COUNT(*) FROM df GROUP BY product;"
    result = [{"product": "A", "count": 10}, {"product": "B", "count": 5}]
    assert suggest_chart_type(sql, result) == "bar"

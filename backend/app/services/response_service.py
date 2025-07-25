import json
from app.models.response_model import Response
from app.models.database import SessionLocal


class ResponseService:
    def __init__(self):
        self.db = SessionLocal()

    def save_response(self, question, sql_query, result, chart, chart_data, status, error_message):
        response_obj = Response(
            question=question,
            sql_query=sql_query,
            result=json.dumps(result),
            chart=chart,
            chart_data=json.dumps(chart_data) if chart_data else None,
            status=status,
            error_message=error_message,
        )
        self.db.add(response_obj)
        self.db.commit()
        self.db.refresh(response_obj)
        return response_obj

    def list_responses(self):
        responses = self.db.query(Response).all()
        return [
            {
                "id": r.id,
                "question": r.question,
                "sql_query": r.sql_query,
                "result": json.loads(r.result),
                "date": r.date.isoformat() if r.date else None,
                "chart": r.chart,
                "chart_data": json.loads(r.chart_data) if r.chart_data else None,
            }
            for r in responses
        ]

    def close(self):
        self.db.close()

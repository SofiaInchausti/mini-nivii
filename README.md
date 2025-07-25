# Mini Nivii – Take-Home Challenge

## Objective

Recreate a simplified version of Nivii: a full-stack app that allows users to ask natural language questions about a dataset and receive an automatic chart as a response.

---

## Features

- **Input:** Field for users to enter a natural language question about the data (e.g., “What was the top-selling product in March?”).
- **Output:** An area that displays a chart by default as the answer.
- If the result cannot be charted, a table, summary, or clear message is shown.

---

## How does it work?

1. **Data loading:**  
   The system loads the provided CSV into a SQL database (SQLite by default for local development).
2. **Question translation:**  
   The backend uses a generative model (LLM) to translate the user's question into a SQL query.
3. **Execution and visualization:**  
   The backend runs the SQL query, processes the result, and returns data ready for charting. The frontend auto-selects the most appropriate chart type.
4. **Error handling:**  
   If the result cannot be charted, a table, summary, or explanatory message is shown.

---

## Tech Stack

- **Backend:** Python (FastAPI, SQLAlchemy, Pandas, LLM API)
- **Frontend:** React + Chart.js
- **Database:** SQLite (development) / PostgreSQL (Docker)
- **Visualization:** Chart.js
- **Containers:** Docker & Docker Compose

---

## Project Structure

```text
mini-nivii/
  backend/
    app/
      controllers/
      models/
      schemas/
      services/
      utils/
    data/
      data.csv
      data.db
    requirements.txt
  frontend/
    src/
    public/
    package.json
  docker-compose.yml
```

---

## Setup & Usage

### 1. Clone the repository

```bash
git clone <repo-url>
cd mini-nivii
```

### 2. Environment variables

- If you use LLMs that require an API Key, create a `.env` file in `backend/` with your key:
  ```
  LLM_API_KEY=your_key
  ```

### 3. Start services with Docker Compose

```bash
docker-compose up --build
```

- The frontend will be available at [http://localhost:3000](http://localhost:3000)
- The backend at [http://localhost:8000](http://localhost:8000)
- The PostgreSQL database is initialized automatically.

### 4. (Optional) Run locally without Docker

#### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Design Decisions & Trade-offs

- **Simplicity:** Prioritized a clear and modular architecture, following the KISS principle.
- **Database:**  
  - SQLite for local development (easy to use and portable).
  - PostgreSQL in Docker to simulate a more realistic, multi-user environment.
- **Data loading:**  
  - The backend can load data from a CSV using Pandas.
  - To share the same data, include the `.db` file or the CSV.
- **LLM:**  
  - The backend translates questions to SQL using a generative model (provider can be swapped easily).
- **Visualization:**  
  - The frontend auto-selects the chart type based on the received data.
  - If charting is not possible, a table or clear message is shown.

---

## Scalability

### Multi-user

- **Backend:**  
  - Use a robust database (PostgreSQL) and independent sessions.
  - Add authentication and access control if needed.
- **Frontend:**  
  - Maintain question history per user.
  - Use websockets for real-time updates if desired.

### Large datasets / multiple tables

- **Database:**  
  - Index relevant columns.
  - Optimize generated SQL queries.
  - Use pagination and aggregations in the backend.
- **Backend:**  
  - Limit the size of results sent to the frontend.
  - Process and summarize data before sending.
- **Frontend:**  
  - Efficient visualization (virtualization, lazy loading).
  - Allow users to filter and explore the data.

---

## Testing

- Unit and integration tests for core services (see `backend/tests/`).

---

## Bonus
  - Question and answer history.
---







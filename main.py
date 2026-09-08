import os
from fastapi import FastAPI
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from databricks import sql
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "https://spain-fuel-prices-dashboard.vercel.app",
        "https://spain-fuel-prices-dashboard-cyl1km6ai-skynet23.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_connection():
    return sql.connect(
        server_hostname=os.getenv("DATABRICKS_SERVER_HOSTNAME"),
        http_path=os.getenv("DATABRICKS_HTTP_PATH"),
        access_token=os.getenv("DATABRICKS_TOKEN"),
    )

@app.get("/stations")
def get_stations(
    page: int = 1,
    page_size: int = 50,
    provincia: Optional[str] = None,
    fuel_type: Optional[str] = None,
):
    offset = (page - 1) * page_size

    query = "SELECT * FROM gold_fuel_prices_by_type WHERE 1=1"

    if provincia:
        query += f" AND provincia = '{provincia}'"

    if fuel_type:
        query += f" AND fuel_type = '{fuel_type}'"

    query += f" LIMIT {page_size} OFFSET {offset}"

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)

            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

            data = [dict(zip(columns, row)) for row in rows]

            return {
                "data": data,
                "page": page,
                "page_size": page_size,
            }

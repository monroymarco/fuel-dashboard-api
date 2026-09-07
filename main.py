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
    allow_origins=["*"],
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
def get_stations(provincia: Optional[str] = None, fuel_type: Optional[str] = None):
    query = "SELECT * FROM gold_fuel_prices_by_type WHERE 1=1"
    if provincia:
        query += f" AND provincia = '{provincia}'"
    if fuel_type:
        query += f" AND fuel_type = '{fuel_type}'"
    query += " LIMIT 15000"

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]

import azure.functions as func
import openai
import pyodbc
import requests
import os
import logging
import json

# Load environment variables from Azure Function settings
AZURE_SEARCH_API_KEY = os.getenv("AZURE_SEARCH_API_KEY")
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SQL_SERVER = os.getenv("SQL_SERVER")
SQL_DATABASE = os.getenv("SQL_DATABASE")
SQL_USERNAME = os.getenv("SQL_USERNAME")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")
INDEX_NAME = "items-index"
BATCH_SIZE = 500

def main(mytimer: func.TimerRequest) -> None:
    logging.info("Azure Function triggered: Checking for changes in SQL Database.")

    # Azure SQL Connection
    connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SQL_SERVER};DATABASE={SQL_DATABASE};UID={SQL_USERNAME};PWD={SQL_PASSWORD}'
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()

    # ✅ Step 1: Check for new/updated records in the last 24 hours
    cursor.execute("""
        SELECT ITEM#, description, status, commodity, CurrentBalance, last_updated
        FROM your_table
        WHERE last_updated > DATEADD(day, -1, GETDATE())
    """)
    updated_rows = cursor.fetchall()

    # ✅ Step 2: Fetch deleted records in the last 24 hours
    cursor.execute("""
        SELECT ITEM#
        FROM deleted_items_table
        WHERE deleted_at > DATEADD(day, -1, GETDATE())
    """)
    deleted_rows = [row[0] for row in cursor.fetchall()]

    # ✅ Step 3: Generate OpenAI Embeddings
    def generate_embedding(text):
        try:
            response = openai.Embedding.create(
                input=text,
                model="text-embedding-ada-002"
            )
            return response["data"][0]["embedding"]
        except Exception as e:
            logging.error(f"OpenAI API Error: {e}")
            return [0.0] * 1536  # Return a zero vector if API fails

    # ✅ Step 4: Prepare Data for Indexing
    data_to_index = []
    for row in updated_rows:
        item = {
            "@search.action": "mergeOrUpload",
            "ITEM#": str(row[0]),
            "description": row[1],
            "vector_embedding": generate_embedding(row[1]),
            "status": row[2],
            "commodity": row[3],
            "CurrentBalance": int(row[4])
        }
        data_to_index.append(item)

    # ✅ Step 5: Prepare Data for Deletion
    data_to_delete = [{"@search.action": "delete", "ITEM#": str(item)} for item in deleted_rows]

    # ✅ Step 6: Upload Changes to Azure AI Search
    def upload_to_search(data):
        if not data:
            return
        headers = {"Content-Type": "application/json", "api-key": AZURE_SEARCH_API_KEY}
        payload = {"value": data}
        response = requests.post(f"{AZURE_SEARCH_ENDPOINT}/indexes/{INDEX_NAME}/docs/index?api-version=2023-07-01", headers=headers, json=payload)
        logging.info(response.json())

    # ✅ Step 7: Upload in Batches
    for i in range(0, len(data_to_index), BATCH_SIZE):
        upload_to_search(data_to_index[i:i+BATCH_SIZE])

    for i in range(0, len(data_to_delete), BATCH_SIZE):
        upload_to_search(data_to_delete[i:i+BATCH_SIZE])

    cursor.close()
    conn.close()
    logging.info("Azure Function completed: Index updated successfully.")

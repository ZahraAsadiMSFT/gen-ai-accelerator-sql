import openai
import pyodbc
import requests

# Azure AI Search & OpenAI API details
AZURE_SEARCH_API_KEY = "your_azure_search_api_key"
AZURE_SEARCH_ENDPOINT = "https://yoursearchservice.search.windows.net"
INDEX_NAME = "items-index"
OPENAI_API_KEY = "your_openai_api_key"

# Azure SQL Database Connection
server = 'your_server.database.windows.net'
database = 'your_database'
username = 'your_username'
password = 'your_password'
connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

# Connect to SQL
conn = pyodbc.connect(connection_string)
cursor = conn.cursor()

# Fetch updated data (Modify query to match your table structure)
cursor.execute("""
    SELECT ITEM#, description, status, commodity, CurrentBalance
    FROM your_table
""")
rows = cursor.fetchall()

# Function to generate OpenAI embeddings
def generate_embedding(text):
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response["data"][0]["embedding"]

# Prepare data for indexing
data_to_index = []
for row in rows:
    item = {
        "@search.action": "mergeOrUpload",  # Ensures updates instead of duplicates
        "ITEM#": str(row[0]),  
        "description": row[1],
        "vector_embedding": generate_embedding(row[1]),  # Generate OpenAI embedding
        "status": row[2],
        "commodity": row[3],
        "CurrentBalance": int(row[4])  # Convert balance to integer
    }
    data_to_index.append(item)

# Upload data to Azure AI Search
headers = {
    "Content-Type": "application/json",
    "api-key": AZURE_SEARCH_API_KEY
}
payload = {"value": data_to_index}

response = requests.post(f"{AZURE_SEARCH_ENDPOINT}/indexes/{INDEX_NAME}/docs/index?api-version=2023-07-01", headers=headers, json=payload)

print(response.json())  # Should return success response

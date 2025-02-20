import openai
import requests
import os
import json
from azure.storage.blob import BlobServiceClient

# Load environment variables
AZURE_SEARCH_API_KEY = os.getenv("AZURE_SEARCH_API_KEY")
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BLOB_CONNECTION_STRING = os.getenv("BLOB_CONNECTION_STRING")
BLOB_CONTAINER_NAME = os.getenv("BLOB_CONTAINER_NAME")
INDEX_NAME = "items-index"
BATCH_SIZE = 500  # Azure AI Search limit is 1000 docs per batch

# Initialize Blob Service Client
blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(BLOB_CONTAINER_NAME)

# Function to generate OpenAI embeddings
def generate_embedding(text):
    try:
        response = openai.Embedding.create(
            input=text,
            model="text-embedding-ada-002"
        )
        return response["data"][0]["embedding"]
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return [0.0] * 1536  # Fallback to zero vector if embedding fails

# Function to read and process JSON files from Blob Storage
def process_json_files():
    data_to_index = []
    
    # Iterate over each JSON file in the Blob container
    for blob in container_client.list_blobs():
        blob_client = container_client.get_blob_client(blob.name)
        blob_data = blob_client.download_blob().readall()
        json_data = json.loads(blob_data)

        # Ensure JSON is a list of records
        if isinstance(json_data, dict):  
            json_data = [json_data]

        # Process each row from the JSON
        for row in json_data:
            item = {
                "@search.action": "mergeOrUpload",
                "ITEMNUM": str(row.get("ITEMNUM", "")),
                "DESCRIPTION": row.get("DESCRIPTION", ""),
                "vector_embedding": generate_embedding(row.get("DESCRIPTION", "")),  
                "ITEMID": row.get("ITEMID", 0),
                "totalOnhand": row.get("totalOnhand", 0),
                "URL": row.get("URL", ""),
                "partition_id": row.get("partition_id", 0),

                # Process nested fields correctly
                "itemspec_array": [
                    {"ALNVALUE": spec.get("ALNVALUE", ""), "NUMVALUE": spec.get("NUMVALUE", 0)}
                    for spec in row.get("itemspec_array", [])
                ],
                "plusitemterm_array": [
                    {"TERMID": term.get("TERMID", "")} 
                    for term in row.get("plusitemterm_array", [])
                ],
                "invvendor_array": [
                    {
                        "VENDOR": vendor.get("VENDOR", ""),
                        "MANUFACTURER": vendor.get("MANUFACTURER", ""),
                        "MODELNUM": vendor.get("MODELNUM", ""),
                        "CATALOGCODE": vendor.get("CATALOGCODE", "")
                    }
                    for vendor in row.get("invvendor_array", [])
                ]
            }
            data_to_index.append(item)

            # Upload data in batches
            if len(data_to_index) >= BATCH_SIZE:
                upload_to_search(data_to_index)
                data_to_index = []

    # Upload remaining records
    if data_to_index:
        upload_to_search(data_to_index)

# Function to upload data to Azure AI Search
def upload_to_search(data):
    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_SEARCH_API_KEY
    }
    payload = {"value": data}
    response = requests.post(
        f"{AZURE_SEARCH_ENDPOINT}/indexes/{INDEX_NAME}/docs/index?api-version=2023-07-01",
        headers=headers,
        json=payload
    )
    print(response.json())  # Should return success response

# Run processing function
process_json_files()

import openai
import requests
import os
import json

# Azure AI Search credentials
AZURE_SEARCH_API_KEY = os.getenv("AZURE_SEARCH_API_KEY", "your_azure_search_api_key")
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT", "https://yoursearchservice.search.windows.net")
INDEX_NAME = "items-index"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_openai_api_key")

# Generate OpenAI embedding
def generate_embedding(text):
    try:
        response = openai.Embedding.create(input=text, model="text-embedding-ada-002")
        return response["data"][0]["embedding"]
    except Exception as e:
        print(f"OpenAI API Error: {e}")
        return [0.0] * 1536  # Fallback zero vector

# Search query
query = "stainless steel hex screw"
query_vector = generate_embedding(query)

# Request payload
payload = {
    "search": query,
    "vectorQueries": [
        {
            "kind": "vector",
            "field": "vector_embedding",
            "value": query_vector,
            "k": 5
        }
    ],
    "queryType": "semantic",
    "semanticConfiguration": "semantic-config",
    "searchMode": "all"
}

# Send request to Azure AI Search
headers = {"Content-Type": "application/json", "api-key": AZURE_SEARCH_API_KEY}
response = requests.post(f"{AZURE_SEARCH_ENDPOINT}/indexes/{INDEX_NAME}/docs/search?api-version=2023-07-01", headers=headers, json=payload)

# Print results
response_data = response.json()
if "value" in response_data:
    for i, result in enumerate(response_data["value"]):
        print(f"{i+1}. ITEM#: {result.get('ITEM#', 'N/A')}")
        print(f"   Description: {result.get('description', 'N/A')}")
        print(f"   Score: {result.get('@search.score', 'N/A')}\n")
else:
    print("No results found.")

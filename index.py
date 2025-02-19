import requests

AZURE_SEARCH_API_KEY = "your_azure_search_api_key"
AZURE_SEARCH_ENDPOINT = "https://yoursearchservice.search.windows.net"
INDEX_NAME = "items-index"

# Define index schema
index_schema = {
    "name": INDEX_NAME,
    "fields": [
        {"name": "ITEM#", "type": "Edm.String", "key": True, "filterable": True, "sortable": True, "facetable": True},
        {"name": "description", "type": "Edm.String", "searchable": True},
        {"name": "vector_embedding", "type": "Collection(Edm.Single)", "searchable": True, "vectorSearchDimensions": 1536, "vectorSearchAlgorithm": "hnsw"},
        {"name": "status", "type": "Edm.String", "filterable": True, "sortable": True, "facetable": True},
        {"name": "commodity", "type": "Edm.String", "filterable": True, "sortable": True, "facetable": True},
        {"name": "CurrentBalance", "type": "Edm.Int32", "sortable": True}
    ],
    "semantic": {
        "configurations": [
            {
                "name": "semantic-config",
                "prioritizedFields": {
                    "titleField": {"fieldName": "description"},
                    "contentFields": [{"fieldName": "description"}]
                }
            }
        ]
    },
    "vectorSearch": {
        "algorithms": [
            {
                "name": "hnsw",
                "kind": "hnsw",
                "parameters": {
                    "m": 4,
                    "efConstruction": 400
                }
            }
        ]
    }
}

# Create index
headers = {
    "Content-Type": "application/json",
    "api-key": AZURE_SEARCH_API_KEY
}
response = requests.put(f"{AZURE_SEARCH_ENDPOINT}/indexes/{INDEX_NAME}?api-version=2023-07-01", headers=headers, json=index_schema)

print(response.json())  # Should return success response

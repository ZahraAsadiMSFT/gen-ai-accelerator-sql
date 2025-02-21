import requests

AZURE_SEARCH_API_KEY = "your_azure_search_api_key"
AZURE_SEARCH_ENDPOINT = "https://yoursearchservice.search.windows.net"
INDEX_NAME = "items-index"

# Define index schema
index_schema = {
    "name": INDEX_NAME,
    "fields": [
        {"name": "ITEMNUM", "type": "Edm.String", "key": True, "filterable": True, "sortable": True, "facetable": True},
        {"name": "DESCRIPTION", "type": "Edm.String", "searchable": True},
        {"name": "vector_embedding", "type": "Collection(Edm.Single)", "searchable": True, "vectorSearchDimensions": 1536, "vectorSearchAlgorithm": "hnsw"},
        {"name": "ITEMID", "type": "Edm.Int32", "sortable": True, "filterable": True},
        {"name": "totalOnhand", "type": "Edm.Int32", "sortable": True, "filterable": True},
        {"name": "URL", "type": "Edm.String", "searchable": True},
        {"name": "partition_id", "type": "Edm.Int32", "filterable": True, "sortable": True},

        # itemspec_array - Stores multiple specifications for an item
        {
            "name": "itemspec_array",
            "type": "Collection(Edm.ComplexType)",
            "fields": [
                {"name": "ALNVALUE", "type": "Edm.String", "searchable": True},
                {"name": "NUMVALUE", "type": "Edm.Int32", "filterable": True}  
            ]
        },

        # plusitemterm_array - Stores term IDs related to the item
        {
            "name": "plusitemterm_array",
            "type": "Collection(Edm.ComplexType)",
            "fields": [
                {"name": "TERMID", "type": "Edm.String", "searchable": True}
            ]
        },

        # invvendor_array - Stores vendor details for the item
        {
            "name": "invvendor_array",
            "type": "Collection(Edm.ComplexType)",
            "fields": [
                {"name": "VENDOR", "type": "Edm.String", "filterable": True, "facetable": True},
                {"name": "MANUFACTURER", "type": "Edm.String", "filterable": True, "facetable": True},
                {"name": "MODELNUM", "type": "Edm.String", "searchable": True},
                {"name": "CATALOGCODE", "type": "Edm.String", "searchable": True}
            ]
        }
    ],
    "semantic": {
        "configurations": [
            {
                "name": "semantic-config",
                "prioritizedFields": {
                    "titleField": {"fieldName": "DESCRIPTION"},
                    "contentFields": [{"fieldName": "DESCRIPTION"}]
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
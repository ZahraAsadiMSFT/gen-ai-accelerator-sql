# Azure AI Search Indexing with Azure SQL and OpenAI Embeddings

## Overview
This project automates the process of indexing data from an Azure SQL database into Azure AI Search. It ensures that only changed rows (new or updated) are indexed and that deleted rows are removed. The project also leverages OpenAI embeddings for semantic search on the description field.

## Explaining Key Field Properties
Each field in Azure AI Search has different capabilities. Here’s what they mean:

| Property      | What It Does? |
|--------------|--------------|
| **key**      | Uniquely identifies each document. (Only one field can be True—in this case, `ITEM#`.) |
| **searchable** | Allows full-text search (used for text-based fields like `description`). |
| **filterable** | Allows filtering in queries (used for structured fields like `status`, `commodity`). |
| **sortable** | Allows sorting query results (useful for numbers, dates, or categories). |
| **facetable** | Allows aggregation and filtering (e.g., count how many items have a specific `commodity`). |

## Project Files

### **1. Azure Function Code (`__init__.py`)**
This script:
- Connects to Azure SQL.
- Fetches only **new or updated records** (last 24 hours).
- Fetches **deleted records** and removes them from Azure AI Search.
- Generates **OpenAI embeddings** for `description`.
- Uploads data to **Azure AI Search** in **batches** to optimize performance.

### **2. Function Configuration (`function.json`)**
Defines the **Azure Timer Trigger**, which runs the function **once per day**:
```json
{
    "scriptFile": "__init__.py",
    "bindings": [
        {
            "name": "mytimer",
            "type": "timerTrigger",
            "direction": "in",
            "schedule": "0 0 * * *"
        }
    ]
}
```

### **3. Environment Variables (Stored in Azure Function App Configuration)**
| Variable | Description |
|----------|-------------|
| `AZURE_SEARCH_API_KEY` | API key for Azure AI Search. |
| `AZURE_SEARCH_ENDPOINT` | Endpoint for Azure AI Search service. |
| `OPENAI_API_KEY` | API key for OpenAI embeddings. |
| `SQL_SERVER` | Azure SQL Server name. |
| `SQL_DATABASE` | Azure SQL Database name. |
| `SQL_USERNAME` | Azure SQL Database username. |
| `SQL_PASSWORD` | Azure SQL Database password. |

## How to Test the Index

### Test Full-Text Search (Keyword Search on ITEM#)**
```json
{
  "search": "3260",
  "queryType": "full",
  "searchMode": "any"
}
```
Test Semantic Search (Semantic Search on description)**
Expected behavior after running test-semantic.py: This should return the **exact match** for `ITEM# = 3260`.


Expected behavior: This should return the **top 5 most relevant matches** based on vector similarity.

## Deployment Steps
1. **Deploy the Azure Function:**
```bash
func azure functionapp publish my_function_app
```
2. **Configure Environment Variables** in **Azure Portal > Function App > Configuration**.
3. **Verify Logs** in **Azure Portal > Monitor > Logs**.
4. **Run the Function Locally** for Testing:
```bash
func start
```

## Conclusion
This setup ensures that the **Azure AI Search index stays updated automatically** with new, modified, and deleted records from Azure SQL, while leveraging **OpenAI embeddings** for enhanced search capabilities.


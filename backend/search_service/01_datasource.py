from azure.search.documents.indexes import SearchIndexerClient
from azure.search.documents.indexes.models import (
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection
)
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
import os

load_dotenv()

credential = DefaultAzureCredential()

AZURE_SEARCH_SERVICE = os.getenv("AZURE_SEARCH_SERVICE")
AZURE_STORAGE_CONNECTION = os.getenv("AZURE_STORAGE_CONNECTION")

# Create a data source 
indexer_client = SearchIndexerClient(endpoint=AZURE_SEARCH_SERVICE, credential=credential)
container = SearchIndexerDataContainer(name="nasa-data-container")
data_source_connection = SearchIndexerDataSourceConnection(
    name="py-rag-tutorial-ds",
    type="azureblob",
    connection_string=AZURE_STORAGE_CONNECTION,
    container=container
)
data_source = indexer_client.create_or_update_data_source_connection(data_source_connection)

print(f"Data source '{data_source.name}' created or updated")
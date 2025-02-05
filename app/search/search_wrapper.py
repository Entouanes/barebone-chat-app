"""
Module for defining the Pipeline class that orchestrates the creation of the search index,
data source, skillset, and indexer using Azure Search services. This enables both vector 
and semantic search functionalities.
"""
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizableTextQuery
from azure.identity import DefaultAzureCredential
from utils import create_data_source, create_search_index, create_skillset, create_indexer
from dotenv import load_dotenv
import os


class SearchWrapper:
    def __init__(
        self,
        index_name="default-idx",
        skillset_name="default-ss",
        indexer_name="default-idxr",
        container_name="default-full",
        data_source_name="default-ds"
    ):
        """
        Initializes the Pipeline with environment variables and configuration settings.
        Loads variables from the .env file.
        """
        load_dotenv()
        self.AZURE_OPENAI_ENDPOINT=os.getenv("AZURE_OPENAI_ENDPOINT")
        self.AZURE_OPENAI_API_KEY=os.getenv("AZURE_OPENAI_API_KEY")
        self.AZURE_SEARCH_SERVICE=os.getenv("AZURE_SEARCH_SERVICE")
        self.AZURE_STORAGE_CONNECTION=os.getenv("AZURE_STORAGE_CONNECTION")
        self.AZURE_AI_COGNITIVE_SERVICES_KEY=os.getenv("AZURE_AI_COGNITIVE_SERVICES_KEY")
        self.AZURE_AI_COGNITIVE_SERVICES_ACCOUNT=os.getenv("AZURE_AI_COGNITIVE_SERVICES_ACCOUNT")
        self.index_name=index_name
        self.data_source_name=data_source_name
        self.skillset_name=skillset_name
        self.indexer_name=indexer_name
        self.container_name=container_name
        self.credential = DefaultAzureCredential()
        self.search_client=SearchClient(endpoint=self.AZURE_SEARCH_SERVICE, index_name=self.index_name, credential=self.credential)

    def search(self, query: str):
        """
        Connects to the Azure AI search service using default environment variables,
        executes the provided query, and returns the top 5 results.
        """
        vector_query = VectorizableTextQuery(
            text=query, 
            k_nearest_neighbors=50, 
            fields="text_vector"
        )

        results = self.search_client.search(
            search_text=query,
            vector_queries=[vector_query],
            select=["title", "chunk", "locations"],
            semantic_configuration_name='my-semantic-config',
            top=5,
            query_type='', 
        )

        return results

    def run_config_pipeline(self):
        """
        Executes the pipeline to set up the entire Azure Search environment.
        Sequentially creates the data source, search index, skillset, and indexer.
        """
        # Orchestrate pipeline steps:
        data_source = create_data_source()
        create_search_index()
        create_skillset()
        create_indexer(data_source)      
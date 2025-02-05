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
        container_name="default-container",
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
        self.index_name=os.getenv("AZURE_SEARCH_INDEX_NAME") or index_name
        self.indexer_name=os.getenv("AZURE_SEARCH_INDEXER_NAME") or indexer_name
        self.data_source_name=os.getenv("AZURE_SEARCH_DATA_SOURCE") or data_source_name
        self.skillset_name=os.getenv("AZURE_SEARCH_SKILLSET_NAME") or skillset_name
        self.container_name=os.getenv("AZURE_STORAGE_CONTAINER_NAME") or container_name
        self.credential=DefaultAzureCredential()
        self.search_client=SearchClient(endpoint=self.AZURE_SEARCH_SERVICE, index_name=self.index_name, credential=self.credential)

    def search(self, query: str):
        """
        Connects to the Azure AI search service using default environment variables,
        executes the provided query, and returns the top 5 results.
        """

        results = self.search_client.search(
            search_text=query,
            semantic_configuration_name='my-semantic-config',
            top=5,
        )

        return results

    def run_config_pipeline(self):
        """
        Executes the pipeline to set up the entire Azure Search environment.
        Sequentially creates the data source, search index, skillset, and indexer.
        """
        # Orchestrate pipeline steps:
        data_source = create_data_source(
            self.AZURE_SEARCH_SERVICE,
            self.credential,
            self.container_name,
            self.data_source_name,
            self.AZURE_STORAGE_CONNECTION
        )
        create_search_index(
            self.AZURE_SEARCH_SERVICE,
            self.credential,
            self.index_name,
            self.AZURE_OPENAI_ENDPOINT
        )
        create_skillset(
            azure_search_service=self.AZURE_SEARCH_SERVICE,
            credential=self.credential,
            index_name=self.index_name,
            skillset_name=self.skillset_name,
            azure_openai_endpoint=self.AZURE_OPENAI_ENDPOINT,
            azure_ai_cognitive_services_key=self.AZURE_AI_COGNITIVE_SERVICES_KEY
        )
        create_indexer(
            azure_search_service=self.AZURE_SEARCH_SERVICE,
            credential=self.credential,
            indexer_name=self.indexer_name,
            skillset_name=self.skillset_name,
            index_name=self.index_name,
            data_source=data_source
        )
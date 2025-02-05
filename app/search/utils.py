from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes import SearchIndexerClient
from azure.search.documents.indexes.models import (
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    AzureOpenAIVectorizer,
    AzureOpenAIVectorizerParameters,
    SearchIndex,
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection,
    SplitSkill,
    InputFieldMappingEntry,
    OutputFieldMappingEntry,
    AzureOpenAIEmbeddingSkill,
    EntityRecognitionSkill,
    SearchIndexerIndexProjection,
    SearchIndexerIndexProjectionSelector,
    SearchIndexerIndexProjectionsParameters,
    IndexProjectionMode,
    SearchIndexerSkillset,
    CognitiveServicesAccountKey,
    SearchIndexer,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
)

def create_search_index(self):
    """
    Creates a search index with specified fields, vector search, and semantic search configurations.
    Returns:
        SearchIndex: The created search index.
    """
    # Set up SearchIndexClient and define index fields
    index_client = SearchIndexClient(endpoint=self.AZURE_SEARCH_SERVICE, credential=self.credential)  
    fields = [
        SearchField(name="parent_id", type=SearchFieldDataType.String),  
        SearchField(name="title", type=SearchFieldDataType.String),
        SearchField(name="locations", type=SearchFieldDataType.Collection(SearchFieldDataType.String), filterable=True),
        SearchField(name="color", type=SearchFieldDataType.String, key=True, sortable=True, filterable=True, facetable=True, analyzer_name="keyword"),  
        SearchField(name="description", type=SearchFieldDataType.String, sortable=False, filterable=False, facetable=False),  
        SearchField(name="text_vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), vector_search_dimensions=1024, vector_search_profile_name="myHnswProfile")
    ]  
    
    # Define semantic configuration for enhanced search ranking
    semantic_config = SemanticConfiguration(  
        name="my-semantic-config",  
        prioritized_fields=SemanticPrioritizedFields(  
            content_fields=[SemanticField(field_name="chunk")]  
        ),  
    )  
    # Configure semantic search settings
    semantic_search = SemanticSearch(configurations=[semantic_config])
    # Configure vector search using Azure OpenAI
    vector_search = VectorSearch(  
        algorithms=[  
            HnswAlgorithmConfiguration(name="myHnsw"),
        ],  
        profiles=[  
            VectorSearchProfile(  
                name="myHnswProfile",  
                algorithm_configuration_name="myHnsw",  
                vectorizer_name="myOpenAI",  
            )
        ],  
        vectorizers=[  
            AzureOpenAIVectorizer(  
                vectorizer_name="myOpenAI",  
                kind="azureOpenAI",  
                parameters=AzureOpenAIVectorizerParameters(  
                    resource_url=self.AZURE_OPENAI_ENDPOINT,  
                    deployment_name="text-embedding-3-large",
                    model_name="text-embedding-3-large"
                ),
            ),  
        ], 
    )  
    
    # Create the search index with both vector and semantic configurations
    index = SearchIndex(name=self.index_name, fields=fields, vector_search=vector_search, semantic_search=semantic_search)    
    result = index_client.create_or_update_index(index)  
    print(f"{result.name} created")  
    return result
def create_data_source(self):
    """
    Creates or updates a data source connection for the search indexer.
    Returns:
        SearchIndexerDataSourceConnection: The created or updated data source connection.
    """
    # Initialize SearchIndexerClient and define the data container
    indexer_client = SearchIndexerClient(endpoint=self.AZURE_SEARCH_SERVICE, credential=self.credential)
    container = SearchIndexerDataContainer(name="nasa-data-container")
    data_source_connection = SearchIndexerDataSourceConnection(
        name=self.data_source_name,
        type="azureblob",
        connection_string=self.AZURE_STORAGE_CONNECTION,
        container=container
    )
    data_source = indexer_client.create_or_update_data_source_connection(data_source_connection)
    print(f"Data source '{data_source.name}' created or updated")
    return data_source
def create_skillset(self):
    """
    Creates a skillset with specified skills and index projections for the search indexer.
    Returns:
        SearchIndexerSkillset: The created skillset.
    """
    # Define skills for document splitting, embedding, and entity recognition
    split_skill = SplitSkill(  
        description="Split skill to chunk documents",  
        text_split_mode="pages",  
        context="/document",  
        maximum_page_length=2000,  
        page_overlap_length=500,  
        inputs=[  
            InputFieldMappingEntry(name="text", source="/document/content"),  
        ],  
        outputs=[  
            OutputFieldMappingEntry(name="textItems", target_name="pages")  
        ],  
    )  
    
    embedding_skill = AzureOpenAIEmbeddingSkill(  
        description="Skill to generate embeddings via Azure OpenAI",  
        context="/document/pages/*",  
        resource_url=self.AZURE_OPENAI_ENDPOINT,  
        deployment_name="text-embedding-3-large",  
        model_name="text-embedding-3-large",
        dimensions=1024,
        inputs=[  
            InputFieldMappingEntry(name="text", source="/document/pages/*"),  
        ],  
        outputs=[  
            OutputFieldMappingEntry(name="embedding", target_name="text_vector")  
        ]
    )
    entity_skill = EntityRecognitionSkill(
        description="Skill to recognize entities in text",
        context="/document/pages/*",
        categories=["Location"],
        default_language_code="en",
        inputs=[
            InputFieldMappingEntry(name="text", source="/document/pages/*")
        ],
        outputs=[
            OutputFieldMappingEntry(name="locations", target_name="locations")
        ],
    )
    
    # Define index projection to map document fields to index fields
    index_projections = SearchIndexerIndexProjection(  
        selectors=[  
            SearchIndexerIndexProjectionSelector(  
                target_index_name=self.index_name,  
                parent_key_field_name="parent_id",  
                source_context="/document/pages/*",  
                mappings=[  
                    InputFieldMappingEntry(name="chunk", source="/document/pages/*"),  
                    InputFieldMappingEntry(name="text_vector", source="/document/pages/*/text_vector"),
                    InputFieldMappingEntry(name="locations", source="/document/pages/*/locations"),  
                    InputFieldMappingEntry(name="title", source="/document/metadata_storage_name"),  
                ],  
            ),  
        ],  
        parameters=SearchIndexerIndexProjectionsParameters(  
            projection_mode=IndexProjectionMode.SKIP_INDEXING_PARENT_DOCUMENTS  
        ),  
    ) 
    # Configure cognitive services for the skillset
    cognitive_services_account = CognitiveServicesAccountKey(key=self.AZURE_AI_COGNITIVE_SERVICES_KEY)
    skills = [split_skill, embedding_skill, entity_skill]
    # Create the overall skillset configuration
    skillset = SearchIndexerSkillset(  
        name=self.skillset_name,  
        description="Skillset to chunk documents and generating embeddings",  
        skills=skills,  
        index_projection=index_projections,
        cognitive_services_account=cognitive_services_account,
    )
    
    # Apply the skillset configuration using SearchIndexerClient
    client = SearchIndexerClient(endpoint=self.AZURE_SEARCH_SERVICE, credential=self.credential)  
    client.create_or_update_skillset(skillset)  
    print(f"{skillset.name} created")  
    return skillset
def create_indexer(self, data_source: SearchIndexerDataSourceConnection):
    """
    Creates and runs an indexer to index documents and generate embeddings.
    Args:
        data_source (SearchIndexerDataSourceConnection): The data source connection to be used by the indexer.
    Returns:
        SearchIndexer: The created and running indexer.
    """
    # Define an indexer with the specified skillset and target index.
    indexer_parameters = None
    indexer = SearchIndexer(  
        name=self.indexer_name,  
        description="Indexer to index documents and generate embeddings",  
        skillset_name=self.skillset_name,  
        target_index_name=self.index_name,  
        data_source_name=data_source.name,
        parameters=indexer_parameters
    )  
    # Apply and run the indexer
    indexer_client = SearchIndexerClient(endpoint=self.AZURE_SEARCH_SERVICE, credential=self.credential)  
    indexer_result = indexer_client.create_or_update_indexer(indexer)  
    print(f' {self.indexer_name} is created and running. Give the indexer a few minutes before running a query.')  
    return indexer_result
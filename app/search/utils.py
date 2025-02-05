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
    #SplitSkill,
    #InputFieldMappingEntry,
    #OutputFieldMappingEntry,
    #AzureOpenAIEmbeddingSkill,
    #EntityRecognitionSkill,
    #SearchIndexerIndexProjection,
    #SearchIndexerIndexProjectionSelector,
    #SearchIndexerIndexProjectionsParameters,
    #IndexProjectionMode,
    #SearchIndexerSkillset,
    #CognitiveServicesAccountKey,
    SearchIndexer,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
    IndexingParameters,
    IndexingParametersConfiguration,
    IndexingSchedule
)

def create_search_index(azure_search_service, credential, index_name, azure_openai_endpoint):
    """
    Creates a search index with specified fields, vector search, and semantic search configurations.
    Returns:
        SearchIndex: The created search index.
    """
    # Set up SearchIndexClient and define index fields
    index_client = SearchIndexClient(endpoint=azure_search_service, credential=credential)  
    
    fields = [
        SearchField(name="programID", type=SearchFieldDataType.String, key=True, searchable=True, filterable=True, facetable=True, sortable=True),
        SearchField(name="orchestra", type=SearchFieldDataType.String, searchable=True, filterable=True, facetable=True, sortable=True),
        SearchField(name="season", type=SearchFieldDataType.String, searchable=True, filterable=True, facetable=True, sortable=True),
        SearchField(
            name="concerts",
            type=SearchFieldDataType.Collection(SearchFieldDataType.ComplexType),
            fields=[
                SearchField(name="eventType", type=SearchFieldDataType.String, searchable=True, filterable=False, sortable=False, facetable=False),
                SearchField(name="Location", type=SearchFieldDataType.String, searchable=True, filterable=True, sortable=False, facetable=True),
                SearchField(name="Venue", type=SearchFieldDataType.String, searchable=True, filterable=True, sortable=False, facetable=True),
                SearchField(name="Date", type=SearchFieldDataType.String, searchable=False, filterable=True, sortable=False, facetable=True),
                SearchField(name="Time", type=SearchFieldDataType.String, searchable=False, filterable=True, sortable=False, facetable=True),
            ]
        ),
        SearchField(
            name="works",
            type=SearchFieldDataType.Collection(SearchFieldDataType.ComplexType),
            fields=[
                SearchField(name="ID", type=SearchFieldDataType.String, searchable=True, filterable=False, sortable=False, facetable=False),
                SearchField(name="composerName", type=SearchFieldDataType.String, searchable=True, filterable=True, sortable=False, facetable=True),
                SearchField(name="workTitle", type=SearchFieldDataType.String, searchable=True, filterable=True, sortable=False, facetable=True),
                SearchField(name="conductorName", type=SearchFieldDataType.String, searchable=True, filterable=True, sortable=False, facetable=True),
                SearchField(name="soloists", type=SearchFieldDataType.Collection(SearchFieldDataType.String), searchable=True, filterable=True, sortable=False, facetable=True),
            ]
        )
    ]
    
    # Define semantic configuration for enhanced search ranking
    semantic_config = SemanticConfiguration(  
        name="my-semantic-config",  
        prioritized_fields=SemanticPrioritizedFields(  
            title_field=SemanticField(field_name="orchestra"),
            content_fields=[SemanticField(field_name="works")]
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
                    resource_url=azure_openai_endpoint,  
                    deployment_name="text-embedding-3-large",
                    model_name="text-embedding-3-large"
                ),
            ),  
        ], 
    )  
    
    # Create the search index with both vector and semantic configurations
    index = SearchIndex(name=index_name, fields=fields, vector_search=vector_search, semantic_search=semantic_search)    
    result = index_client.create_or_update_index(index)  
    print(f"{result.name} created")  
    return result

def create_data_source(azure_search_service, credential, container_name, data_source_name, azure_storage_connection):
    """
    Creates or updates a data source connection for the search indexer.
    Returns:
        SearchIndexerDataSourceConnection: The created or updated data source connection.
    """
    # Initialize SearchIndexerClient and define the data container
    indexer_client = SearchIndexerClient(endpoint=azure_search_service, credential=credential)
    container = SearchIndexerDataContainer(name=container_name)
    data_source_connection = SearchIndexerDataSourceConnection(
        name=data_source_name,
        type="azureblob",
        connection_string=azure_storage_connection,
        container=container
    )
    data_source = indexer_client.create_or_update_data_source_connection(data_source_connection)
    print(f"Data source '{data_source.name}' created or updated")
    return data_source

def create_skillset(azure_search_service, credential, index_name, skillset_name, azure_openai_endpoint, azure_ai_cognitive_services_key):
    """
    Creates a skillset with specified skills and index projections for the search indexer.
    Returns:
        SearchIndexerSkillset: The created skillset.
    """

    # TODO: Uncomment the following code to create a skillset with skills and index projections

    # Define skills for document splitting, embedding, and entity recognition
    #split_skill = SplitSkill(  
    #    description="Split skill to chunk documents",  
    #    text_split_mode="pages",  
    #    context="/document",  
    #    maximum_page_length=2000,  
    #    page_overlap_length=500,  
    #    inputs=[  
    #        InputFieldMappingEntry(name="text", source="/document/content"),  
    #    ],  
    #    outputs=[  
    #        OutputFieldMappingEntry(name="textItems", target_name="pages")  
    #    ],  
    #)  
    #
    #embedding_skill = AzureOpenAIEmbeddingSkill(  
    #    description="Skill to generate embeddings via Azure OpenAI",  
    #    context="/document/pages/*",  
    #    resource_url=azure_openai_endpoint,  
    #    deployment_name="text-embedding-3-large",  
    #    model_name="text-embedding-3-large",
    #    dimensions=1024,
    #    inputs=[  
    #        InputFieldMappingEntry(name="text", source="/document/pages/*"),  
    #    ],  
    #    outputs=[  
    #        OutputFieldMappingEntry(name="embedding", target_name="text_vector")  
    #    ]
    #)
    #entity_skill = EntityRecognitionSkill(
    #    description="Skill to recognize entities in text",
    #    context="/document/pages/*",
    #    categories=["Location"],
    #    default_language_code="en",
    #    inputs=[
    #        InputFieldMappingEntry(name="text", source="/document/pages/*")
    #    ],
    #    outputs=[
    #        OutputFieldMappingEntry(name="locations", target_name="locations")
    #    ],
    #)
    #
    ## Define index projection to map document fields to index fields
    #index_projections = SearchIndexerIndexProjection(  
    #    selectors=[  
    #        SearchIndexerIndexProjectionSelector(  
    #            target_index_name=index_name,  
    #            parent_key_field_name="parent_id",  
    #            source_context="/document/pages/*",  
    #            mappings=[  
    #                InputFieldMappingEntry(name="chunk", source="/document/pages/*"),  
    #                InputFieldMappingEntry(name="text_vector", source="/document/pages/*/text_vector"),
    #                InputFieldMappingEntry(name="locations", source="/document/pages/*/locations"),  
    #                InputFieldMappingEntry(name="title", source="/document/metadata_storage_name"),  
    #            ],  
    #        ),  
    #    ],  
    #    parameters=SearchIndexerIndexProjectionsParameters(  
    #        projection_mode=IndexProjectionMode.SKIP_INDEXING_PARENT_DOCUMENTS  
    #    ),  
    #) 
    ## Configure cognitive services for the skillset
    #cognitive_services_account = CognitiveServicesAccountKey(key=azure_ai_cognitive_services_key)
    #skills = [split_skill, embedding_skill, entity_skill]
    ## Create the overall skillset configuration
    #skillset = SearchIndexerSkillset(  
    #    name=skillset_name,  
    #    description="Skillset to chunk documents and generating embeddings",  
    #    skills=skills,  
    #    index_projection=index_projections,
    #    cognitive_services_account=cognitive_services_account,
    #)
    #
    ## Apply the skillset configuration using SearchIndexerClient
    #client = SearchIndexerClient(endpoint=azure_search_service, credential=credential)  
    #client.create_or_update_skillset(skillset)  
    #print(f"{skillset.name} created")  
    #return skillset
    pass

def create_indexer(azure_search_service, credential, indexer_name, skillset_name, index_name, data_source):
    """
    Creates and runs an indexer to index documents and generate embeddings.
    Args:
        data_source (SearchIndexerDataSourceConnection): The data source connection to be used by the indexer.
    Returns:
        SearchIndexer: The created and running indexer.
    """
    # Define an indexer with the specified skillset and target index.
    indexer_parameters = IndexingParameters(
        configuration=IndexingParametersConfiguration(
            parsing_mode="json",
            document_root="/programs",
        )
    )
    indexer = SearchIndexer(  
        name=indexer_name,  
        description="Indexer to index documents and generate embeddings",  
        skillset_name=skillset_name,  
        target_index_name=index_name,  
        data_source_name=data_source.name,
        parameters=indexer_parameters,
        schedule=IndexingSchedule(interval="PT2H", max_failed_items=10)

    )  
    # Apply and run the indexer
    indexer_client = SearchIndexerClient(endpoint=azure_search_service, credential=credential)  
    indexer_result = indexer_client.create_or_update_indexer(indexer)  
    print(f' {indexer_name} is created and running. Give the indexer a few minutes before running a query.')  
    return indexer_result
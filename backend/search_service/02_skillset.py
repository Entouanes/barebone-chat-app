from azure.search.documents.indexes.models import (
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
    CognitiveServicesAccountKey
)

from dotenv import load_dotenv
from azure.search.documents.indexes import SearchIndexerClient
from azure.identity import DefaultAzureCredential
import os

load_dotenv()

credential = DefaultAzureCredential()

AZURE_SEARCH_SERVICE = os.getenv("AZURE_SEARCH_SERVICE")
AZURE_OPENAI_ACCOUNT = os.getenv("AZURE_OPENAI_ACCOUNT")
AZURE_AI_MULTISERVICE_KEY = os.getenv("AZURE_AI_MULTISERVICE_KEY")
index_name = "py-rag-tutorial-idx"

# Create a skillset  
skillset_name = "py-rag-tutorial-ss"

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
    resource_url=AZURE_OPENAI_ACCOUNT,  
    deployment_name="text-embedding-3-large",  
    model_name="text-embedding-3-large",
    dimensions=1024,
    inputs=[  
        InputFieldMappingEntry(name="text", source="/document/pages/*"),  
    ],  
    outputs=[  
        OutputFieldMappingEntry(name="embedding", target_name="text_vector")  
    ],  
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
    ]
)
  
index_projections = SearchIndexerIndexProjection(  
    selectors=[  
        SearchIndexerIndexProjectionSelector(  
            target_index_name=index_name,  
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

cognitive_services_account = CognitiveServicesAccountKey(key=AZURE_AI_MULTISERVICE_KEY)

skills = [split_skill, embedding_skill, entity_skill]

skillset = SearchIndexerSkillset(  
    name=skillset_name,  
    description="Skillset to chunk documents and generating embeddings",  
    skills=skills,  
    index_projection=index_projections,
    cognitive_services_account=cognitive_services_account
)
  
client = SearchIndexerClient(endpoint=AZURE_SEARCH_SERVICE, credential=credential)  
client.create_or_update_skillset(skillset)  
print(f"{skillset.name} created")  
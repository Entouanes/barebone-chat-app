# Chat component for the barebone chat app using Azure OpenAI and Streamlit
from openai import AzureOpenAI  # Import Azure OpenAI client
import streamlit as st       # Import Streamlit for UI
from search.search_wrapper import SearchWrapper  # Import search service wrapper

# Extract API configuration from Streamlit secrets
api_key = st.secrets["AZURE_OPENAI_API_KEY"]
api_version = st.secrets["AZURE_OPENAI_API_VERSION"]
api_endpoint = st.secrets["AZURE_OPENAI_ENDPOINT"]
model = st.secrets["AZURE_OPENAI_MODEL"]

# Set up the sidebar with logo and about section
with st.sidebar:
    st.image("static/logo.png", width=100)  # Display logo
    st.title("About")
    st.write(
        f"""
        This is a simple chatbot built using OpenAI's {model}. 
        It is powered by Azure's OpenAI API.
        """
    )

# Main app title
st.title("RoboChat")

# Initialize Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint=api_endpoint, 
    api_key=api_key,
    api_version=api_version,
)

# Define the prompt template for grounded responses using sources
GROUNDED_PROMPT="""
You are an AI assistant that helps users learn from the information found in the source material.
Answer the query using only the sources provided below.
The sources are in JSON format. You can use the information in the sources to answer the query.
Use bullets if the answer has multiple points.
If the answer is longer than 3 sentences, provide a summary.
Answer ONLY with the facts listed in the list of sources below. Cite your source when you answer the question
If there isn't enough information below, say you don't know.
Do not generate answers that don't use the sources below.
Query: {query}
Sources:\n{sources}
"""

# Initialize search service
search_service = SearchWrapper()

# Helper function to format sources for the prompt
def sources_formatted(sources):
    return list(sources)

# Initialize session messages if not present
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages in the chat interface
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Get user input and process the chat message
if prompt := st.chat_input("What is up?"):
    # Append user message to session state
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Search for relevant sources based on user query
    source = search_service.search(prompt)
    
    # Display user message in the chat UI
    with st.chat_message("human"):
        st.markdown(prompt)
    
    # Process and display streaming response from the assistant
    with st.chat_message("assistant"):
        # Create request with formatted grounded prompt including search sources
        rag_context = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user", 
                    "content": GROUNDED_PROMPT.format(
                        query=st.session_state.messages[-1], 
                        sources=sources_formatted(search_service.search(st.session_state.messages[-1]))
                    )
                }
            ],
            stream=True,
        )
        # Stream and display the assistant's response
        response = st.write_stream(rag_context)
    
    # Append assistant response to session state
    st.session_state.messages.append({"role": "assistant", "content": response})
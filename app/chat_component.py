from openai import AzureOpenAI
import streamlit as st
from search_config import SearchConfig

api_key = st.secrets["AZURE_OPENAI_API_KEY"]
api_version = st.secrets["AZURE_OPENAI_API_VERSION"]
api_endpoint = st.secrets["AZURE_OPENAI_ENDPOINT"]
model = st.secrets["AZURE_OPENAI_MODEL"]


with st.sidebar:
    st.image("static/logo.png", width=100)

    st.title("About")
    st.write(
        f"""
        This is a simple chatbot built using OpenAI's {model}. 
        It is powered by Azure's OpenAI API.
        """
    )
st.title("RoboChat")

client = AzureOpenAI(
    azure_endpoint=api_endpoint, 
    api_key=api_key,
    api_version=api_version,
    )

# Provide instructions to the model
GROUNDED_PROMPT="""
You are an AI assistant that helps users learn from the information found in the source material.
Answer the query using only the sources provided below.
Use bullets if the answer has multiple points.
If the answer is longer than 3 sentences, provide a summary.
Answer ONLY with the facts listed in the list of sources below. Cite your source when you answer the question
If there isn't enough information below, say you don't know.
Do not generate answers that don't use the sources below.
Query: {query}
Sources:\n{sources}
"""

ai_search = SearchConfig()

def sources_formatted(sources):
    return "=================\n".join([f'TITLE: {document["title"]}, CONTENT: {document["chunk"]}, LOCATIONS: {document["locations"]}' for document in sources])

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    source = ai_search.search(prompt)
    with st.chat_message("human"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        rag_context = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user", 
                    "content": GROUNDED_PROMPT.format(
                        query=st.session_state.messages[-1], 
                        sources=sources_formatted(ai_search.search(st.session_state.messages[-1]))
                    )
                }
            ],
            stream=True,
        )

        response = st.write_stream(rag_context)
    st.session_state.messages.append({"role": "assistant", "content": response})
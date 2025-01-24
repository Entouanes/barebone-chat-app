from openai import AzureOpenAI
import streamlit as st

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

print(st.secrets["AZURE_OPENAI_ENDPOINT"])

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("human"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=model,
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
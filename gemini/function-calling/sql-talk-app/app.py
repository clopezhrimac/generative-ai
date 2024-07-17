import time
import streamlit as st
from vertexai.generative_models import FunctionDeclaration, GenerativeModel, Part, Tool
from functions import permanence_func, permanence_model, query_api_func, call_cloud_run_api
import vertexai.preview.generative_models as generative_models
import numpy as np
from utils import upload_to_gcs
import os
import time
import random
# import google.generativeai as genai

# Credenciales de Google Cloud
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "dev.json"
BUCKET_NAME = "ue4_ndlk_nonprod_stg_gcs_iadev_artfsto"
SUBFOLDER = "generativeai-downloads/asesor ventas"

# Wrap the FunctionDeclaration in a Tool
api_tool = Tool(
    function_declarations=[permanence_func, query_api_func],
)

# model = GenerativeModel(
#     "gemini-1.5-pro-001",
#     generation_config={"temperature": 0},
#     tools=[api_tool],
# )

model = GenerativeModel(
    "gemini-1.5-flash-001",
    generation_config={"temperature": 0},
)

generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
}

safety_settings = {
    generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
}

st.set_page_config(
    page_title="TalentBot",
    page_icon="vertex-ai.png",
    layout="wide",
)

# Load custom CSS
# def load_css(file_name):
#     with open(file_name) as f:
#         st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# load_css("styles.css")

# header_html = """
# <div class="header">
#     <h2>Centro de Conocimiento</h2>
# </div>
# """
# st.markdown(header_html, unsafe_allow_html=True)

col1, col2 = st.columns([8, 1])
with col1:
    st.title("TalenBot")
with col2:
    st.image("vertex-ai.png")

st.subheader("Powered by Gemini")

# st.markdown(
#     "[Source Code](https://github.com/GoogleCloudPlatform/generative-ai/tree/main/gemini/function-calling/sql-talk-app/)   •   [Documentation](https://cloud.google.com/vertex-ai/docs/generative-ai/multimodal/function-calling)"
# )

with st.expander("Ejemplos de promt", expanded=True):
    st.write(
        """
        - Resume el CV.
        - Compara los CV en una tabla.
        - Dame el numero de DNI de <nombre>.
        - Que candidato domina mas lenguajes.
    """
    )

def submit():
    st.session_state.user_input_prompt = st.session_state.user_input
    st.session_state.user_input = ''

def initialize_session_state():
    # if "chat" not in st.session_state:
    #     st.session_state.chat = model.start_chat(history = [])
    if "messages" not in st.session_state:
        st.session_state.messages = []
    # flags para flujo de archivo adjunto
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []
        st.session_state.uploaded_files_uris = []
    if 'user_input_prompt' not in st.session_state: # This one is specifically use for clearing the user text input after they hit enter
        st.session_state.user_input_prompt = 'None'
    if "file_uploader_key" not in st.session_state:
        st.session_state["file_uploader_key"] = 0
    if 'model_processing' not in st.session_state:
        st.session_state.model_processing = False

def reset_session_state():
    st.session_state["file_uploader_key"] += 1
    st.session_state.uploaded_files = None
    st.session_state.uploaded_files_uris = []
    # st.rerun()
    print("********** HISTORY ***************")
    print(st.session_state.messages)


############################################# Main #############################################

# Initialize the session state variables
initialize_session_state()

chat = model.start_chat(history=[])

# rednderizar todo
for message in  st.session_state.messages:
    # print(f"history type element: {message}/{type(message)}")
    with st.chat_message(message["role"]):
        st.markdown(message["content"].replace("$", "\$"))  # noqa: W605
# inicializar promt
prompt = st.chat_input("Como te puedo ayudar?", disabled=st.session_state.model_processing)

# Crear file_uploader para múltiples archivos
with st.sidebar:
    uploaded_files = st.file_uploader("Elija archivos PDF", type="pdf", accept_multiple_files=True, key=st.session_state["file_uploader_key"])
    if uploaded_files != []:
        # Use to check if PDFs are uploaded
        st.session_state.uploaded_files = uploaded_files
        st.session_state.uploaded_files_uris = []

def debug(text=''):
    print(text)
    print(f'**messages in session_state: {st.session_state.messages}, len: {len(st.session_state.messages)}')
    print(f'**uploaded_files in session_state: {"uploaded_files" in st.session_state}')
    print(f'**session_state.uploaded_files: {st.session_state.uploaded_files}, len: {len(uploaded_files)}')
    for uri in st.session_state.uploaded_files_uris:
        print(f"     ->{uri}")

def create_multimodal_message(file_uris, promt=""):
    documents = [Part.from_uri(mime_type="application/pdf", uri=uri) for uri in file_uris]
    return documents + [promt]

def update_uris():
    st.session_state.uploaded_files_uris = []
    for uploaded_file in st.session_state.uploaded_files:
        destination_blob_name = f"{SUBFOLDER}/{uploaded_file.name}"
        file_uri = f"gs://{BUCKET_NAME}/{destination_blob_name}"
        st.session_state.uploaded_files_uris.append(file_uri)

debug("---->antes")
# Logica de archivo adjunto
# if "uploaded_files" in st.session_state and len(uploaded_files)>0:
#     st.session_state.uploaded_files = uploaded_files
#Chat
if prompt:
    # Renderizar input del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if prompt.isspace():
        # st.write("Input contains only spaces.")
        with st.chat_message("assistant"):
            st.markdown("Ingresa un texto no vacio por favor.")
    else:
        # Renderizar response modelo
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            prompt += """ Responde en español, por favor."""
            with st.spinner("Respondiendo..."):
                st.session_state.model_processing = True
                if st.session_state.uploaded_files and prompt:
                    new_pdfs = []
                    for uploaded_file in st.session_state.uploaded_files:
                        destination_blob_name = f"{SUBFOLDER}/{uploaded_file.name}"
                        if f"gs://{BUCKET_NAME}/{destination_blob_name}" not in st.session_state.uploaded_files_uris:
                            new_pdfs.append(uploaded_file)
                    for i, uploaded_file in enumerate(new_pdfs):
                        destination_blob_name = f"{SUBFOLDER}/{uploaded_file.name}"
                        print(f"Se subira el archivo: {uploaded_file.name} a STORAGE")
                        file_uri = upload_to_gcs(BUCKET_NAME, uploaded_file, destination_blob_name)
                        st.session_state.uploaded_files_uris.append(file_uri)
                        new_pdfs[i] = file_uri
                        print(f"uri: {file_uri}")
                    update_uris()
                    print(f"All uris: {st.session_state.uploaded_files_uris}")
                    response = chat.send_message(create_multimodal_message(st.session_state.uploaded_files_uris, prompt),
                                                            generation_config=generation_config, 
                                                            safety_settings=safety_settings, stream=True)
                else:
                    print(f"Se enviaria solo texto: <{prompt}>")
                    # Check if input contains only spaces
                    
                    response = chat.send_message(
                        prompt, 
                        generation_config=generation_config, 
                        safety_settings=safety_settings,
                        stream=True
                        )
                print(f'======> response: {response}')
                try:
                    full_response = ""
                    for chunk in response:
                        word_count = 0
                        random_int = random.randint(5,10)
                        # random_int = 5
                        for word in chunk.text:
                            full_response+=word
                            word_count+=1
                            if word_count == random_int:
                                time.sleep(0.05)
                                message_placeholder.markdown(full_response + "_")
                                word_count = 0
                                random_int = random.randint(5,10)
                    message_placeholder.markdown(full_response)
                except Exception as e:
                    st.exception(e)
            
            # full_response = response.candidates[0].content.parts[0].text
            print(f"full_response: {full_response}")
            st.session_state.model_processing = False
            # with message_placeholder.container():
            #     st.markdown(full_response.replace("$", "\$"))  # noqa: W605

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": full_response,
                }
            )

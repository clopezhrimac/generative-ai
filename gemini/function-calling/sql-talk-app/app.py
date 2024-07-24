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
from promts import *
import pandas as pd
from io import StringIO
from contextlib import redirect_stdout
# import google.generativeai as genai

# Credenciales de Google Cloud
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "dev.json"
BUCKET_NAME = "ue4_ndlk_nonprod_stg_gcs_iadev_artfsto"
SUBFOLDER = "generativeai-downloads/asesor ventas"

# Wrap the FunctionDeclaration in a Tool
api_tool = Tool(
    function_declarations=[permanence_func, query_api_func],
)
generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
}
model = GenerativeModel(
    "gemini-1.5-pro-001",
    generation_config=generation_config,
    system_instruction=SYSTEM_INSTRUCTION_V2
)

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

col1, col2 = st.columns([8, 1])
with col1:
    st.title("TalenBot")
with col2:
    st.image("vertex-ai.png")

st.subheader("Powered by Gemini")

with st.expander("Ejemplos de promt", expanded=True):
    st.write(
        """
        - Califica este candidato.
        - Compara los candidatos en una tabla resumen.
        - Dame el numero de DNI de <nombre>.
        - Que candidato domina mas lenguajes.
    """
    )


def initialize_session_state():
    if "chat_session" not in st.session_state:
        st.session_state.chat_session = model.start_chat(history = [])
    if "messages" not in st.session_state:
        st.session_state.messages = []
    # flags para flujo de archivo adjunto
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []
        st.session_state.uploaded_files_uris = []
    if "uploaded_xlsx" not in st.session_state:
        st.session_state.uploaded_xlsx = None
    if "xlsx_df" not in st.session_state:
        st.session_state.xlsx_df = None
    if 'user_input_prompt' not in st.session_state: # This one is specifically use for clearing the user text input after they hit enter
        st.session_state.user_input_prompt = 'None'
    if "file_uploader_key" not in st.session_state:
        st.session_state["file_uploader_key"] = 0
    if "processing" not in st.session_state:
        st.session_state.processing = False
    # if 'model_processing' not in st.session_state:
    #     st.session_state.model_processing = False

def print_chat_history(chat):
    print("Chat History:")
    print(chat.history)
############################################# Main #############################################

# Initialize the session state variables
initialize_session_state()

# rednderizar todo
for message in  st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"].replace("$", "\$"))  # noqa: W605
# inicializar promt
prompt = st.chat_input("Como te puedo ayudar?", disabled=st.session_state.processing)

def save_xlsx(uploaded_xlsx):
    destination_blob_name = f"{SUBFOLDER}/{uploaded_xlsx.name}"
    uri = upload_to_gcs(BUCKET_NAME, uploaded_xlsx, destination_blob_name)
    print(f"uri del xlsx: {uri}")
    return uri
# Crear file_uploader para múltiples archivos
with st.sidebar:
    uploaded_files = st.file_uploader("Elija los CV de candidatos en PDF", type="pdf", accept_multiple_files=True, key=st.session_state["file_uploader_key"])
    if uploaded_files != []:
        # Use to check if PDFs are uploaded
        st.session_state.uploaded_files = uploaded_files
        # st.session_state.uploaded_files_uris = []
    uploaded_xlsx = st.file_uploader("Suba candidatos por Excel", type="xlsx")
    if uploaded_xlsx != None:
        st.session_state.uploaded_xlsx = uploaded_xlsx
        print(f"filename: {uploaded_xlsx.name}")
        df = pd.read_excel(uploaded_xlsx, dtype=str)
        st.session_state.xlsx_df = df
        # save_xlsx(uploaded_xlsx)
        

# if uploaded_xlsx != None:
if st.session_state.uploaded_xlsx is not None:
    st.subheader("Preview:")
    st.write(st.session_state.xlsx_df.head(10))
    if st.button("Confirmar carga de archivo"):
        st.session_state.processing = True
        save_xlsx(st.session_state.uploaded_xlsx)

# if st.session_state.processing:
#     progress_text = "Procesando archivo..."
#     my_bar = st.progress(0, text=progress_text)
#     for percent_complete in range(100):
#         time.sleep(3)  # Simulate processing time
#         my_bar.progress(percent_complete + 1, text=progress_text)
#     st.success("Procesamiento completado!")
#     st.session_state.processing = False

if st.session_state.processing:
    df = st.session_state.xlsx_df
    total_rows = len(df)
    total_time = total_rows * 10  # Total processing time in seconds
    progress_text = "Procesando archivo..."
    my_bar = st.progress(0, text=progress_text)
    
    for i, row in df.iterrows():
        time.sleep(10)  # Simulate processing time for each row
        progress = (i + 1) / total_rows
        my_bar.progress(progress, text=f"{progress_text} ({int(progress * 100)}%)")
    
    st.success("Procesamiento completado!")
    st.session_state.processing = False


def debug(text=''):
    print(text)
    print(f'**messages in session_state: {st.session_state.messages}, len: {len(st.session_state.messages)}')
    print(f'**uploaded_files in session_state: {"uploaded_files" in st.session_state}')
    print(f'**session_state.uploaded_files: {st.session_state.uploaded_files}, len: {len(uploaded_files)}')
    for uri in st.session_state.uploaded_files_uris:
        print(f"     ->{uri}")

def create_multimodal_message(file_uris, promt=""):
    documents = [Part.from_uri(mime_type="application/pdf", uri=uri) for uri in file_uris]
    return documents + [Part.from_text(prompt)]

def save_new_files(uploaded_files):
    new_files = []
    for uploaded_file in uploaded_files:
        destination_blob_name = f"{SUBFOLDER}/{uploaded_file.name}"
        file_uri = f"gs://{BUCKET_NAME}/{destination_blob_name}"
        print(f'session_state.uploaded_files_uris: {st.session_state.uploaded_files_uris}')
        if file_uri not in st.session_state.uploaded_files_uris:
            print(f"entro nuevo fiel: {file_uri}")
            st.session_state.uploaded_files_uris.append(file_uri)
            # Save the file to GCS
            uri = upload_to_gcs(BUCKET_NAME, uploaded_file, destination_blob_name)
            new_files.append(uri)

    return new_files

# debug("---->antes")
#Chat
if prompt:
    # Renderizar input del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    if prompt.isspace():
        with st.chat_message("assistant"):
            st.markdown("Ingresa un texto no vacio por favor.")
    else:
        # Renderizar response modelo
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            prompt += """, Responde en español, por favor."""
            with st.spinner("Respondiendo..."):
                # st.session_state.model_processing = True
                
                new_pdfs = save_new_files(st.session_state.uploaded_files)
                if st.session_state.uploaded_xlsx != None:
                    mm_message = f"Usa el dataframe con nombre df con columnas {st.session_state.xlsx_df.columns} y genera el codigo python para {prompt}"
                    response = st.session_state.chat_session.send_message(mm_message, generation_config=generation_config, safety_settings=safety_settings, stream=False)
                    response = response.candidates[0].content.parts[0].text
                    # response.parts[0].text
                    print(f"xlsx response: \n{response}")
                    # Extract the code block from the response
                    start_index = response.find("```python") + len("```python")
                    end_index = response.find("```", start_index)
                    extracted_code = response[start_index:end_index].strip()

                    # Display the extracted code
                    # st.subheader("Extracted Code:")
                    # st.code(extracted_code, language='python')

                    # Execute the extracted code and capture the output
                    with StringIO() as output_buffer:
                        with redirect_stdout(output_buffer):
                            exec(extracted_code)
                        captured_output = output_buffer.getvalue()

                    # Display the captured output
                    st.subheader("Captured Output:")
                    st.code(captured_output, language='python')
                    full_response = captured_output
                else:
                    mm_message = create_multimodal_message(new_pdfs, prompt)
                    response = st.session_state.chat_session.send_message(mm_message, generation_config=generation_config, safety_settings=safety_settings, stream=True)

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
            # print(f"full_response: {full_response}")
            # st.session_state.model_processing = False
            # with message_placeholder.container():
            #     st.markdown(full_response.replace("$", "\$"))  # noqa: W605

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": full_response,
                }
            )
            print_chat_history(st.session_state.chat_session)

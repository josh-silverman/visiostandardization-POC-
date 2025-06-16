import streamlit as st
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
import openai
import os
import base64

# --- Load environment variables ---
load_dotenv()

AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
BLOB_CONTAINER = os.getenv("BLOB_CONTAINER")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")  # GPT-4o deployment

# --- Initialize Azure Blob Storage client ---
try:
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(BLOB_CONTAINER)
except Exception as e:
    st.error(f"Could not connect to Azure Blob Storage: {e}")
    st.stop()

# --- Initialize Azure OpenAI client ---
openai.api_type = "azure"
openai.api_base = AZURE_OPENAI_ENDPOINT
openai.api_version = "2024-02-15-preview"
openai.api_key = AZURE_OPENAI_API_KEY

st.title("PNG Shape Counter with Azure OpenAI GPT-4o")

st.markdown("""
Upload a PNG diagram (e.g., a flowchart or schematic), and GPT-4o Vision will tell you how many boxes (rectangles) are in the image.
""")

uploaded_file = st.file_uploader("Upload PNG image", type=["png"])

if uploaded_file is not None:
    # Show image preview
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
    
    # Save to Azure Blob Storage
    if st.button("Upload to Azure Storage"):
        try:
            blob_client = container_client.get_blob_client(uploaded_file.name)
            uploaded_file.seek(0)  # Ensure file pointer is at start
            blob_client.upload_blob(uploaded_file, overwrite=True)
            st.success(f"'{uploaded_file.name}' uploaded to Azure Blob Storage!")
        except Exception as e:
            st.error(f"Upload failed: {e}")

    # Option to send to GPT-4o
    if st.button("Analyze with GPT-4o Vision"):
        # Read image bytes and base64 encode
        uploaded_file.seek(0)
        image_bytes = uploaded_file.read()
        image_base64 = base64.b64encode(image_bytes).decode()

        question = st.text_input("Ask a question about the image:", "How many shapes are in this image? WHat are the different types of shapes")

        with st.spinner("Sending image to Azure OpenAI GPT-4o..."):
            try:
                response = openai.ChatCompletion.create(
                    engine=AZURE_OPENAI_DEPLOYMENT,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant who specializes in analyzing diagrams."},
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": question},
                                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                            ],
                        }
                    ],
                    max_tokens=500,
                )
                answer = response['choices'][0]['message']['content']
                st.markdown("**GPT-4o's Answer:**")
                st.write(answer)
            except Exception as e:
                st.error(f"Azure OpenAI error: {e}")

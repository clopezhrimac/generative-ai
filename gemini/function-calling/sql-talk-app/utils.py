from google.cloud import storage
import os

# Función para subir archivos a Google Cloud Storage
def upload_to_gcs(bucket_name, file, destination_blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_file(file)
    file_uri = f"gs://{bucket_name}/{destination_blob_name}"
    return file_uri
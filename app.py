from flask import Flask, request, jsonify
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.storage.blob import BlobServiceClient
import uuid

app = Flask(__name__)

KEY_VAULT_URL = "https://mediaappvault1.vault.azure.net/"

def get_storage_client():
    credential = DefaultAzureCredential()
    secret_client = SecretClient(vault_url=KEY_VAULT_URL, credential=credential)
    conn_str = secret_client.get_secret("StorageConnectionString").value
    return BlobServiceClient.from_connection_string(conn_str)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Media Upload API is running!"}), 200

@app.route("/upload", methods=["POST"])
def upload_image():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    blob_name = str(uuid.uuid4()) + "-" + file.filename
    try:
        blob_service = get_storage_client()
        container_client = blob_service.get_container_client("images")
        container_client.upload_blob(name=blob_name, data=file.read())
        return jsonify({"message": "Uploaded!", "blob_name": blob_name}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

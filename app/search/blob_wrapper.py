from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from dotenv import load_dotenv
import os

class BlobWrapper:
    """
    A wrapper for Azure Blob Storage operations, including listing, uploading, and deleting blobs.
    Initializes the connection using environment variables.
    """
    def __init__(self, source_directory_path=None):
        """
        Initialize BlobWrapper with optional source directory path.
        Loads environment variables, sets up credentials, and performs uploads.
        """
        load_dotenv()
        self.account_url = os.getenv("AZURE_STORAGE_ACCOUNT_URL")
        self.container = os.getenv("AZURE_STORAGE_CONTAINER_NAME")
        self.source_directory = source_directory_path or os.getenv("AZURE_BLOB_SOURCE_DIRECTORY")
        self.credential = DefaultAzureCredential()
        self.blob_service_client = BlobServiceClient(account_url=self.account_url, credential=self.credential)
        self.container_client = self.blob_service_client.get_container_client(container=self.container)

    def list(self):
        """
        List all blobs in the container.
        Returns:
            A list or generator of blob objects.
        """
        try:
            # Get iterable list of blobs
            list = self.container_client.list_blobs()
            return list
        except Exception as e:
            print(e)

    def delete(self, blob_name):
        """
        Delete the specified blob by name.
        Parameters:
            blob_name (str): The name of the blob to delete.
        """
        try:
            blob_client = self.blob_service_client.get_blob_client(container=self.container, blob=blob_name)
            blob_client.delete_blob()
        except Exception as e:
            print(e)

    def upload(self, filename, file_path):
        """
        Upload a file as a blob to the container.
        Parameters:
            filename (str): The path of the file to upload.
        """
        try:
            with open(file_path, "rb") as data:
                container_client = self.blob_service_client.get_container_client(self.container)
                container_client.upload_blob(name=filename, data=data, overwrite=False)
        except Exception as e:
            print(e)

    def upload_all(self, source_directory=None):
        """
        Upload all files from the source directory if it exists.
        """
        if source_directory:
            self.source_directory = source_directory

        if self.source_directory and os.path.isdir(self.source_directory):
            for filename in os.listdir(self.source_directory):
                file_path = os.path.join(self.source_directory, filename)
                if os.path.isfile(file_path):
                    self.upload(filename=filename, file_path=file_path)
        else:
            # Log when no valid source directory is available
            print("No source directory found, skipping upload")


# main
if __name__ == "__main__":
    blob_wrapper = BlobWrapper()
from azure.storage.blob import BlobServiceClient
from datetime import datetime
import json
from typing import Optional
from kleiven.azure.storage import BlobStorage

class BlobService:
    def __init__(self, connection_string: str):
        self._client = BlobServiceClient.from_connection_string(
            conn_str=connection_string)

    @property
    def client(self) -> BlobServiceClient:
        return self._client

    def get_blob_storage(self, container: str, blob: str) -> "BlobStorage":
        blob_client = self.client.get_blob_client(container=container,
                                                  blob=blob)
        return BlobStorage(client=blob_client)

    def create_and_upload_blob(self, data,
                               container: str,
                               blob_name: str,
                               tags=None,
                               overwrite: bool = False
                               ) -> Optional["BlobStorage"]:

        blob_storage = self.get_blob_storage(container=container,
                                             blob=blob_name)
        if overwrite or not blob_storage.client.exists():
            # Upload the created file
            blob_storage.client.upload_blob(
                json.dumps(data), overwrite=overwrite)

            # Create tags if given
            if tags is not None:
                blob_storage.client.set_blob_tags(tags=tags)
            else:
                tags = {}

            # Create metadata
            metadata = {**tags, "timestamp": datetime.utcnow().isoformat()}
            blob_storage.client.set_blob_metadata(metadata)

            return blob_storage

        return None

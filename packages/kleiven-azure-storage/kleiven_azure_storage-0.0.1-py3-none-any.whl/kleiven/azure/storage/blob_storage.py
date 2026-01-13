from azure.storage.blob import BlobClient

class BlobStorage:

    def __init__(self, client: BlobClient):
        self._client = client

    @property
    def client(self) -> BlobClient:
        return self._client

    @property
    def container(self) -> str:
        return self.client.container_name

    @property
    def blob(self):
        return self.client.blob_name

    @property
    def metadata(self):
        return self.client.get_blob_properties().get("metadata", {})

from azure.data.tables import TableServiceClient
from kleiven.azure.storage import TableStorage

class TableService:
    def __init__(self, connection_string: str):
        self._client = TableServiceClient.from_connection_string(
            conn_str=connection_string)

    @property
    def client(self) -> TableServiceClient:
        return self._client

    def get_table_storage(self, table_name: str) -> "TableStorage":
        table_client = self.client.get_table_client(table_name=table_name)
        return TableStorage(client=table_client)
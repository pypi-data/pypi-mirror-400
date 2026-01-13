from .table_storage import TableStorage
from .table_service import TableService
from .blob_storage import BlobStorage
from .blob_service import BlobService
import os
from dotenv import load_dotenv


load_dotenv()

def get_table_service(env_variable_name: str = "AZURE_STORAGE_CONNECTION_STRING") -> TableService:
    connection_string = os.getenv(env_variable_name, None)
    if connection_string is None:
        raise Exception(f"No connection string in envvar {env_variable_name} "
                        "found.")
    return TableService(connection_string=os.getenv(env_variable_name))

def get_table_storage(table_name: str, env_variable_name: str = "AZURE_STORAGE_CONNECTION_STRING") -> TableStorage:  # noqa E501
    return get_table_service(
        env_variable_name).get_table_storage(table_name=table_name)


def get_blob_service(env_variable_name: str = "AZURE_STORAGE_CONNECTION_STRING") -> BlobService:
    connection_string = os.getenv(env_variable_name, None)
    if connection_string is None:
        raise Exception(f"No connection string in envvar {env_variable_name} "
                        "found.")
    return BlobService(connection_string=os.getenv(env_variable_name))

def get_blob_storage(container: str, blob: str, env_variable_name: str = "AZURE_STORAGE_CONNECTION_STRING") -> BlobStorage:  # noqa E501
    return get_blob_service(
        env_variable_name).get_blob_storage(container=container, blob=blob)

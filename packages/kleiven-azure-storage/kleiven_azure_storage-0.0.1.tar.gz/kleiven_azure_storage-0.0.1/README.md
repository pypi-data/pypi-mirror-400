# kleiven-azure-storage

Small helpers around Azure Table Storage and Blob Storage clients. The package
wraps the Azure SDK to keep common operations short and consistent.

```bash
pip install kleiven-azure-storage
```

## Requirements

- Python 3.10+
- `azure-data-tables`
- `azure-storage-blob`
- `python-dotenv`


## Configuration

The package loads environment variables via `python-dotenv`.
Define your Azure connection string in `.env` or the shell:

```env
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=...;
```

You can also pass a custom env var name to the helpers.

## Quick start

### Tables

```python
from kleiven.azure.storage import get_table_storage

users = get_table_storage(table_name="users", env_variable_name = "AZURE_STORAGE_CONNECTION_STRING")

# Get an entity
entity = users.get_entity(
        partition_key = 'users',
        row_key = "123",
        select = 'Name') # None if it partition_key, row_key does not exist in table

if entity is not None:
  print(entity.get("Name", None))



# Upsert entity (replace by default)
entity = {
    "PartitionKey": "users",
    "RowKey": "123",
    "name": "Ada",
}

# Upsert entity (replace by default)
table.upsert_entity(entity)

# Upsert entity: Merge
from azure.data.tables import UpdateMode
storage.upsert_entity(
    entity=entity,
    mode=UpdateMode.MERGE,
    create_table_if_not_exist = True
)

# Create table if not already exist
storage.upsert_entity(
    entity=entity,
    create_table_if_not_exist = True
)


```

### Blobs

```python
from kleiven.azure.storage import get_blob_service

service = get_blob_service()
blob = service.create_and_upload_blob(
    data={"hello": "world"},
    container="my-container",
    blob_name="example.json",
    tags={"source": "demo"},
    overwrite=True,
)

if blob is not None:
    print(blob.container, blob.blob)
    print(blob.metadata)
```

## API overview

### Helper functions

- `get_table_service(env_variable_name="AZURE_STORAGE_CONNECTION_STRING")`
- `get_table_storage(table_name, env_variable_name="AZURE_STORAGE_CONNECTION_STRING")`
- `get_blob_service(env_variable_name="AZURE_STORAGE_CONNECTION_STRING")`
- `get_blob_storage(container, blob, env_variable_name="AZURE_STORAGE_CONNECTION_STRING")`

### TableStorage

`TableStorage` wraps `azure.data.tables.TableClient`:

- `upsert_entity(entity, mode=UpdateMode.REPLACE, create_table_if_not_exist=False)`
- `get_entity(partition_key, row_key, select=None, silent=True, create_table_if_not_exist=False)`
- `query_entities(query_filter, select=None)`
- `get_entities(entities, select=None)`
- `batch_save(entities, update_mode=UpdateMode.MERGE, create_table_if_not_exist=False)`
- `batch_delete(entities)`

### BlobService and BlobStorage

`BlobService` wraps `azure.storage.blob.BlobServiceClient`:

- `get_blob_storage(container, blob)`
- `create_and_upload_blob(data, container, blob_name, tags=None, overwrite=False)`

`BlobStorage` exposes convenience properties:

- `container`
- `blob`
- `metadata`

## Notes

- `create_and_upload_blob` returns `None` when `overwrite=False` and the blob
  already exists.
- `create_table_if_not_exist=True` currently depends on a `wolfbrain.storage`
  helper. If you do not have that dependency, keep the flag set to `False`.

from azure.data.tables import (TableClient, TableEntity, UpdateMode,
                               TableTransactionError)
from azure.core.exceptions import ResourceNotFoundError
from typing import Optional, Union

class TableStorage:

    def __init__(self, client: TableClient):
        self._client = client

    @property
    def table_name(self) -> str:
        return self.client.table_name()

    @property
    def client(self) -> TableClient:
        return self._client

    @staticmethod
    def swap_to_edm_types(entity):
        for key, value in entity.items():
            if isinstance(value, int) and value > 2**31 - 1:
                entity[key] = str(value)
        return entity

    def upsert_entity(self, entity,
                      mode=UpdateMode.REPLACE,
                      create_table_if_not_exist=False) -> "dict[str, str]":
        try:
            self.client.upsert_entity(mode=mode, entity=entity)
        except ResourceNotFoundError as e:
            if create_table_if_not_exist:
                from kleiven.azure.storage import get_table_service
                ts = get_table_service().client
                new_client = ts.create_table_if_not_exists(
                    self.client.table_name)
                # Try again
                new_client.upsert_entity(mode=mode, entity=entity)
            else:
                raise e

    def get_entity(self, partition_key, row_key,
                   select=None,
                   silent=True,
                   create_table_if_not_exist=False) -> TableEntity:

        try:
            if select:
                return self.client.get_entity(
                    partition_key=partition_key, row_key=row_key,
                    select=select)
            else:
                return self.client.get_entity(
                    partition_key=partition_key, row_key=row_key)

        except ResourceNotFoundError as e:
            if silent:
                return None
            else:
                raise e

    def query_entities(self, query_filter: str,
                       select: Optional[Union[str, "list[str]"]] = None):
        if select is not None:
            select = ','.join(select)
        pages = self.client.query_entities(
            query_filter=query_filter, select=select).by_page()
        result = []
        for page in pages:
            for entity in page:
                result.append(entity)

        return result

    def get_entities(self, entities, select=None):
        if select is not None:
            select = ','.join(select)

        result = []
        filter = ""
        i = 0
        for entity in entities:
            pk = entity['PartitionKey']
            rk = entity['RowKey']

            if i == 14:
                for record in self.client.query_entities(query_filter=filter,
                                                         select=select):
                    result.append(record)
                i = 0

            if i == 0:
                filter = (f"(PartitionKey eq '{pk}' and RowKey eq"f" '{rk}')")
            else:
                filter = filter + \
                    f" or (PartitionKey eq '{pk}' and RowKey eq '{rk}')"
            i = i + 1

        if i > 0:
            for record in self.client.query_entities(query_filter=filter,
                                                     select=select):
                result.append(record)

        return result

    def batch_delete(self,
                     entities: "list[dict]"):
        max_operations_per_batch = 100
        batches = []  # type: list[tuple[str,dict, dict[str, UpdateMode]]]

        added = {}  # type: dict[str, dict[str, bool]]
        partitions = {}   # type: dict[str, list]
        for entity in entities:
            pk = entity["PartitionKey"]
            operation = ("delete", entity)

            if pk in partitions:
                if added.get(pk, {}).get(entity["RowKey"], False):
                    continue
                partitions[pk].append(operation)
                if len(partitions[pk]) == max_operations_per_batch:
                    batches.append(partitions[pk])
                    del partitions[pk]
                    del added[pk]
            else:
                partitions[pk] = [operation]

            if pk not in added:
                added[pk] = {}

            added[pk][entity["RowKey"]] = True

        for operations in partitions.values():
            batches.append(operations)

        responses = []
        for operations in batches:
            responses.extend(self.client.submit_transaction(operations))

        return responses

    def batch_save(self,
                   entities: "list[dict]",
                   update_mode=UpdateMode.MERGE,
                   create_table_if_not_exist=False):
        max_operations_per_batch = 100
        batches = []  # type: list[tuple[str,dict, dict[str, UpdateMode]]]

        added = {}  # type: dict[str, dict[str, bool]]
        partitions = {}   # type: dict[str, list]
        for entity in entities:
            TableStorage.swap_to_edm_types(entity)

            pk = entity["PartitionKey"]
            operation = ("upsert", entity, {"mode": update_mode})

            if pk in partitions:
                if added.get(pk, {}).get(entity["RowKey"], False):
                    continue
                partitions[pk].append(operation)
                if len(partitions[pk]) == max_operations_per_batch:
                    batches.append(partitions[pk])
                    del partitions[pk]
                    del added[pk]
            else:
                partitions[pk] = [operation]

            if pk not in added:
                added[pk] = {}

            added[pk][entity["RowKey"]] = True

        for operations in partitions.values():
            batches.append(operations)

        responses = []
        for operations in batches:
            try:
                r = self.client.submit_transaction(operations)
                responses.extend(r)
            except TableTransactionError as e:
                if e.error_code == "TableNotFound":
                    if create_table_if_not_exist:
                        from kleiven.azure.storage import get_table_service
                        ts = get_table_service().client
                        new_client = ts.create_table_if_not_exists(
                            self.client.table_name)
                        # Try again
                        responses.extend(
                            new_client.submit_transaction(operations))
                    else:
                        raise e

        return responses

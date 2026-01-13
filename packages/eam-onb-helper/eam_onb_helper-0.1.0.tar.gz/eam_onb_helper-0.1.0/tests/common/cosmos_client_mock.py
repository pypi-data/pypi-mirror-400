"""This module contains the CosmosClientMock class."""


# pylint: disable=unused-argument
class CosmosClientMock:
    """This class is used to mock the CosmosClient class."""
    def __init__(self, uri, key):
        self.results = []

    def get_database_client(self, data_base: str):
        """Return the database client."""
        return self

    def get_container_client(self, container: str):
        """Return the container client."""
        return self

    def query_items(
            self, query: str,
            parameters: list = None,
            enable_cross_partition_query: bool = False):
        """Return the query results."""
        results = self.results
        self.results = []

        return results

    def upsert_item(self, body):
        """Add an item to the results."""
        self.results.append(body)
        return body

    def delete_item(self, item_id, partition_key):
        """Delete an item from the results."""
        self.results = None
        
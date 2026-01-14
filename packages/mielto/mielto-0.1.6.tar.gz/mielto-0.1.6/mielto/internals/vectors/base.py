from abc import ABC, abstractmethod


class VectorDB(ABC):
    @abstractmethod
    def create(self, name, vector_size, distance):
        """Create a new vector index."""
        pass

    @abstractmethod
    def insert(self, vectors, payloads=None, ids=None):
        """Insert vectors into a collection."""
        pass

    @abstractmethod
    def search(self, query, vectors, limit=5, filters=None):
        """Search for similar vectors."""
        pass

    @abstractmethod
    def delete(self, vector_id):
        """Delete a vector by ID."""
        pass

    @abstractmethod
    def update(self, vector_id, vector=None, payload=None):
        """Update a vector and its payload."""
        pass

    @abstractmethod
    def get(self, vector_id):
        """Retrieve a vector by ID."""
        pass

    @abstractmethod
    def list_indexes(self):
        """List all vector indexes."""
        pass

    @abstractmethod
    def delete_index(self):
        """Delete a vector index."""
        pass

    @abstractmethod
    def info(self):
        """Get information about a vector index."""
        pass

    @abstractmethod
    def list(self, filters=None, limit=None):
        """List all chunks."""
        pass

    @abstractmethod
    def reset(self):
        """Reset by delete the collection and recreate it."""
        pass

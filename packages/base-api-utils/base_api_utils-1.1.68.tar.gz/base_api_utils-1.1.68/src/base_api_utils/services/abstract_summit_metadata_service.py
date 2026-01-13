from abc import abstractmethod, ABC

from django.db.models import Model


class AbstractSummitMetadataService(ABC):

    @abstractmethod
    def upsert(self, show_id, payload) -> Model:
        pass

    @abstractmethod
    def delete(self, show_id):
        pass


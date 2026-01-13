from abc import abstractmethod, ABC

from django.db.models import Model


class AbstractSponsorMetadataService(ABC):

    @abstractmethod
    def upsert(self, payload) -> Model:
        pass

    @abstractmethod
    def delete(self, sponsor_id):
        pass

    @abstractmethod
    def upsert_sponsorship(self, payload) -> Model:
        pass

    @abstractmethod
    def remove_sponsorship(self, sponsorship_id):
        pass

    @abstractmethod
    def upsert_sponsorship_addon(self, payload) -> Model:
        pass

    @abstractmethod
    def remove_sponsorship_addon(self, sponsorship_addon_id):
        pass


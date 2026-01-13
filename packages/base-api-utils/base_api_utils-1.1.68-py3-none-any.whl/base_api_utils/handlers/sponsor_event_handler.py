import logging

from ..domain import EventMessage
from .base_event_handler import BaseEventHandler
from ..utils import handle_db_connections

from ..domain.events import InboundDomainEvent
from ..services import AbstractSponsorMetadataService


class SponsorEventHandler(BaseEventHandler):
    HANDLED_EVENTS = [
        InboundDomainEvent.SPONSOR_CREATED.value,
        InboundDomainEvent.SPONSOR_UPDATED.value,
        InboundDomainEvent.SPONSOR_DELETED.value,
    ]

    def __init__(self, sponsor_service: AbstractSponsorMetadataService) -> None:
        self.sponsor_service = sponsor_service

    def can_handle(self, event_type: str) -> bool:
        return event_type in self.HANDLED_EVENTS

    def handle(self, event: EventMessage) -> bool:
        try:
            logging.getLogger('api').debug(
                f"SponsorEventHandler::handle - Processing sponsor event: {event.event_type} - {event.payload}")

            if event.event_type in [InboundDomainEvent.SPONSOR_CREATED.value, InboundDomainEvent.SPONSOR_UPDATED.value]:
                return self._handle_sponsor_created_or_updated(event)
            elif event.event_type == InboundDomainEvent.SPONSOR_DELETED.value:
                return self._handle_sponsor_deleted(event)
        except Exception as e:
            logging.getLogger('api').error(f"Error processing sponsor event: {e}")
            return False

        return False

    @handle_db_connections(max_retries=3)
    def _handle_sponsor_created_or_updated(self, event: EventMessage) -> bool:
        sponsor_data = event.payload
        self.sponsor_service.upsert(sponsor_data)
        return True

    @handle_db_connections(max_retries=3)
    def _handle_sponsor_deleted(self, event: EventMessage) -> bool:
        sponsor_data = event.payload
        self.sponsor_service.delete(sponsor_data.get('id'))
        return True
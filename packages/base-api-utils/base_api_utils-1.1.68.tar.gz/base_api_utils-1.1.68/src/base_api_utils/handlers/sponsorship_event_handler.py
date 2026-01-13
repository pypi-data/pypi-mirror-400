import logging

from ..domain import EventMessage
from .base_event_handler import BaseEventHandler
from ..utils import handle_db_connections

from ..domain.events import InboundDomainEvent
from ..services import AbstractSponsorMetadataService


class SponsorshipEventHandler(BaseEventHandler):
    HANDLED_EVENTS = [
        InboundDomainEvent.SPONSORSHIP_CREATED.value,
        InboundDomainEvent.SPONSORSHIP_UPDATED.value,
        InboundDomainEvent.SPONSORSHIP_REMOVED.value,
    ]

    def __init__(self, sponsor_service: AbstractSponsorMetadataService) -> None:
        self.sponsor_service = sponsor_service

    def can_handle(self, event_type: str) -> bool:
        return event_type in self.HANDLED_EVENTS

    def handle(self, event: EventMessage) -> bool:
        try:
            logging.getLogger('api').debug(
                f"SponsorshipEventHandler::handle - Processing sponsorship event: {event.event_type} - {event.payload}")

            if event.event_type in [InboundDomainEvent.SPONSORSHIP_CREATED.value,
                                    InboundDomainEvent.SPONSORSHIP_UPDATED.value]:
                return self._handle_sponsorship_created_or_updated(event)
            elif event.event_type == InboundDomainEvent.SPONSORSHIP_REMOVED.value:
                return self._handle_sponsorship_deleted(event)
        except Exception as e:
            logging.getLogger('api').error(f"Error processing sponsorship event: {e}")
            return False

        return False

    @handle_db_connections(max_retries=3)
    def _handle_sponsorship_created_or_updated(self, event: EventMessage) -> bool:
        sponsorship_data = event.payload
        self.sponsor_service.upsert_sponsorship(sponsorship_data)
        return True

    @handle_db_connections(max_retries=3)
    def _handle_sponsorship_deleted(self, event: EventMessage) -> bool:
        sponsorship_data = event.payload
        self.sponsor_service.remove_sponsorship(sponsorship_data.get('id'))
        return True
import logging

from ..domain import EventMessage
from .base_event_handler import BaseEventHandler
from ..utils import handle_db_connections

from ..domain.events import InboundDomainEvent
from ..services import AbstractSponsorMetadataService


class SponsorshipAddOnEventHandler(BaseEventHandler):
    HANDLED_EVENTS = [
        InboundDomainEvent.SPONSORSHIP_ADDON_CREATED.value,
        InboundDomainEvent.SPONSORSHIP_ADDON_UPDATED.value,
        InboundDomainEvent.SPONSORSHIP_ADDON_REMOVED.value,
    ]

    def __init__(self, sponsor_service: AbstractSponsorMetadataService) -> None:
        self.sponsor_service = sponsor_service

    def can_handle(self, event_type: str) -> bool:
        return event_type in self.HANDLED_EVENTS

    def handle(self, event: EventMessage) -> bool:
        try:
            logging.getLogger('api').debug(
                f"SponsorshipAddOnEventHandler::handle - Processing sponsorship addon event: {event.event_type} - {event.payload}")

            if event.event_type in [InboundDomainEvent.SPONSORSHIP_ADDON_CREATED.value,
                                    InboundDomainEvent.SPONSORSHIP_ADDON_UPDATED.value]:
                return self._handle_sponsorship_addon_created_or_updated(event)
            elif event.event_type == InboundDomainEvent.SPONSORSHIP_ADDON_REMOVED.value:
                return self._handle_sponsorship_addon_deleted(event)
        except Exception as e:
            logging.getLogger('api').error(f"Error processing sponsorship addon event: {e}")
            return False

        return False

    @handle_db_connections(max_retries=3)
    def _handle_sponsorship_addon_created_or_updated(self, event: EventMessage) -> bool:
        sponsorship_addon_data = event.payload
        self.sponsor_service.upsert_sponsorship_addon(sponsorship_addon_data)
        return True

    @handle_db_connections(max_retries=3)
    def _handle_sponsorship_addon_deleted(self, event: EventMessage) -> bool:
        sponsorship_addon_data = event.payload
        self.sponsor_service.remove_sponsorship_addon(
            sponsorship_addon_data.get('id'))
        return True
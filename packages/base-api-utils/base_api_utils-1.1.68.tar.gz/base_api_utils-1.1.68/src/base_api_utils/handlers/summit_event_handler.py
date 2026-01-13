import logging

from ..domain import EventMessage
from .base_event_handler import BaseEventHandler
from ..utils import handle_db_connections

from ..domain.events import InboundDomainEvent
from ..services import AbstractSummitMetadataService


class SummitEventHandler(BaseEventHandler):
    HANDLED_EVENTS = [
        InboundDomainEvent.SUMMIT_CREATED.value,
        InboundDomainEvent.SUMMIT_UPDATED.value,
        InboundDomainEvent.SUMMIT_DELETED.value,
    ]

    def __init__(self, show_service: AbstractSummitMetadataService) -> None:
        self.show_service = show_service

    def can_handle(self, event_type: str) -> bool:
        return event_type in self.HANDLED_EVENTS

    def handle(self, event: EventMessage) -> bool:
        try:
            logging.getLogger('api').info(f"Processing summit event: {event.event_type}")

            if event.event_type in [InboundDomainEvent.SUMMIT_CREATED.value, InboundDomainEvent.SUMMIT_UPDATED.value]:
                return self._handle_summit_created_or_updated(event)
            elif event.event_type == InboundDomainEvent.SUMMIT_DELETED.value:
                return self._handle_summit_deleted(event)
        except Exception as e:
            logging.getLogger('api').error(f"Error processing summit event: {e}")
            return False

        return False

    @handle_db_connections(max_retries=3)
    def _handle_summit_created_or_updated(self, event: EventMessage) -> bool:
        summit_data = event.payload
        self.show_service.upsert(summit_data.get('id'), summit_data)
        return True

    @handle_db_connections(max_retries=3)
    def _handle_summit_deleted(self, event: EventMessage) -> bool:
        summit_data = event.payload
        self.show_service.delete(summit_data.get('id'))
        return True
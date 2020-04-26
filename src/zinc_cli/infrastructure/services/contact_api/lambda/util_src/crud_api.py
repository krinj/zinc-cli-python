from typing import Optional

from .crud_exception import CrudException
from .crud_service import CrudService


class CrudApi:

    ACCEPTED_METHODS = ["GET", "PUT", "POST"]

    def __init__(self, service: CrudService):
        self.service = service

    def handle_rest_request(self, event, context):

        method = event["method"] if "method" in event else None
        body = event["body"] if "body" in event else None

        # If no method, this is fatal.
        if method is None or method not in self.ACCEPTED_METHODS:
            raise CrudException("No method detected in request")

        if method == "GET":
            self._handle_get_request(body)

        if method == "PUT":
            self._handle_put_request(body)

        if method == "POST":
            self._handle_post_request(body)

    def _handle_get_request(self, body: Optional[dict]):
        return self.service.get_item_range(partition_key=self.service.get_default_pk())

    def _handle_post_request(self, body: Optional[dict]):
        return self.service.put_item_from_request_body(body)

    def _handle_put_request(self, body: Optional[dict]):
        return self.service.put_item_from_request_body(body)


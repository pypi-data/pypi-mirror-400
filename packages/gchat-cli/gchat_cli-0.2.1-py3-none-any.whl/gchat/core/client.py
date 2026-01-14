"""Google Chat API client wrapper."""

from datetime import datetime

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from gchat.models.message import Message
from gchat.models.space import Space
from gchat.utils.errors import NetworkError, SpaceNotFoundError
from gchat.utils.network import retry_on_network_error


class ChatClient:
    """Wrapper around Google Chat API."""

    def __init__(self, credentials: Credentials):
        self.service = build("chat", "v1", credentials=credentials)

    def list_spaces(self) -> list[Space]:
        """List all spaces the user is a member of."""
        try:
            spaces = []
            page_token = None

            while True:
                request = self.service.spaces().list(pageSize=100, pageToken=page_token)
                response = retry_on_network_error(
                    request.execute, context="listing spaces"
                )

                for space_data in response.get("spaces", []):
                    spaces.append(Space.from_api(space_data))

                page_token = response.get("nextPageToken")
                if not page_token:
                    break

            return spaces

        except HttpError as e:
            raise NetworkError.from_exception(e, "listing spaces")

    def get_space(self, space_id: str) -> Space:
        """Get details of a specific space."""
        # Ensure proper format
        space_name = space_id if space_id.startswith("spaces/") else f"spaces/{space_id}"

        try:
            request = self.service.spaces().get(name=space_name)
            response = retry_on_network_error(request.execute, context="getting space")
            return Space.from_api(response)
        except HttpError as e:
            if e.resp.status == 404:
                raise SpaceNotFoundError(f"Space not found: {space_id}")
            raise NetworkError.from_exception(e, "getting space")

    def send_message(self, space_id: str, text: str) -> Message:
        """Send a text message to a space."""
        space_name = space_id if space_id.startswith("spaces/") else f"spaces/{space_id}"

        try:
            request = (
                self.service.spaces()
                .messages()
                .create(parent=space_name, body={"text": text})
            )
            response = retry_on_network_error(request.execute, context="sending message")
            return Message.from_api(response)
        except HttpError as e:
            if e.resp.status == 404:
                raise SpaceNotFoundError(f"Space not found: {space_id}")
            raise NetworkError.from_exception(e, "sending message")

    def list_messages(
        self,
        space_id: str,
        limit: int = 25,
        after: datetime | None = None,
        before: datetime | None = None,
    ) -> list[Message]:
        """List messages from a space."""
        space_name = space_id if space_id.startswith("spaces/") else f"spaces/{space_id}"

        # Build filter for date range
        filters = []
        if after:
            filters.append(f'createTime > "{after.isoformat()}"')
        if before:
            filters.append(f'createTime < "{before.isoformat()}"')

        filter_str = " AND ".join(filters) if filters else None

        try:
            messages: list[Message] = []
            page_token: str | None = None

            while len(messages) < limit:
                page_size = min(100, limit - len(messages))
                request = self.service.spaces().messages().list(
                    parent=space_name,
                    pageSize=page_size,
                    pageToken=page_token,
                    filter=filter_str,
                )
                response = retry_on_network_error(
                    request.execute, context="listing messages"
                )

                for msg_data in response.get("messages", []):
                    messages.append(Message.from_api(msg_data))
                    if len(messages) >= limit:
                        break

                page_token = response.get("nextPageToken")
                if not page_token:
                    break

            return messages

        except HttpError as e:
            if e.resp.status == 404:
                raise SpaceNotFoundError(f"Space not found: {space_id}")
            raise NetworkError.from_exception(e, "listing messages")

    def search_messages(
        self,
        space_id: str,
        keyword: str | None = None,
        sender: str | None = None,
        after: datetime | None = None,
        before: datetime | None = None,
        limit: int = 50,
    ) -> list[Message]:
        """Search messages with optional filters.

        Date filtering is done API-side, text/sender filtering is done client-side.
        """
        # Get messages with date filter (API-side)
        messages = self.list_messages(
            space_id=space_id,
            limit=limit * 2 if keyword or sender else limit,  # Fetch more if filtering
            after=after,
            before=before,
        )

        # Apply client-side filters
        if keyword:
            keyword_lower = keyword.lower()
            messages = [m for m in messages if keyword_lower in m.text.lower()]

        if sender:
            sender_lower = sender.lower()
            messages = [
                m
                for m in messages
                if sender_lower in m.sender_name.lower()
                or (m.sender_email and sender_lower in m.sender_email.lower())
            ]

        return messages[:limit]

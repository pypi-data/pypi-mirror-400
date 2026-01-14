"""Chat resources."""

from typing import Any

from planvantage.resources.base import BaseResource


class ChatsResource(BaseResource):
    """Resource for managing chats."""

    def get(self, guid: str) -> Any:
        """Get a specific chat by GUID.

        Args:
            guid: The chat's unique identifier.

        Returns:
            Chat data.
        """
        return self._http.get(f"/chat/{guid}")

    def create(self, **kwargs: Any) -> Any:
        """Create a new chat.

        Args:
            **kwargs: Chat fields.

        Returns:
            Created chat data.
        """
        return self._http.post("/chat", json=kwargs)

    def update(
        self,
        guid: str,
        **kwargs: Any,
    ) -> Any:
        """Update a chat.

        Args:
            guid: The chat's unique identifier.
            **kwargs: Fields to update.

        Returns:
            Updated chat data.
        """
        return self._http.patch(f"/chat/{guid}", json=kwargs)

    def delete(self, guid: str) -> None:
        """Delete a chat.

        Args:
            guid: The chat's unique identifier.
        """
        self._http.delete(f"/chat/{guid}")


class ChatMessagesResource(BaseResource):
    """Resource for managing chat messages."""

    def get(self, guid: str) -> Any:
        """Get a specific chat message.

        Args:
            guid: The message's unique identifier.

        Returns:
            Message data.
        """
        return self._http.get(f"/chatmessage/{guid}")

    def create(self, **kwargs: Any) -> Any:
        """Create a new chat message.

        Args:
            **kwargs: Message fields.

        Returns:
            Created message data.
        """
        return self._http.post("/chatmessage", json=kwargs)

    def delete(self, guid: str) -> None:
        """Delete a chat message.

        Args:
            guid: The message's unique identifier.
        """
        self._http.delete(f"/chatmessage/{guid}")

    def get_more(self, chat_guid: str) -> Any:
        """Get more messages for a chat.

        Args:
            chat_guid: The chat's unique identifier.

        Returns:
            Additional messages.
        """
        return self._http.get(f"/chat/moremessages/{chat_guid}")

    def cancel(self, guid: str) -> None:
        """Cancel message processing.

        Args:
            guid: The message's unique identifier.
        """
        self._http.post(f"/chatmessage/{guid}/cancel")

    def reprocess(self, guid: str) -> None:
        """Reprocess a message.

        Args:
            guid: The message's unique identifier.
        """
        self._http.post(f"/chatmessage/{guid}/reprocess")

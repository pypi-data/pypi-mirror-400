"""Plan documents resource."""

from typing import Any, BinaryIO, Optional

from planvantage.models.plandocument import (
    PlanDocumentData,
    PlanDocumentInfo,
)
from planvantage.resources.base import BaseResource


class PlanDocumentsResource(BaseResource):
    """Resource for managing plan documents."""

    def get(self, guid: str) -> PlanDocumentData:
        """Get a specific plan document by GUID.

        Args:
            guid: The document's unique identifier.

        Returns:
            Full document data including extracted content.

        Example:
            >>> doc = client.plandocuments.get("doc_abc123")
            >>> print(doc.filename)
        """
        data = self._http.get(f"/plandocument/{guid}")
        return PlanDocumentData.model_validate(data)

    def upload(
        self,
        plan_sponsor_guid: str,
        file: BinaryIO,
        filename: Optional[str] = None,
    ) -> PlanDocumentInfo:
        """Upload a plan document.

        Args:
            plan_sponsor_guid: The plan sponsor's GUID.
            file: File-like object to upload.
            filename: Optional filename override.

        Returns:
            Created document info.

        Example:
            >>> with open("plan.pdf", "rb") as f:
            ...     doc = client.plandocuments.upload(
            ...         plan_sponsor_guid="ps_abc123",
            ...         file=f,
            ...         filename="Plan Summary 2024.pdf"
            ...     )
        """
        files = {"file": (filename or "document", file)}
        data = self._http.post(
            f"/plansponsor/{plan_sponsor_guid}/plandocument",
            files=files,
        )
        return PlanDocumentInfo.model_validate(data)

    def delete(self, guid: str) -> None:
        """Delete a plan document.

        Args:
            guid: The document's unique identifier.

        Example:
            >>> client.plandocuments.delete("doc_abc123")
        """
        self._http.delete(f"/plandocument/{guid}")

    def download(self, guid: str) -> bytes:
        """Download the document file.

        Args:
            guid: The document's unique identifier.

        Returns:
            File contents as bytes.

        Example:
            >>> content = client.plandocuments.download("doc_abc123")
            >>> with open("plan.pdf", "wb") as f:
            ...     f.write(content)
        """
        return self._http.get(f"/plandocument/{guid}/download")

    def view(self, guid: str) -> bytes:
        """Get document for inline viewing.

        Args:
            guid: The document's unique identifier.

        Returns:
            File contents as bytes.
        """
        return self._http.get(f"/plandocument/{guid}/view")

    def reprocess(self, guid: str) -> None:
        """Reprocess document extraction.

        Args:
            guid: The document's unique identifier.

        Example:
            >>> client.plandocuments.reprocess("doc_abc123")
        """
        self._http.post(f"/plandocument/{guid}/reprocess")

"""Document retrieval endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, overload

from pydantic import BaseModel

if TYPE_CHECKING:
    from secblast.client import SecBlastClient


class DocumentContent(BaseModel):
    """Document content in JSON format."""

    document_id: str
    file_name: str | None = None
    content_type: str | None = None
    size: int | None = None
    data: str | dict

    @property
    def content(self) -> str | dict:
        """Alias for data field."""
        return self.data


class DocumentsMixin:
    """Document retrieval API methods."""

    @overload
    def get_document(
        self: "SecBlastClient",
        document_id: str,
        *,
        output_format: Literal["raw"] = "raw",
        convert_xml_to_json: bool = False,
    ) -> bytes: ...

    @overload
    def get_document(
        self: "SecBlastClient",
        document_id: str,
        *,
        output_format: Literal["json"],
        convert_xml_to_json: bool = False,
    ) -> DocumentContent: ...

    def get_document(
        self: "SecBlastClient",
        document_id: str,
        *,
        output_format: Literal["raw", "json"] = "raw",
        convert_xml_to_json: bool = False,
    ) -> bytes | DocumentContent:
        """
        Fetch a document by ID.

        Args:
            document_id: The document ID (e.g., "0001104659-25-121266-1")
            output_format: "raw" returns bytes, "json" returns structured data
            convert_xml_to_json: Convert XML documents to JSON (only with json format)

        Returns:
            Raw bytes if output_format="raw", DocumentContent if output_format="json"
        """
        params: dict = {"document_id": document_id}

        if output_format == "json":
            params["output_format"] = "json"
            if convert_xml_to_json:
                params["convert_xml_to_json"] = True

            data = self._request("POST", "/document", json=params)
            return DocumentContent.model_validate(data)
        else:
            return self._request_raw("POST", "/document", json=params)

    @overload
    def get_pdf(
        self: "SecBlastClient",
        *,
        document_id: str,
    ) -> bytes: ...

    @overload
    def get_pdf(
        self: "SecBlastClient",
        *,
        accession_number: str,
    ) -> bytes: ...

    def get_pdf(
        self: "SecBlastClient",
        *,
        document_id: str | None = None,
        accession_number: str | None = None,
    ) -> bytes:
        """
        Generate a PDF from a document or entire filing.

        Args:
            document_id: Generate PDF from a single document
            accession_number: Generate PDF from entire filing (all HTML docs)

        Returns:
            PDF binary data

        Note:
            Exactly one of document_id or accession_number must be provided.
        """
        if document_id and accession_number:
            raise ValueError("Provide either document_id or accession_number, not both")
        if not document_id and not accession_number:
            raise ValueError("Must provide either document_id or accession_number")

        params: dict = {}
        if document_id:
            params["document_id"] = document_id
        else:
            params["accession_number"] = accession_number

        return self._request_raw("POST", "/pdf", json=params)

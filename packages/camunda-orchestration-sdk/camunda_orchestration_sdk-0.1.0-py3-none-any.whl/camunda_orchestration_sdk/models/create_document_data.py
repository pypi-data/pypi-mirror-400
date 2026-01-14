from __future__ import annotations

import json
from collections.abc import Mapping
from io import BytesIO
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from .. import types
from ..types import UNSET, File, Unset

if TYPE_CHECKING:
    from ..models.create_document_data_metadata import CreateDocumentDataMetadata


T = TypeVar("T", bound="CreateDocumentData")


@_attrs_define
class CreateDocumentData:
    """
    Attributes:
        file (File):
        metadata (CreateDocumentDataMetadata | Unset): Information about the document.
    """

    file: File
    metadata: CreateDocumentDataMetadata | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        file = self.file.to_tuple()

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "file": file,
            }
        )
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []

        files.append(("file", self.file.to_tuple()))

        if not isinstance(self.metadata, Unset):
            files.append(
                (
                    "metadata",
                    (
                        None,
                        json.dumps(self.metadata.to_dict()).encode(),
                        "application/json",
                    ),
                )
            )

        return files

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_document_data_metadata import CreateDocumentDataMetadata

        d = dict(src_dict)
        file = File(payload=BytesIO(d.pop("file")))

        _metadata = d.pop("metadata", UNSET)
        metadata: CreateDocumentDataMetadata | Unset
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = CreateDocumentDataMetadata.from_dict(_metadata)

        create_document_data = cls(
            file=file,
            metadata=metadata,
        )

        return create_document_data

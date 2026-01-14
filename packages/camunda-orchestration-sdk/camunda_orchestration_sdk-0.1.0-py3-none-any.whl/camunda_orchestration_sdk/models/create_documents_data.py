from __future__ import annotations

import json
from collections.abc import Mapping
from io import BytesIO
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from .. import types
from ..types import UNSET, File, Unset

if TYPE_CHECKING:
    from ..models.create_documents_data_metadata_list_item import (
        CreateDocumentsDataMetadataListItem,
    )


T = TypeVar("T", bound="CreateDocumentsData")


@_attrs_define
class CreateDocumentsData:
    """
    Attributes:
        files (list[File]): The documents to upload.
        metadata_list (list[CreateDocumentsDataMetadataListItem] | Unset): Optional JSON array of metadata object whose
            index aligns with each file entry. The metadata array must have the same length as the files array.
    """

    files: list[File]
    metadata_list: list[CreateDocumentsDataMetadataListItem] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        files = []
        for files_item_data in self.files:
            files_item = files_item_data.to_tuple()

            files.append(files_item)

        metadata_list: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.metadata_list, Unset):
            metadata_list = []
            for metadata_list_item_data in self.metadata_list:
                metadata_list_item = metadata_list_item_data.to_dict()
                metadata_list.append(metadata_list_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "files": files,
            }
        )
        if metadata_list is not UNSET:
            field_dict["metadataList"] = metadata_list

        return field_dict

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []

        for files_item_element in self.files:
            files.append(("files", files_item_element.to_tuple()))

        if not isinstance(self.metadata_list, Unset):
            for metadata_list_item_element in self.metadata_list:
                files.append(
                    (
                        "metadataList",
                        (
                            None,
                            json.dumps(metadata_list_item_element.to_dict()).encode(),
                            "application/json",
                        ),
                    )
                )

        return files

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_documents_data_metadata_list_item import (
            CreateDocumentsDataMetadataListItem,
        )

        d = dict(src_dict)
        files = []
        _files = d.pop("files")
        for files_item_data in _files:
            files_item = File(payload=BytesIO(files_item_data))

            files.append(files_item)

        _metadata_list = d.pop("metadataList", UNSET)
        metadata_list: list[CreateDocumentsDataMetadataListItem] | Unset = UNSET
        if _metadata_list is not UNSET:
            metadata_list = []
            for metadata_list_item_data in _metadata_list:
                metadata_list_item = CreateDocumentsDataMetadataListItem.from_dict(
                    metadata_list_item_data
                )

                metadata_list.append(metadata_list_item)

        create_documents_data = cls(
            files=files,
            metadata_list=metadata_list,
        )

        return create_documents_data

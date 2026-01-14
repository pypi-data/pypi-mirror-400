from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="PinClockData")


@_attrs_define
class PinClockData:
    """
    Attributes:
        timestamp (int): The exact time in epoch milliseconds to which the clock should be pinned.
    """

    timestamp: int

    def to_dict(self) -> dict[str, Any]:
        timestamp = self.timestamp

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "timestamp": timestamp,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        timestamp = d.pop("timestamp")

        pin_clock_data = cls(
            timestamp=timestamp,
        )

        return pin_clock_data

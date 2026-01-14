from __future__ import annotations

from enum import StrEnum

from pydantic import Field

from parcelforce_expresslink.models.base import PFBaseModel


class AlertType(StrEnum):
    ERROR = 'ERROR'
    WARNING = 'WARNING'
    NOTIFICATION = 'NOTIFICATION'


class Alert(PFBaseModel):
    code: int | None = None
    message: str
    type: AlertType = AlertType.NOTIFICATION


class Alerts(PFBaseModel):
    alert: list[Alert] = Field(default_factory=list[Alert])

    @classmethod
    def empty(cls):
        return cls(alert=[])

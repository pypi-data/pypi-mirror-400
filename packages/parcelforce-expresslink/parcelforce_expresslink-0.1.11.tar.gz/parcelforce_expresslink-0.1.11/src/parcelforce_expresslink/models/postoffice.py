from parcelforce_expresslink.models.address import AddressRecipient
from parcelforce_expresslink.models.base import PFBaseModel


class Hours(PFBaseModel):
    open: str | None = None
    close: str | None = None
    close_lunch: str | None = None
    after_lunch_opening: str | None = None


class DayHours(PFBaseModel):
    hours: Hours | None = None


class OpeningHours(PFBaseModel):
    mon: DayHours | None = None
    tue: DayHours | None = None
    wed: DayHours | None = None
    thu: DayHours | None = None
    fri: DayHours | None = None
    sat: DayHours | None = None
    sun: DayHours | None = None
    bank_hol: DayHours | None = None


class Position(PFBaseModel):
    longitude: float | None = None
    latitude: float | None = None


class PostOffice(PFBaseModel):
    post_office_id: str | None = None
    business: str | None = None
    address: AddressRecipient | None = None
    opening_hours: OpeningHours | None = None
    distance: float | None = None
    availability: bool | None = None
    position: Position | None = None
    booking_reference: str | None = None


class ConvenientCollect(PFBaseModel):
    postcode: str | None = None
    post_office: list[PostOffice] | None = None
    count: int | None = None
    post_office_id: str | None = None


class SpecifiedPostOffice(PFBaseModel):
    postcode: str | None = None
    post_office: list[PostOffice | None]
    count: int | None = None
    post_office_id: str | None = None

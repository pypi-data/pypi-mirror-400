from typing import Self, TYPE_CHECKING

from pydantic import Field

from parcelforce_expresslink.models.address import AddressCollection, AddressTemporary
from parcelforce_expresslink.models.base import PFBaseModel, DateTimeRange
from parcelforce_expresslink.models.contact import ContactCollection
from parcelforce_expresslink.models.postoffice import ConvenientCollect, SpecifiedPostOffice
from parcelforce_expresslink.models.services import ServiceCodes

if TYPE_CHECKING:
    from parcelforce_expresslink.models.shipment import Shipment


class Returns(PFBaseModel):
    returns_email: str | None = None
    email_message: str | None = None
    email_label: bool


class CollectionInfo(PFBaseModel):
    collection_contact: ContactCollection
    collection_address: AddressCollection
    collection_time: DateTimeRange

    @classmethod
    def from_shipment(cls, shipment: 'Shipment') -> Self:
        return cls(
            collection_address=AddressCollection(**shipment.recipient_address.model_dump()),
            collection_contact=ContactCollection.model_validate(
                shipment.recipient_contact.model_dump(exclude={'notifications'})
            ),
            collection_time=DateTimeRange.null_times_from_date(shipment.shipping_date),
        )


class NominatedDeliveryDatelist(PFBaseModel):
    nominated_delivery_date: list[str] = Field(default_factory=list)


class Department(PFBaseModel):
    department_id: list[int | None] = Field(None, description='')
    service_codes: list[ServiceCodes | None] = Field(None, description='')
    nominated_delivery_date_list: NominatedDeliveryDatelist | None = None


class Departments(PFBaseModel):
    department: list[Department] = Field(default_factory=list)


class NominatedDeliveryDates(PFBaseModel):
    service_code: str | None = None
    departments: Departments | None = None


class SafePlacelist(PFBaseModel):
    safe_place: list[str] = Field(default_factory=list)


class SpecifiedNeighbour(PFBaseModel):
    address: list[AddressTemporary] = Field(default_factory=list)


class DeliveryOptions(PFBaseModel):
    convenient_collect: ConvenientCollect | None = None
    irts: bool | None = None
    letterbox: bool | None = None
    specified_post_office: SpecifiedPostOffice | None = None
    specified_neighbour: str | None = None
    safe_place: str | None = None
    pin: int | None = None
    named_recipient: bool | None = None
    address_only: bool | None = None
    nominated_delivery_date: str | None = None
    personal_parcel: str | None = None

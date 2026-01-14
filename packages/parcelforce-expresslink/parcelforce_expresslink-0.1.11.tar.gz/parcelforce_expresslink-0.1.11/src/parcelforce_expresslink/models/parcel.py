from parcelforce_expresslink.models.base import PFBaseModel


class HazardousGood(PFBaseModel):
    lqdgun_code: str | None = None
    lqdg_description: str | None = None
    lqdg_volume: float | None = None
    firearms: str | None = None


class HazardousGoods(PFBaseModel):
    hazardous_good: list[HazardousGood]


class ContentDetail(PFBaseModel):
    country_of_manufacture: str
    country_of_origin: str | None = None
    manufacturers_name: str | None = None
    description: str
    unit_weight: float
    unit_quantity: int
    unit_value: float
    currency: str
    tariff_code: str | None = None
    tariff_description: str | None = None
    article_reference: str | None = None


class ContentDetails(PFBaseModel):
    content_detail: list[ContentDetail]


class ContentData(PFBaseModel):
    name: str
    data: str


class ParcelContents(PFBaseModel):
    item: list[ContentData]

class Parcel(PFBaseModel):
    weight: float | None = None
    length: int | None = None
    height: int | None = None
    width: int | None = None
    purpose_of_shipment: str | None = None
    invoice_number: str | None = None
    export_license_number: str | None = None
    certificate_number: str | None = None
    content_details: ContentDetails | None = None
    shipping_cost: float | None = None

class Parcels(PFBaseModel):
    parcel: list[Parcel]


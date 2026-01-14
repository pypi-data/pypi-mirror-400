from pathlib import Path

from pydantic import Field

from parcelforce_expresslink.models.base import PFBaseModel
from parcelforce_expresslink.models.parcel import ParcelContents


class LabelItem(PFBaseModel):
    name: str
    data: str


class LabelData(PFBaseModel):
    item: list[LabelItem]


class Barcode(PFBaseModel):
    name: str
    data: str


class Barcodes(PFBaseModel):
    barcode: list[Barcode]


class Image(PFBaseModel):
    name: str
    data: str


class Images(PFBaseModel):
    image: list[Image]


class ParcelLabelData(PFBaseModel):
    parcel_number: str | None = None
    shipment_number: str | None = None
    journey_leg: str | None = None
    label_data: LabelData | None = None
    barcodes: Barcodes | None = None
    images: Images | None = None
    parcel_contents: list[ParcelContents | None] = Field(None, description='')


class ShipmentLabelData(PFBaseModel):
    parcel_label_data: list[ParcelLabelData]


class ManifestShipment(PFBaseModel):
    shipment_number: str
    service_code: str


class ManifestShipments(PFBaseModel):
    manifest_shipment: list[ManifestShipment]


class Document(PFBaseModel):
    data: bytes

    def download(self, outpath: Path) -> Path:
        with open(outpath, 'wb') as f:
            f.write(self.data)
        return Path(outpath)

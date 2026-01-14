from __future__ import annotations

from datetime import date

from pydantic import Field

from parcelforce_expresslink.models.base import PFBaseModel, DateTimeRange
from parcelforce_expresslink.models.documents import ManifestShipments
from parcelforce_expresslink.models.parcel import Parcels


class CompletedShipment(PFBaseModel):
    shipment_number: str | None = None
    out_bound_shipment_number: str | None = None
    in_bound_shipment_number: str | None = None
    partner_number: str | None = None


class CompletedCancelInfo(PFBaseModel):
    status: str | None = None
    shipment_number: str | None = None


class CompletedCancel(PFBaseModel):
    completed_cancel_info: CompletedCancelInfo | None = None


class Enhancement(PFBaseModel):
    enhanced_compensation: str | None = None
    saturday_delivery_required: bool | None = None


class CompletedManifestInfo(PFBaseModel):
    department_id: int
    manifest_number: str
    manifest_type: str
    total_shipment_count: int
    manifest_shipments: ManifestShipments


class CompletedShipments(PFBaseModel):
    completed_shipment: list[CompletedShipment] = Field(default_factory=list)


class CompletedShipmentInfoCreatePrint(PFBaseModel):
    lead_shipment_number: str | None = None
    shipment_number: str | None = None
    delivery_date: str | None = None
    status: str
    completed_shipments: CompletedShipments


class CompletedShipmentInfo(PFBaseModel):
    lead_shipment_number: str | None = None
    delivery_date: date | None = None
    status: str | None = None
    completed_shipments: CompletedShipments | None = None


class CompletedManifests(PFBaseModel):
    completed_manifest_info: list[CompletedManifestInfo]


class InternationalInfo(PFBaseModel):
    parcels: Parcels | None = None
    exporter_customs_reference: str | None = None
    recipient_importer_vat_no: str | None = None
    original_export_shipment_no: str | None = None
    documents_only: bool | None = None
    documents_description: str | None = None
    value_under200_us_dollars: bool | None = None
    shipment_description: str | None = None
    comments: str | None = None
    invoice_date: str | None = None
    terms_of_delivery: str | None = None
    purchase_order_ref: str | None = None


class CompletedReturnInfo(PFBaseModel):
    status: str
    shipment_number: str
    collection_time: DateTimeRange


class InBoundDetails(PFBaseModel):
    contract_number: str
    service_code: str
    total_shipment_weight: str | None = None
    enhancement: Enhancement | None = None
    reference_number1: str | None = None
    reference_number2: str | None = None
    reference_number3: str | None = None
    reference_number4: str | None = None
    reference_number5: str | None = None
    special_instructions1: str | None = None
    special_instructions2: str | None = None
    special_instructions3: str | None = None
    special_instructions4: str | None = None

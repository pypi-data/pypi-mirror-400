from typing import Self

from pydantic import constr

from parcelforce_expresslink.models.base import PFBaseModel, VALID_POSTCODE


class AddressTemporary(PFBaseModel):
    address_line1: str | None = None
    address_line2: str | None = None
    address_line3: str | None = None
    town: str | None = None
    postcode: str | None = None
    country: str = 'GB'

    @property
    def lines_dict(self):
        return {line_field: getattr(self, line_field) for line_field in sorted(self.lines_fields_set)}

    @property
    def lines_fields_set(self):
        return {_ for _ in self.model_fields_set if 'address_line' in _ and getattr(self, _) is not None}

    @property
    def lines_str(self):
        return '\n'.join(self.lines_dict.values())

    @property
    def lines_str_oneline(self):
        return ', '.join(self.lines_dict.values())


class AddressBase(AddressTemporary):
    address_line1: constr(max_length=24)
    address_line2: constr(max_length=24) | None = None
    address_line3: constr(max_length=24) | None = None
    town: constr(max_length=25)
    postcode: VALID_POSTCODE


class AddressSender(AddressBase):
    @classmethod
    def from_recipient(cls, recipient: AddressBase) -> Self:
        return cls(**recipient.model_dump(exclude_none=True))


class AddressCollection(AddressSender):
    address_line1: constr(max_length=40)
    address_line2: constr(max_length=40) | None = None
    address_line3: constr(max_length=40) | None = None
    town: constr(max_length=30)


class AddressRecipient(AddressCollection):
    address_line1: constr(max_length=40)
    address_line2: constr(max_length=50) | None = None
    address_line3: constr(max_length=60) | None = None
    town: constr(max_length=30)


class AddressChoice[T: AddressCollection | AddressRecipient | AddressTemporary](PFBaseModel):
    address: T
    # address: T = sqm.Field(sa_column=sqm.Column(sqm.JSON))
    score: int


# AddTypes = AddressRecipient | AddressCollection | AddressSender

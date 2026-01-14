import re
from typing import Annotated
import datetime as dt
from pydantic import (
    BaseModel,
    ConfigDict,
    AliasGenerator,
    StringConstraints,
    ValidationError,
    AfterValidator,
    BeforeValidator,
    Field,
)
from pydantic.alias_generators import to_pascal


class PFBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            alias=to_pascal,
        ),
        populate_by_name=True,
        use_enum_values=True,
    )


def string_type(length: int):
    return Annotated[str, StringConstraints(max_length=length)]


POSTCODE_EXCLUDED = {'C', 'I', 'K', 'M', 'O', 'V'}
POSTCODE_PATTERN = re.compile(r'([A-Z]{1,2}\d[A-Z\d]? ?\d[A-Z]{2})')


def validate_uk_postcode(v: str):
    if not re.match(POSTCODE_PATTERN, v) and not set(v[-2:]).intersection(POSTCODE_EXCLUDED):
        raise ValidationError('Invalid UK postcode')
    return v


VALID_POSTCODE = Annotated[
    str,
    AfterValidator(validate_uk_postcode),
    BeforeValidator(lambda s: s.strip().upper()),
    Field(..., description='A valid UK postcode'),
]


class DateTimeRange(PFBaseModel):
    from_: str = Field(alias='From')
    to: str

    @classmethod
    def null_times_from_date(cls, null_date: dt.date):
        null_isodatetime = dt.datetime.combine(null_date, dt.time(0, 0)).isoformat(
            timespec='seconds'
        )
        return cls(from_=null_isodatetime, to=null_isodatetime)

    @classmethod
    def from_datetimes(cls, from_dt: dt.datetime, to_dt: dt.datetime):
        return cls(
            from_=from_dt.isoformat(timespec='seconds'), to=to_dt.isoformat(timespec='seconds')
        )



class ExpressLinkError(Exception): ...


class ExpressLinkWarning(Exception): ...


class ExpressLinkNotification(Exception): ...
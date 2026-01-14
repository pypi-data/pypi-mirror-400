from typing import Self

from pydantic import model_validator, constr

from parcelforce_expresslink.models.base import PFBaseModel
from parcelforce_expresslink.models.notifications import RecipientNotifications, CollectionNotifications

MyPhone = str

class Contact(PFBaseModel):
    business_name: constr(max_length=40)
    mobile_phone: str
    email_address: constr(max_length=50)
    contact_name: constr(max_length=30)
    notifications: RecipientNotifications | None = RecipientNotifications.standard_recipient()

    @property
    def notifications_str(self) -> str:
        msg = f'Recip Notifications = {self.notifications} ({self.email_address} + {self.mobile_phone})'
        return msg

    @classmethod
    def empty(cls):
        return cls(
            business_name='',
            mobile_phone='00000000000',
            email_address='',
            contact_name='',
        )


class ContactCollection(Contact):
    senders_name: constr(max_length=25) | None = None
    telephone: MyPhone | None = None
    notifications: CollectionNotifications | None = CollectionNotifications.standard_collection()

    @property
    def notifications_str(self) -> str:
        msg = f'Collecton Notifications = {self.notifications} ({self.email_address} + {self.mobile_phone})'
        return msg

    @model_validator(mode='after')
    def fill_nones(self):
        self.telephone = self.telephone or self.mobile_phone
        self.senders_name = self.senders_name or self.contact_name
        return self

    # @classmethod
    # def from_contact(cls, contact: Contact):
    #     return cls(
    #         **contact.model_dump(exclude={'notifications'}),
    #         senders_name=contact.contact_name,


class ContactSender(Contact):
    business_name: constr(max_length=25) | None = None
    # business_name: constr(max_length=25)
    mobile_phone: MyPhone
    email_address: constr(max_length=50)
    contact_name: constr(max_length=25) | None = None

    telephone: MyPhone | None = None
    senders_name: constr(max_length=25) | None = None
    notifications: None = None

    @classmethod
    def from_recipient(cls, recipient_contact) -> Self:
        return cls(**recipient_contact.model_dump(exclude={'notifications'}))


class ContactTemporary(Contact):
    business_name: str = ''
    contact_name: str = ''
    mobile_phone: MyPhone | None = None
    email_address: str = ''
    telephone: MyPhone | None = None
    senders_name: str = ''

    @model_validator(mode='after')
    def fake(self):
        for field, value in self.model_dump().items():
            if not value:
                value = '========='
                if field == 'email_address':
                    value = f'{value}@f======f.com'
                setattr(self, field, value)
        return self

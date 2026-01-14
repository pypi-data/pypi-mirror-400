from enum import StrEnum

import pydantic as _p

from parcelforce_expresslink.models.base import PFBaseModel


class RecipientNotification(StrEnum):
    EMAIL = 'EMAIL'
    EMAIL_DOD_INT = 'EMAILDODINT'
    EMAIL_ATTEMPT = 'EMAILATTEMPTDELIVERY'
    EMAIL_COLL_REC = 'EMAILCOLLRECEIVED'
    EMAIL_START_DEL = 'EMAILSTARTOFDELIVERY'
    DELIVERY = 'DELIVERYNOTIFICATION'
    SMS_DOD = 'SMSDAYOFDESPATCH'
    SMS_START_DEL = 'SMSSTARTOFDELIVERY'
    SMS_ATTEMPT_DEL = 'SMSATTEMPTDELIVERY'
    SMS_COLL_REC = 'SMSCOLLRECEIVED'


class RecipientNotifications(PFBaseModel):
    notification_type: list[RecipientNotification] = _p.Field(default_factory=list)

    @classmethod
    def standard_recipient(cls):
        return cls(
            notification_type=[
                RecipientNotification.EMAIL,
                RecipientNotification.SMS_DOD,
                RecipientNotification.DELIVERY,
            ]
        )


class CollectionNotification(StrEnum):
    EMAIL = 'EMAIL'
    EMAIL_RECIEVED = 'EMAILCOLLRECEIVED'
    SMS_RECIEVED = 'SMSCOLLRECEIVED'


class CollectionNotifications(PFBaseModel):
    notification_type: list[CollectionNotification] = _p.Field(default_factory=list)

    @classmethod
    def standard_collection(cls):
        return cls(
            notification_type=[
                CollectionNotification.EMAIL,
                # CollectionNotificationType.SMS_RECIEVED,
                # CollectionNotificationType.EMAIL_RECIEVED,
            ]
        )



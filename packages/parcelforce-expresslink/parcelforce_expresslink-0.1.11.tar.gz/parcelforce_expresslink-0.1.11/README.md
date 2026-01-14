ParcelForce ExpressLink API Client
===============================
A Python client for the ParcelForce ExpressLink API.

Uses Combadge to handle SOAP requests via Pydantic models.

# Installation

pip install parcelforce-expresslink

# Settings

Required:

- API Username
- API Password
- Account Number
- Contract Number

Optional:

- Endpoint (default: https://expresslink.parcelforce.net/ws)
- WSDL (default: bundled)
- Binding (default: {http://www.parcelforce.net/ws/ship/v14}ShipServiceSoapBinding)
- Tracking URL Stem (default: https://www.royalmail.com/track-your-item#/tracking-results/)

## Get settings from EITHER:

### Env File (direct)

ParcelforceSettings.from_env_file(path: str)

### Env File (indirect)

ParcelforceSettings.from_env(env:str) (where env is the environment variable pointing to the env file)

### Args

ParcelForceSettings.from_args(*, usrname: str, password: str, contract_num: str, account_num: str):

# Usage

## Create a client

``` python
    settings = ParcelforceSettings()
    client = ParcelforceClient(settings=settings)
```

## Create a Recipient Contact

``` python
    recip_contact = Contact(
        contact_name="A Name",
        email_address="anaddress@adomain.com",
        mobile_phone="07123456789",
        business_name="A Business Name",
    )
```

## Create a Recipient Address

``` python
    recip_address = AddressRecipient(
        address_line1="An AddressLine",
        town="A Town",
        postcode="AA1BB2",
        )
```

## Create a Shipment

``` python
    shipment = Shipment(
        recipient_address=recip_address,
        recipient_contact=recip_contact,
        total_number_of_parcels=1,
        shipping_date=date.today(),
        )
    response: ShipmentResponse = client.request_shipment(shipment)
    print(f"Shipment Number: {response.shipment_num}, Status: {response.status}")
```


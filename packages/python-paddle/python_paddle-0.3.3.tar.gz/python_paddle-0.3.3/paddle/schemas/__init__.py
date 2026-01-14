from __future__ import annotations

from enum import Enum
from typing import Annotated, Any, Literal

from pydantic import (
    AnyUrl,
    AwareDatetime,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    RootModel,
)


class AddressCity(RootModel[Annotated[str, Field(max_length=200)] | None]):
    root: Annotated[str, Field(max_length=200)] | None = Field(
        ..., description="City of this address.", examples=["Astoria"], title="City"
    )


class AddressDescription(RootModel[Annotated[str, Field(max_length=1024)] | None]):
    root: Annotated[str, Field(max_length=1024)] | None = Field(
        ...,
        description="Memorable description for this address.",
        examples=["Paddle.com"],
        title="Description",
    )


class AddressFirstLine(RootModel[Annotated[str, Field(max_length=1024)] | None]):
    root: Annotated[str, Field(max_length=1024)] | None = Field(
        ...,
        description="First line of this address.",
        examples=["3811 Ditmars Blvd"],
        title="First line",
    )


class AddressId(RootModel[Annotated[str, Field(pattern="^add_[a-z\\d]{26}$")]]):
    root: Annotated[str, Field(pattern="^add_[a-z\\d]{26}$")] = Field(
        ...,
        description="Unique Paddle ID for this address entity, prefixed with `add_`.",
        examples=["add_01gm302t81w94gyjpjpqypkzkf"],
        title="Address ID",
    )


class AddressPostalCode(RootModel[Annotated[str, Field(max_length=200)] | None]):
    root: Annotated[str, Field(max_length=200)] | None = Field(
        ...,
        description="ZIP or postal code of this address. Required for some countries.",
        examples=["11105-1803"],
        title="Postal Code",
    )


class AddressRegion(RootModel[Annotated[str, Field(max_length=200)] | None]):
    root: Annotated[str, Field(max_length=200)] | None = Field(
        ...,
        description="State, county, or region of this address.",
        examples=["NY"],
        title="Region",
    )


class AddressSecondLine(RootModel[Annotated[str, Field(max_length=1024)] | None]):
    root: Annotated[str, Field(max_length=1024)] | None = Field(
        ..., description="Second line of this address.", title="Second line"
    )


class Totals(BaseModel):
    subtotal: str | None = Field(
        None,
        description="Total before tax. For tax adjustments, the value is 0.",
        examples=["15000"],
    )
    tax: str | None = Field(
        None, description="Total tax on the subtotal.", examples=["1500"]
    )
    total: str | None = Field(None, description="Total after tax.", examples=["16500"])


class AdjustmentTaxRatesUsedItem(BaseModel):
    tax_rate: str | None = Field(
        None,
        description="Rate used to calculate tax for this adjustment.",
        examples=["0.2"],
    )
    totals: Totals | None = Field(
        None,
        description="Calculated totals for the tax applied to this adjustment.",
        title="AdjustmentTaxRateUsedTotals",
    )


class AdjustmentTaxRatesUsed(RootModel[list[AdjustmentTaxRatesUsedItem]]):
    root: list[AdjustmentTaxRatesUsedItem] = Field(
        ...,
        description="List of tax rates applied for this adjustment.",
        title="AdjustmentTaxRateUsed",
    )


class AdjustmentAction(Enum):
    credit = "credit"
    refund = "refund"
    chargeback = "chargeback"
    chargeback_reverse = "chargeback_reverse"
    chargeback_warning = "chargeback_warning"
    chargeback_warning_reverse = "chargeback_warning_reverse"
    credit_reverse = "credit_reverse"


class AdjustmentId(RootModel[Annotated[str, Field(pattern="^adj_[a-z\\d]{26}$")]]):
    root: Annotated[str, Field(pattern="^adj_[a-z\\d]{26}$")] = Field(
        ...,
        description="Unique Paddle ID for this adjustment entity, prefixed with `adj_`.",
        examples=["adj_01gya6twkp8y0tv1e19rsgst9m"],
        title="Adjustment ID",
    )


class Type(Enum):
    full = "full"
    partial = "partial"
    tax = "tax"
    proration = "proration"


class AdjustmentItemId(
    RootModel[Annotated[str, Field(pattern="^adjitm_[a-z\\d]{26}$")]]
):
    root: Annotated[str, Field(pattern="^adjitm_[a-z\\d]{26}$")] = Field(
        ...,
        description="Unique Paddle ID for this adjustment item, prefixed with `adjitm_`.",
        examples=["adjitm_01gw4rs4kex0prncwfne87ft8x"],
        title="Adjustment item ID",
    )


class AdjustmentItemTotals(BaseModel):
    subtotal: str | None = Field(
        None, description="Amount multiplied by quantity.", examples=["15000"]
    )
    tax: str | None = Field(
        None, description="Total tax on the subtotal.", examples=["1500"]
    )
    total: str | None = Field(None, description="Total after tax.", examples=["16500"])


class AdjustmentTaxMode(Enum):
    external = "external"
    internal = "internal"


class AdjustmentType(Enum):
    full = "full"
    partial = "partial"


class ApiKeyId(RootModel[Annotated[str, Field(pattern="^apikey_[a-z\\d]{26}$")]]):
    root: Annotated[str, Field(pattern="^apikey_[a-z\\d]{26}$")] = Field(
        ...,
        description="Unique Paddle ID for this API key entity, prefixed with `apikey_`.",
        examples=["apikey_01gm106t81w94gyjgsaqypkjkl"],
        title="API Key ID",
    )


class ApikeyDescription(RootModel[Annotated[str, Field(min_length=1, max_length=250)]]):
    root: Annotated[str, Field(min_length=1, max_length=250)] = Field(
        ...,
        description="Short description of this API key. Typically gives details about what the API key is used for and where it's used.",
        title="ApiKeyDescription",
    )


class ApikeyName(RootModel[Annotated[str, Field(min_length=1, max_length=150)]]):
    root: Annotated[str, Field(min_length=1, max_length=150)] = Field(
        ...,
        description="Short name of this API key. Typically unique and human-identifiable.",
        title="ApiKeyName",
    )


class ApikeySecret(
    RootModel[
        Annotated[
            str,
            Field(
                pattern="^pdl_(live|sdbx)_apikey_[a-z\\d]{26}_[a-zA-Z\\d]{22}_[a-zA-Z\\d]{3}$"
            ),
        ]
    ]
):
    root: Annotated[
        str,
        Field(
            pattern="^pdl_(live|sdbx)_apikey_[a-z\\d]{26}_[a-zA-Z\\d]{22}_[a-zA-Z\\d]{3}$"
        ),
    ] = Field(
        ...,
        description="An API key, prefixed with `pdl_` and containing `_apikey_ `.",
        title="ApiKeySecret",
    )


class ApikeySecretRedacted(
    RootModel[Annotated[str, Field(pattern="^[a-z\\d_]*\\*{4}$")]]
):
    root: Annotated[str, Field(pattern="^[a-z\\d_]*\\*{4}$")] = Field(
        ...,
        description="An obfuscated version of this API key, prefixed with `pdl_` and containing `_apikey_ `.",
        title="ApiKeySecretRedacted",
    )


class ApikeyStatus(Enum):
    active = "active"
    expired = "expired"
    revoked = "revoked"


class BusinessId(RootModel[Annotated[str, Field(pattern="^biz_[a-z\\d]{26}$")]]):
    root: Annotated[str, Field(pattern="^biz_[a-z\\d]{26}$")] = Field(
        ...,
        description="Unique Paddle ID for this business entity, prefixed with `biz_`.",
        examples=["biz_01grrebrzaee2qj2fqqhmcyzaj"],
        title="Business ID",
    )


class CardCardholderName(RootModel[str]):
    root: str = Field(
        ..., description="The name on the card used to pay.", title="Cardholder Name"
    )


class CardExpiryMonth(RootModel[float]):
    root: float = Field(
        ...,
        description="Month of the expiry date of the card used to pay.",
        examples=[12],
        title="Card Expiry Month",
    )


class CardExpiryYear(RootModel[float]):
    root: float = Field(
        ...,
        description="Year of the expiry date of the card used to pay.",
        examples=["2028"],
        title="Card Expiry Year",
    )


class CardLast4(RootModel[str]):
    root: str = Field(
        ...,
        description="Last four digits of the card used to pay.",
        examples=["4242"],
        title="Card Last Four",
    )


class CardType(Enum):
    american_express = "american_express"
    diners_club = "diners_club"
    discover = "discover"
    jcb = "jcb"
    mada = "mada"
    maestro = "maestro"
    mastercard = "mastercard"
    union_pay = "union_pay"
    unknown = "unknown"
    visa = "visa"


class CatalogType(Enum):
    custom = "custom"
    standard = "standard"


class CollectionMode(Enum):
    automatic = "automatic"
    manual = "manual"


class CountryCodeSupported(Enum):
    AD = "AD"
    AE = "AE"
    AG = "AG"
    AI = "AI"
    AL = "AL"
    AM = "AM"
    AO = "AO"
    AR = "AR"
    AS = "AS"
    AT = "AT"
    AU = "AU"
    AW = "AW"
    AX = "AX"
    AZ = "AZ"
    BA = "BA"
    BB = "BB"
    BD = "BD"
    BE = "BE"
    BF = "BF"
    BG = "BG"
    BH = "BH"
    BI = "BI"
    BJ = "BJ"
    BL = "BL"
    BM = "BM"
    BN = "BN"
    BO = "BO"
    BQ = "BQ"
    BR = "BR"
    BS = "BS"
    BT = "BT"
    BV = "BV"
    BW = "BW"
    BZ = "BZ"
    CA = "CA"
    CC = "CC"
    CG = "CG"
    CH = "CH"
    CI = "CI"
    CK = "CK"
    CL = "CL"
    CM = "CM"
    CN = "CN"
    CO = "CO"
    CR = "CR"
    CV = "CV"
    CW = "CW"
    CX = "CX"
    CY = "CY"
    CZ = "CZ"
    DE = "DE"
    DJ = "DJ"
    DK = "DK"
    DM = "DM"
    DO = "DO"
    DZ = "DZ"
    EC = "EC"
    EE = "EE"
    EG = "EG"
    EH = "EH"
    ER = "ER"
    ES = "ES"
    ET = "ET"
    FI = "FI"
    FJ = "FJ"
    FK = "FK"
    FM = "FM"
    FO = "FO"
    FR = "FR"
    GA = "GA"
    GB = "GB"
    GD = "GD"
    GE = "GE"
    GF = "GF"
    GG = "GG"
    GH = "GH"
    GI = "GI"
    GL = "GL"
    GM = "GM"
    GN = "GN"
    GP = "GP"
    GQ = "GQ"
    GR = "GR"
    GS = "GS"
    GT = "GT"
    GU = "GU"
    GW = "GW"
    GY = "GY"
    HK = "HK"
    HM = "HM"
    HN = "HN"
    HR = "HR"
    HU = "HU"
    ID = "ID"
    IE = "IE"
    IL = "IL"
    IM = "IM"
    IN = "IN"
    IO = "IO"
    IQ = "IQ"
    IS = "IS"
    IT = "IT"
    JE = "JE"
    JM = "JM"
    JO = "JO"
    JP = "JP"
    KE = "KE"
    KG = "KG"
    KH = "KH"
    KI = "KI"
    KM = "KM"
    KN = "KN"
    KR = "KR"
    KW = "KW"
    KY = "KY"
    KZ = "KZ"
    LA = "LA"
    LB = "LB"
    LC = "LC"
    LI = "LI"
    LK = "LK"
    LR = "LR"
    LS = "LS"
    LT = "LT"
    LU = "LU"
    LV = "LV"
    MA = "MA"
    MC = "MC"
    MD = "MD"
    ME = "ME"
    MF = "MF"
    MG = "MG"
    MH = "MH"
    MK = "MK"
    MN = "MN"
    MO = "MO"
    MP = "MP"
    MQ = "MQ"
    MR = "MR"
    MS = "MS"
    MT = "MT"
    MU = "MU"
    MV = "MV"
    MW = "MW"
    MX = "MX"
    MY = "MY"
    MZ = "MZ"
    NA = "NA"
    NC = "NC"
    NE = "NE"
    NF = "NF"
    NG = "NG"
    NL = "NL"
    NO = "NO"
    NP = "NP"
    NR = "NR"
    NU = "NU"
    NZ = "NZ"
    OM = "OM"
    PA = "PA"
    PE = "PE"
    PF = "PF"
    PG = "PG"
    PH = "PH"
    PK = "PK"
    PL = "PL"
    PM = "PM"
    PN = "PN"
    PR = "PR"
    PS = "PS"
    PT = "PT"
    PW = "PW"
    PY = "PY"
    QA = "QA"
    RE = "RE"
    RO = "RO"
    RS = "RS"
    RW = "RW"
    SA = "SA"
    SB = "SB"
    SC = "SC"
    SE = "SE"
    SG = "SG"
    SH = "SH"
    SI = "SI"
    SJ = "SJ"
    SK = "SK"
    SL = "SL"
    SM = "SM"
    SN = "SN"
    SR = "SR"
    ST = "ST"
    SV = "SV"
    SX = "SX"
    SZ = "SZ"
    TC = "TC"
    TD = "TD"
    TF = "TF"
    TG = "TG"
    TH = "TH"
    TJ = "TJ"
    TK = "TK"
    TL = "TL"
    TM = "TM"
    TN = "TN"
    TO = "TO"
    TR = "TR"
    TT = "TT"
    TV = "TV"
    TW = "TW"
    TZ = "TZ"
    UA = "UA"
    UG = "UG"
    UM = "UM"
    US = "US"
    UY = "UY"
    UZ = "UZ"
    VA = "VA"
    VC = "VC"
    VG = "VG"
    VI = "VI"
    VN = "VN"
    VU = "VU"
    WF = "WF"
    WS = "WS"
    XK = "XK"
    YT = "YT"
    ZA = "ZA"
    ZM = "ZM"


class CreatedAt(RootModel[AwareDatetime]):
    root: AwareDatetime = Field(
        ...,
        description="RFC 3339 datetime string of when this entity was created. Set automatically by Paddle.",
        examples=["2024-10-12T07:20:50.52Z"],
        title="Created at",
    )


class CurrencyCode(Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    AUD = "AUD"
    CAD = "CAD"
    CHF = "CHF"
    HKD = "HKD"
    SGD = "SGD"
    SEK = "SEK"
    ARS = "ARS"
    BRL = "BRL"
    CNY = "CNY"
    COP = "COP"
    CZK = "CZK"
    DKK = "DKK"
    HUF = "HUF"
    ILS = "ILS"
    INR = "INR"
    KRW = "KRW"
    MXN = "MXN"
    NOK = "NOK"
    NZD = "NZD"
    PLN = "PLN"
    RUB = "RUB"
    THB = "THB"
    TRY = "TRY"
    TWD = "TWD"
    UAH = "UAH"
    VND = "VND"
    ZAR = "ZAR"


class CurrencyCodeChargeback(Enum):
    AUD = "AUD"
    CAD = "CAD"
    EUR = "EUR"
    GBP = "GBP"
    USD = "USD"


class CurrencyCodePayout(Enum):
    AUD = "AUD"
    CAD = "CAD"
    CHF = "CHF"
    CNY = "CNY"
    CZK = "CZK"
    DKK = "DKK"
    EUR = "EUR"
    GBP = "GBP"
    HUF = "HUF"
    PLN = "PLN"
    SEK = "SEK"
    USD = "USD"
    ZAR = "ZAR"


class CustomData(BaseModel):
    model_config = ConfigDict(extra="allow")


class Type1(Enum):
    alipay = "alipay"
    apple_pay = "apple_pay"
    card = "card"
    google_pay = "google_pay"
    korea_local = "korea_local"
    paypal = "paypal"
    blik = "blik"
    kakao_pay = "kakao_pay"
    south_korea_local_card = "south_korea_local_card"
    mb_way = "mb_way"
    naver_pay = "naver_pay"
    pix = "pix"
    samsung_pay = "samsung_pay"
    upi = "upi"


class Origin(Enum):
    saved_during_purchase = "saved_during_purchase"
    subscription = "subscription"


class General(BaseModel):
    model_config = ConfigDict(extra="forbid")
    overview: str = Field(
        ...,
        description="Link to the overview page in the customer portal.",
        examples=[
            "https://customer-portal.paddle.com/cpl_01j7zbyqs3vah3aafp4jf62qaw?action=overview&token="
        ],
    )


class CustomerPortalSessionId(
    RootModel[Annotated[str, Field(pattern="^cpls_[a-z\\d]{26}$")]]
):
    root: Annotated[str, Field(pattern="^cpls_[a-z\\d]{26}$")] = Field(
        ...,
        description="Unique Paddle ID for this customer portal session entity, prefixed with `cpls_`.",
        examples=["cpls_01h4ge9r64c22exjsx0fy8b48b"],
        title="Customer Portal Session ID",
    )


class CustomerAuthToken(RootModel[str]):
    root: str = Field(
        ...,
        description="Authentication token generated by Paddle for this customer. Pass to Paddle.js when opening a checkout to let customers work with saved payment methods.",
        examples=[
            "pca_01hstrngzv6v4ard25jgvywwqq_01hsgrwf0ev6gxm74bp0gebxas_o7scuiadqtvbtspkmbwfnyrvyrq3zig6"
        ],
        title="Customer Auth Token",
    )


class CustomerBalance(BaseModel):
    available: str | None = Field(
        None, description="Total amount of credit available to use.", examples=["200"]
    )
    reserved: str | None = Field(
        None,
        description="Total amount of credit temporarily reserved for `billed` transactions.",
        examples=["400"],
    )
    used: str | None = Field(
        None, description="Total amount of credit used.", examples=["600"]
    )


class CustomerId(RootModel[Annotated[str, Field(pattern="^ctm_[a-z\\d]{26}$")]]):
    root: Annotated[str, Field(pattern="^ctm_[a-z\\d]{26}$")] = Field(
        ...,
        description="Unique Paddle ID for this customer entity, prefixed with `ctm_`.",
        examples=["ctm_01grnn4zta5a1mf02jjze7y2ys"],
        title="Customer ID",
    )


class Type2(Enum):
    flat = "flat"
    flat_per_seat = "flat_per_seat"
    percentage = "percentage"


class RestrictToItem(
    RootModel[Annotated[str, Field(pattern="^(pri|pro)_[a-z\\d]{26}$")]]
):
    root: Annotated[str, Field(pattern="^(pri|pro)_[a-z\\d]{26}$")]


class DiscountCode(
    RootModel[
        Annotated[
            str, Field(pattern="^[a-zA-Z0-9]{1,32}$", min_length=1, max_length=32)
        ]
    ]
):
    root: Annotated[
        str, Field(pattern="^[a-zA-Z0-9]{1,32}$", min_length=1, max_length=32)
    ] = Field(
        ...,
        description="Unique code that customers can use to apply this discount at checkout. Use letters and numbers only, up to 32 characters. Not case-sensitive.",
        title="Discount code",
    )


class DiscountId(RootModel[Annotated[str, Field(pattern="^dsc_[a-z\\d]{26}$")]]):
    root: Annotated[str, Field(pattern="^dsc_[a-z\\d]{26}$")] = Field(
        ...,
        description="Unique Paddle ID for this discount, prefixed with `dsc_`.",
        examples=["dsc_01gv5kpg05xp104ek2fmgjwttf"],
        title="Discount ID",
    )


class DiscountMode(Enum):
    standard = "standard"
    custom = "custom"


class DocumentNumber(RootModel[str]):
    root: str = Field(
        ...,
        description="Document number that is automatically generated by Paddle.",
        examples=["123-45678"],
    )


class Interval(Enum):
    day = "day"
    week = "week"
    month = "month"
    year = "year"


class Duration(BaseModel):
    interval: Interval = Field(..., description="Unit of time.")
    frequency: Annotated[int, Field(ge=1)] = Field(..., description="Amount of time.")


class EffectiveFrom(Enum):
    next_billing_period = "next_billing_period"
    immediately = "immediately"


class EffectiveFromNullable(Enum):
    next_billing_period = "next_billing_period"
    immediately = "immediately"
    NoneType_None = None


class Email(RootModel[EmailStr]):
    root: EmailStr = Field(
        ...,
        description="Email address for this entity.",
        examples=["test@paddle.com"],
        title="Email address",
    )


class EmptyString(RootModel[Annotated[str, Field(min_length=0, max_length=0)]]):
    root: Annotated[str, Field(min_length=0, max_length=0)] = Field(
        ..., title="Empty String"
    )


class Type4(Enum):
    request_error = "request_error"
    api_error = "api_error"


class Error2(BaseModel):
    model_config = ConfigDict(extra="forbid")
    field: str | None = Field(
        None,
        description="Field where validation error occurred.",
        examples=["name", "image_url"],
    )
    message: str | None = Field(
        None,
        description="Information about how the field failed validation.",
        examples=[
            "max length of 200 exceeded, provided value length 220",
            "must be a valid image",
        ],
    )


class Error1(BaseModel):
    type: Type4 = Field(..., description="Type of error encountered.")
    code: str = Field(
        ...,
        description="Short snake case string that describes this error. Use to search the error reference.",
        examples=["not_found"],
    )
    detail: str = Field(
        ...,
        description="Some information about what went wrong as a human-readable string.",
        examples=["Entity pro_01gsz97mq9pa4fkyy0wqenepkz not found"],
    )
    documentation_url: AnyUrl = Field(
        ...,
        description="Link to a page in the error reference for this specific error.",
        examples=["https://developer.paddle.com/errors/shared/not_found"],
    )
    errors: list[Error2] | None = Field(
        None,
        description="List of validation errors. Only returned when there's a validation error.",
    )


class ErrorCode(Enum):
    already_canceled = "already_canceled"
    already_refunded = "already_refunded"
    authentication_failed = "authentication_failed"
    blocked_card = "blocked_card"
    canceled = "canceled"
    declined = "declined"
    declined_not_retryable = "declined_not_retryable"
    expired_card = "expired_card"
    fraud = "fraud"
    invalid_amount = "invalid_amount"
    invalid_payment_details = "invalid_payment_details"
    issuer_unavailable = "issuer_unavailable"
    not_enough_balance = "not_enough_balance"
    preferred_network_not_supported = "preferred_network_not_supported"
    psp_error = "psp_error"
    redacted_payment_method = "redacted_payment_method"
    system_error = "system_error"
    transaction_not_permitted = "transaction_not_permitted"
    unknown = "unknown"


class EventId(RootModel[Annotated[str, Field(pattern="^evt_[a-z\\d]{26}$")]]):
    root: Annotated[str, Field(pattern="^evt_[a-z\\d]{26}$")] = Field(
        ...,
        description="Unique Paddle ID for this event, prefixed with `evt_`.",
        examples=["evt_01gks14ge726w50ch2tmaw2a1x"],
        title="Event ID",
    )


class EventTypeName(Enum):
    address_created = "address.created"
    address_imported = "address.imported"
    address_updated = "address.updated"
    adjustment_created = "adjustment.created"
    adjustment_updated = "adjustment.updated"
    api_key_created = "api_key.created"
    api_key_expired = "api_key.expired"
    api_key_expiring = "api_key.expiring"
    api_key_revoked = "api_key.revoked"
    api_key_updated = "api_key.updated"
    business_created = "business.created"
    business_imported = "business.imported"
    business_updated = "business.updated"
    customer_created = "customer.created"
    customer_imported = "customer.imported"
    customer_updated = "customer.updated"
    discount_created = "discount.created"
    discount_imported = "discount.imported"
    discount_updated = "discount.updated"
    payment_method_saved = "payment_method.saved"
    payment_method_deleted = "payment_method.deleted"
    payout_created = "payout.created"
    payout_paid = "payout.paid"
    price_created = "price.created"
    price_imported = "price.imported"
    price_updated = "price.updated"
    product_created = "product.created"
    product_imported = "product.imported"
    product_updated = "product.updated"
    report_created = "report.created"
    report_updated = "report.updated"
    subscription_activated = "subscription.activated"
    subscription_canceled = "subscription.canceled"
    subscription_created = "subscription.created"
    subscription_imported = "subscription.imported"
    subscription_past_due = "subscription.past_due"
    subscription_paused = "subscription.paused"
    subscription_resumed = "subscription.resumed"
    subscription_trialing = "subscription.trialing"
    subscription_updated = "subscription.updated"
    transaction_billed = "transaction.billed"
    transaction_canceled = "transaction.canceled"
    transaction_completed = "transaction.completed"
    transaction_created = "transaction.created"
    transaction_paid = "transaction.paid"
    transaction_past_due = "transaction.past_due"
    transaction_payment_failed = "transaction.payment_failed"
    transaction_ready = "transaction.ready"
    transaction_revised = "transaction.revised"
    transaction_updated = "transaction.updated"


class ExternalId(RootModel[Annotated[str, Field(min_length=1, max_length=200)]]):
    root: Annotated[str, Field(min_length=1, max_length=200)] = Field(
        ...,
        description="Reference or identifier for this entity from the provider where it was imported from.",
        examples=["9b95b0b8-e10f-441a-862e-1936a6d818ab"],
        title="External ID",
    )


class ImageUrl(RootModel[AnyUrl]):
    root: AnyUrl = Field(..., description="A URL to an image.", title="Image Url")


class Status1(Enum):
    active = "active"
    inactive = "inactive"
    trialing = "trialing"


class Type5(Enum):
    bc = "bc"
    citi = "citi"
    hana = "hana"
    hyundai = "hyundai"
    jeju = "jeju"
    jeonbuk = "jeonbuk"
    kakaobank = "kakaobank"
    kakaopay = "kakaopay"
    kbank = "kbank"
    kdbbank = "kdbbank"
    kookmin = "kookmin"
    kwangju = "kwangju"
    lotte = "lotte"
    mg = "mg"
    naverpaycard = "naverpaycard"
    naverpaypoint = "naverpaypoint"
    nh = "nh"
    payco = "payco"
    post = "post"
    samsung = "samsung"
    samsungpay = "samsungpay"
    savingsbank = "savingsbank"
    shinhan = "shinhan"
    shinhyup = "shinhyup"
    suhyup = "suhyup"
    tossbank = "tossbank"
    unknown = "unknown"
    woori = "woori"


class KoreaLocalUnderlyingDetails(BaseModel):
    type: Type5 | None = None


class KoreaLocalUnderlyingPaymentMethodType(Enum):
    bc = "bc"
    citi = "citi"
    hana = "hana"
    hyundai = "hyundai"
    jeju = "jeju"
    jeonbuk = "jeonbuk"
    kakaobank = "kakaobank"
    kakaopay = "kakaopay"
    kbank = "kbank"
    kdbbank = "kdbbank"
    kookmin = "kookmin"
    kwangju = "kwangju"
    lotte = "lotte"
    mg = "mg"
    naverpaycard = "naverpaycard"
    naverpaypoint = "naverpaypoint"
    nh = "nh"
    payco = "payco"
    post = "post"
    samsung = "samsung"
    samsungpay = "samsungpay"
    savingsbank = "savingsbank"
    shinhan = "shinhan"
    shinhyup = "shinhyup"
    suhyup = "suhyup"
    tossbank = "tossbank"
    unknown = "unknown"
    woori = "woori"


class MigrationProviderPublic(Enum):
    paddle_classic = "paddle_classic"


class Money(BaseModel):
    amount: str = Field(
        ...,
        description="Amount in the lowest denomination for the currency, e.g. 10 USD = 1000 (cents). Although represented as a string, this value must be a valid integer.",
    )
    currency_code: CurrencyCode


class Name(RootModel[Annotated[str, Field(max_length=1024)]]):
    root: Annotated[str, Field(max_length=1024)] = Field(
        ..., description="Full name.", title="Name"
    )


class Origin1(Enum):
    event = "event"
    replay = "replay"


class NotificationId(RootModel[Annotated[str, Field(pattern="^ntf_[a-z\\d]{26}$")]]):
    root: Annotated[str, Field(pattern="^ntf_[a-z\\d]{26}$")] = Field(
        ...,
        description="Unique Paddle ID for this notification, prefixed with `ntf_`.",
        examples=["ntf_01ghbkd0frb9k95cnhwd1bxpvk"],
        title="Notification ID",
    )


class NotificationLogId(
    RootModel[Annotated[str, Field(pattern="^ntflog_[a-z\\d]{26}$")]]
):
    root: Annotated[str, Field(pattern="^ntflog_[a-z\\d]{26}$")] = Field(
        ...,
        description="Unique Paddle ID for this notification log, prefixed with `ntflog_`.",
        examples=["ntflog_01gyfq570sy1nsv2123sbs68kv"],
        title="Notification log ID",
    )


class Type6(Enum):
    email = "email"
    url = "url"


class TrafficSource(Enum):
    platform = "platform"
    simulation = "simulation"
    all = "all"


class NotificationSettingUpdate(BaseModel):
    description: Annotated[str, Field(min_length=1, max_length=500)] | None = Field(
        None,
        description="Short description for this notification destination. Shown in the Paddle Dashboard.",
    )
    destination: Annotated[str, Field(min_length=1, max_length=2048)] | None = Field(
        None, description="Webhook endpoint URL or email address."
    )
    active: bool | None = Field(
        True,
        description="Whether Paddle should try to deliver events to this notification destination.",
    )
    api_version: Annotated[int, Field(ge=1)] | None = Field(
        None,
        description="API version that returned objects for events should conform to. Must be a valid version of the Paddle API. Can't be a version older than your account default. Defaults to your account default if omitted.",
    )
    include_sensitive_fields: bool | None = Field(
        False,
        description="Whether potentially sensitive fields should be sent to this notification destination.",
    )
    subscribed_events: list[EventTypeName] | None = Field(
        None,
        description="Subscribed events for this notification destination. When creating or updating a notification destination, pass an array of event type names only. Paddle returns the complete event type object.",
    )
    traffic_source: TrafficSource | None = Field(
        None,
        description="Whether Paddle should deliver real platform events, simulation events or both to this notification destination.",
    )


class NotificationSettingId(
    RootModel[Annotated[str, Field(pattern="^ntfset_[a-z\\d]{26}$")]]
):
    root: Annotated[str, Field(pattern="^ntfset_[a-z\\d]{26}$")] = Field(
        ...,
        description="Unique Paddle ID for this notification setting, prefixed with `ntfset_`.",
        examples=["ntfset_01gt21c5pdx9q1e4mh1xrsjjn6"],
        title="Notification setting ID",
    )


class OperatorEnum(Enum):
    lt = "lt"
    gte = "gte"


class Operator(RootModel[OperatorEnum | None]):
    root: OperatorEnum | None = Field(
        None,
        description="Operator to use when filtering.",
        examples=["lt"],
        title="FilterOperator",
    )


class OriginTransaction1(Enum):
    api = "api"
    subscription_charge = "subscription_charge"
    subscription_payment_method_change = "subscription_payment_method_change"
    subscription_recurring = "subscription_recurring"
    subscription_update = "subscription_update"
    web = "web"


class OriginTransaction(RootModel[OriginTransaction1]):
    root: OriginTransaction1 = Field(
        ...,
        description="Describes how this transaction was created.",
        title="Transaction origin",
    )


class PaddleId(RootModel[Annotated[str, Field(pattern="^[a-z]{3,10}_[a-z\\d]{26}$")]]):
    root: Annotated[str, Field(pattern="^[a-z]{3,10}_[a-z\\d]{26}$")] = Field(
        ...,
        description="Unique Paddle ID for this entity.",
        examples=[
            "add_01gm302t81w94gyjpjpqypkzkf",
            "adj_01gya6twkp8y0tv1e19rsgst9m",
            "adjitm_01gw4rs4kex0prncwfne87ft8x",
            "biz_01grrebrzaee2qj2fqqhmcyzaj",
            "ctm_01grnn4zta5a1mf02jjze7y2ys",
            "dsc_01gv5kpg05xp104ek2fmgjwttf",
            "evt_01gks14ge726w50ch2tmaw2a1x",
            "ntf_01ghbkd0frb9k95cnhwd1bxpvk",
            "ntflog_01gyfq570sy1nsv2123sbs68kv",
            "ntfset_01gt21c5pdx9q1e4mh1xrsjjn6",
            "pri_01gsz8z1q1n00f12qt82y31smh",
            "pro_01gsz97mq9pa4fkyy0wqenepkz",
            "rep_01h9apkx1d320kpvvfyezr96k0",
            "sub_01h04vsc0qhwtsbsxh3422wjs4",
            "txn_01h04vsbhqc62t8hmd4z3b578c",
            "txnitm_01gm302t81w94gyjpjpqypkzkf",
        ],
        title="PaddleID",
    )


class Pagination(BaseModel):
    per_page: int = Field(
        ...,
        description="Number of entities per page for this response. May differ from the number requested if the requested number is greater than the maximum.",
    )
    next: AnyUrl = Field(
        ...,
        description="URL containing the query parameters of the original request, along with the `after` parameter that marks the starting point of the next page. Always returned, even if `has_more` is `false`.",
    )
    has_more: bool = Field(..., description="Whether this response has another page.")
    estimated_total: int | None = Field(
        None,
        description="Estimated number of entities for this response.",
        examples=[999],
    )


class PaymentMethodId(
    RootModel[Annotated[str, Field(pattern="^paymtd_[a-z\\d]{26}$")]]
):
    root: Annotated[str, Field(pattern="^paymtd_[a-z\\d]{26}$")] = Field(
        ...,
        description="Unique Paddle ID for this payment method entity, prefixed with `paymtd_`.",
        examples=["paymtd_01hkm9xwqpbbpr1ksmvg3sx3v1"],
        title="Payment Method ID",
    )


class PaymentMethodType(Enum):
    alipay = "alipay"
    apple_pay = "apple_pay"
    bancontact = "bancontact"
    card = "card"
    google_pay = "google_pay"
    ideal = "ideal"
    korea_local = "korea_local"
    paypal = "paypal"
    blik = "blik"
    kakao_pay = "kakao_pay"
    south_korea_local_card = "south_korea_local_card"
    mb_way = "mb_way"
    naver_pay = "naver_pay"
    pix = "pix"
    samsung_pay = "samsung_pay"
    upi = "upi"


class Paypal(BaseModel):
    email: str | None = Field(
        None,
        description="Email address associated with the PayPal account.",
        examples=["john.doe@example.com"],
    )
    reference: str | None = Field(None, description="PayPal payment method identifier.")


class Permission(Enum):
    address_read = "address.read"
    address_write = "address.write"
    adjustment_read = "adjustment.read"
    adjustment_write = "adjustment.write"
    business_read = "business.read"
    business_write = "business.write"
    customer_read = "customer.read"
    customer_write = "customer.write"
    customer_auth_token_write = "customer_auth_token.write"
    customer_portal_session_write = "customer_portal_session.write"
    discount_read = "discount.read"
    discount_write = "discount.write"
    notification_read = "notification.read"
    notification_write = "notification.write"
    notification_setting_read = "notification_setting.read"
    notification_setting_write = "notification_setting.write"
    notification_simulation_read = "notification_simulation.read"
    notification_simulation_write = "notification_simulation.write"
    payment_method_read = "payment_method.read"
    payment_method_write = "payment_method.write"
    price_read = "price.read"
    price_write = "price.write"
    product_read = "product.read"
    product_write = "product.write"
    report_read = "report.read"
    report_write = "report.write"
    subscription_read = "subscription.read"
    subscription_write = "subscription.write"
    transaction_read = "transaction.read"
    transaction_write = "transaction.write"


class PriceId(RootModel[Annotated[str, Field(pattern="^pri_[a-z\\d]{26}$")]]):
    root: Annotated[str, Field(pattern="^pri_[a-z\\d]{26}$")] = Field(
        ...,
        description="Unique Paddle ID for this price, prefixed with `pri_`.",
        examples=["pri_01gsz8z1q1n00f12qt82y31smh"],
        title="Price ID",
    )


class PriceName(RootModel[Annotated[str, Field(min_length=1, max_length=150)] | None]):
    root: Annotated[str, Field(min_length=1, max_length=150)] | None = Field(
        ...,
        description="Name of this price, shown to customers at checkout and on invoices. Typically describes how often the related product bills.",
        title="Price Name",
    )


class PriceQuantity(BaseModel):
    minimum: Annotated[int, Field(ge=1, le=999999999)] = Field(
        ...,
        description="Minimum quantity of the product related to this price that can be bought. Required if `maximum` set.",
        examples=[1],
    )
    maximum: Annotated[int, Field(ge=1, le=999999999)] = Field(
        ...,
        description="Maximum quantity of the product related to this price that can be bought. Required if `minimum` set. Must be greater than or equal to the `minimum` value.",
        examples=[100],
    )


class PriceTrialDuration(BaseModel):
    interval: Interval = Field(..., description="Unit of time.")
    frequency: Annotated[int, Field(ge=1)] = Field(..., description="Amount of time.")


class ProductId(RootModel[Annotated[str, Field(pattern="^pro_[a-z\\d]{26}$")]]):
    root: Annotated[str, Field(pattern="^pro_[a-z\\d]{26}$")] = Field(
        ...,
        description="Unique Paddle ID for this product, prefixed with `pro_`.",
        examples=["pro_01gsz97mq9pa4fkyy0wqenepkz"],
        title="Product ID",
    )


class ProductName(RootModel[Annotated[str, Field(min_length=1, max_length=200)]]):
    root: Annotated[str, Field(min_length=1, max_length=200)] = Field(
        ..., description="Name of this product.", title="Product Name"
    )


class Type8(Enum):
    balance = "balance"


class Type9(Enum):
    discounts = "discounts"


class Type10(Enum):
    products_prices = "products_prices"


class Name1(Enum):
    action = "action"
    currency_code = "currency_code"
    status = "status"
    updated_at = "updated_at"


class ReportFilterAdjustment(BaseModel):
    name: Name1 | None = Field(
        None,
        description="Field name to filter by.",
        title="AdjustmentsReportFilterName",
    )
    operator: Operator | None = Field(
        None,
        description="Operator to use when filtering. Valid when filtering by `updated_at`, `null` otherwise.",
    )
    value: list[Any] | str | None = Field(
        None,
        description="Value to filter by. Check the allowed values descriptions for the `name` field to see valid values for a field.",
    )


class ReportFilterAdjustments(RootModel[list[ReportFilterAdjustment]]):
    root: list[ReportFilterAdjustment] = Field(
        ...,
        description="List of filters applied to this report.",
        max_length=10,
        title="AdjustmentsReportFilters",
    )


class Name2(Enum):
    updated_at = "updated_at"


class ReportFilterBalanceItem(BaseModel):
    name: Name2 | None = Field(
        None, description="Field name to filter by.", title="BalanceReportFilterName"
    )
    operator: Operator | None = Field(
        None,
        description="Operator to use when filtering. Valid when filtering by `updated_at`, `null` otherwise.",
    )
    value: list[Any] | str | None = Field(
        None,
        description="Value to filter by. Check the allowed values descriptions for the `name` field to see valid values for a field.",
    )


class ReportFilterBalance(RootModel[list[ReportFilterBalanceItem]]):
    root: list[ReportFilterBalanceItem] = Field(
        ...,
        description="List of filters applied to this report.",
        max_length=10,
        title="BalanceReportFilters",
    )


class Name3(Enum):
    type = "type"
    status = "status"
    updated_at = "updated_at"


class ReportFilterDiscount(BaseModel):
    name: Name3 | None = Field(
        None, description="Field name to filter by.", title="DiscountsReportFilterName"
    )
    operator: Operator | None = Field(
        None,
        description="Operator to use when filtering. Valid when filtering by `updated_at`, `null` otherwise.",
    )
    value: list[Any] | str | None = Field(
        None,
        description="Value to filter by. Check the allowed values descriptions for the `name` field to see valid values for a field.",
    )


class ReportFilterDiscounts(RootModel[list[ReportFilterDiscount]]):
    root: list[ReportFilterDiscount] = Field(
        ...,
        description="List of filters applied to this report.",
        max_length=10,
        title="DiscountsReportFilters",
    )


class Name4(Enum):
    product_status = "product_status"
    price_status = "price_status"
    product_type = "product_type"
    price_type = "price_type"
    product_updated_at = "product_updated_at"
    price_updated_at = "price_updated_at"


class ReportFilterProductsPrice(BaseModel):
    name: Name4 | None = Field(
        None,
        description="Field name to filter by.",
        title="ProductPricesReportFilterName",
    )
    operator: Operator | None = Field(
        None,
        description="Operator to use when filtering. Valid when filtering by `updated_at`, `null` otherwise.",
    )
    value: list[Any] | str | None = Field(None, description="Value to filter by.")


class ReportFilterProductsPrices(RootModel[list[ReportFilterProductsPrice]]):
    root: list[ReportFilterProductsPrice] = Field(
        ...,
        description="List of filters applied to this report.",
        max_length=10,
        title="ProductPricesReportFilters",
    )


class Name5(Enum):
    collection_mode = "collection_mode"
    currency_code = "currency_code"
    origin = "origin"
    status = "status"
    updated_at = "updated_at"


class ReportFilterTransaction(BaseModel):
    name: Name5 | None = Field(
        None,
        description="Field name to filter by.",
        title="TransactionsReportFilterName",
    )
    operator: Operator | None = Field(
        None,
        description="Operator to use when filtering. Valid when filtering by `updated_at`, `null` otherwise.",
    )
    value: list[Any] | str | None = Field(
        None,
        description="Value to filter by. Check the allowed values descriptions for the `name` field to see valid values for a field.",
    )


class ReportFilterTransactions(RootModel[list[ReportFilterTransaction]]):
    root: list[ReportFilterTransaction] = Field(
        ...,
        description="List of filters applied to this report.",
        max_length=10,
        title="TransactionsReportFilters",
    )


class ReportTypeAdjustments(Enum):
    adjustments = "adjustments"
    adjustment_line_items = "adjustment_line_items"


class ReportTypeTransactions(Enum):
    transactions = "transactions"
    transaction_line_items = "transaction_line_items"


class RequestId(RootModel[str]):
    root: str = Field(
        ...,
        description="Unique ID for the request relating to this response. Provide this when contacting Paddle support about a specific request.",
        examples=["b15ec92e-8688-40d4-a04d-f44cbec93355"],
        title="Request ID",
    )


class SavedAt(RootModel[AwareDatetime]):
    root: AwareDatetime = Field(
        ...,
        description="RFC 3339 datetime string of when this entity was saved. Set automatically by Paddle.",
        examples=["2024-10-12T07:20:50.52Z"],
        title="Saved at",
    )


class SimulationConfigEntitiesSubscriptionCreationNoPrices(BaseModel):
    model_config = ConfigDict(extra="forbid")
    customer_id: CustomerId | None = Field(
        None,
        description="Paddle ID of a customer. Adds customer details to webhook payloads.",
    )
    address_id: AddressId | None = Field(
        None,
        description="Paddle ID of an address. Adds address details to webhook payloads. Requires `customer_id`.",
    )
    business_id: BusinessId | None = Field(
        None,
        description="Paddle ID of a business. Adds business details to webhook payloads. Requires `customer_id`.",
    )
    payment_method_id: PaymentMethodId | None = Field(
        None,
        description="Paddle ID of a payment method. Adds payment method details to webhook payloads. Requires `customer_id`.",
    )
    discount_id: DiscountId | None = Field(
        None,
        description="Paddle ID of an existing discount to apply to the simulated subscription.",
    )
    items: None = Field(
        None,
        description="Items for the simulated subscription. Only existing products and prices can be simulated. Non-catalog items are not supported",
    )
    transaction_id: None = Field(
        None,
        description="Paddle ID of an existing transaction. Simulates passing a transaction ID to Paddle.js.",
    )


class SimulationConfigEntitiesSubscriptionCreationTransaction(BaseModel):
    model_config = ConfigDict(extra="forbid")
    customer_id: CustomerId | None = Field(
        None,
        description="Paddle ID of a customer. Adds customer details to webhook payloads.",
    )
    address_id: AddressId | None = Field(
        None,
        description="Paddle ID of an address. Adds address details to webhook payloads. Requires `customer_id`.",
    )
    business_id: BusinessId | None = Field(
        None,
        description="Paddle ID of a business. Adds business details to webhook payloads. Requires `customer_id`.",
    )
    payment_method_id: PaymentMethodId | None = Field(
        None,
        description="Paddle ID of a payment method. Adds payment method details to webhook payloads. Requires `customer_id`.",
    )
    discount_id: DiscountId | None = Field(
        None,
        description="Paddle ID of a discount. Adds discount details (including price calculations) to webhook payloads. Requires `items` or `transaction_id` for the discount to be applied.",
    )
    transaction_id: Annotated[str, Field(pattern="^txn_[a-z\\d]{26}$")] | None = Field(
        None,
        description="Paddle ID of a transaction. Bases the subscription from this transaction.",
    )
    items: None = Field(
        None,
        description="Items to include on the simulated subscription. Only existing products and prices can be simulated. Non-catalog items aren't supported. At least one recurring price must be provided.",
    )


class PaymentOutcome(Enum):
    success = "success"
    recovered_existing_payment_method = "recovered_existing_payment_method"
    recovered_updated_payment_method = "recovered_updated_payment_method"
    failed = "failed"


class DunningExhaustedAction(Enum):
    subscription_paused = "subscription_paused"
    subscription_canceled = "subscription_canceled"


class SimulationConfigOptionsPayment(BaseModel):
    model_config = ConfigDict(extra="forbid")
    payment_outcome: PaymentOutcome | None = Field(
        "success",
        description="Determines which webhooks are sent based on the outcome of the payment. If omitted, defaults to `success`.",
    )
    dunning_exhausted_action: DunningExhaustedAction | None = Field(
        None,
        description="Determines which webhooks are sent based on what happens to the subscription when payment recovery attempts are exhausted. Only applies when `payment_outcome` is `failed`. If omitted, defaults to `null`.",
    )


class PaymentOutcome1(Enum):
    failed = "failed"


class SimulationConfigOptionsPaymentFailed(BaseModel):
    model_config = ConfigDict(extra="forbid")
    payment_outcome: PaymentOutcome1 | None = Field(
        None,
        description="Determines which webhooks are sent based on the outcome of the payment. If omitted, defaults to `success`.",
    )
    dunning_exhausted_action: DunningExhaustedAction | None = Field(
        "subscription_canceled",
        description="Determines which webhooks are sent based on what happens to the subscription when payment recovery attempts are exhausted. If omitted, defaults to `subscription_canceled`.",
    )


class PaymentOutcome2(Enum):
    recovered_existing_payment_method = "recovered_existing_payment_method"


class SimulationConfigOptionsPaymentRecoveredExisting(BaseModel):
    model_config = ConfigDict(extra="forbid")
    payment_outcome: PaymentOutcome2 | None = Field(
        None,
        description="Determines which webhooks are sent based on the outcome of the payment. If omitted, defaults to `success`.",
    )
    dunning_exhausted_action: None = Field(
        None,
        description="Determines which webhooks are sent based on what happens to the subscription when payment recovery attempts are exhausted. Only applies when `payment_outcome` is `failed`. If omitted, defaults to `null`.",
    )


class PaymentOutcome3(Enum):
    recovered_updated_payment_method = "recovered_updated_payment_method"


class SimulationConfigOptionsPaymentRecoveredUpdated(BaseModel):
    model_config = ConfigDict(extra="forbid")
    payment_outcome: PaymentOutcome3 | None = Field(
        None,
        description="Determines which webhooks are sent based on the outcome of the payment. If omitted, defaults to `success`.",
    )
    dunning_exhausted_action: None = Field(
        None,
        description="Determines which webhooks are sent based on what happens to the subscription when payment recovery attempts are exhausted. Only applies when `payment_outcome` is `failed`. If omitted, defaults to `null`.",
    )


class PaymentOutcome4(Enum):
    success = "success"


class SimulationConfigOptionsPaymentSuccess(BaseModel):
    model_config = ConfigDict(extra="forbid")
    payment_outcome: PaymentOutcome4 | None = Field(
        "success",
        description="Determines which webhooks are sent based on the outcome of the payment. If omitted, defaults to `success`.",
    )
    dunning_exhausted_action: None = Field(
        None,
        description="Determines which webhooks are sent based on what happens to the subscription when payment recovery attempts are exhausted. Only applies when `payment_outcome` is `failed`. If omitted, defaults to `null`.",
    )


class Options(BaseModel):
    model_config = ConfigDict(extra="forbid")
    effective_from: EffectiveFrom | None = Field(
        "immediately",
        description="Determines which webhooks are sent based on when the subscription is paused or canceled. If omitted, defaults to `immediately`.",
    )
    has_past_due_transaction: bool | None = Field(
        False,
        description="Whether a simulated subscription has a past due transaction (`true`) or not (`false`), which determines whether events occur for canceling past due transactions. If omitted, defaults to `false`.",
    )


class Options1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    effective_from: EffectiveFrom | None = Field(
        "immediately",
        description="Determines which webhooks are sent based on when the subscription is paused or canceled. If omitted, defaults to `immediately`.",
    )
    has_past_due_transaction: bool | None = Field(
        False,
        description="Whether a simulated subscription has a past due transaction (`true`) or not (`false`), which determines whether events occur for canceling past due transactions. If omitted, defaults to `false`.",
    )


class CustomerSimulatedAs(Enum):
    new = "new"
    existing_email_matched = "existing_email_matched"
    existing_details_prefilled = "existing_details_prefilled"


class BusinessSimulatedAs(Enum):
    not_provided = "not_provided"
    new = "new"
    existing_details_prefilled = "existing_details_prefilled"


class DiscountSimulatedAs(Enum):
    not_provided = "not_provided"
    prefilled = "prefilled"
    entered_by_customer = "entered_by_customer"


class SimulationConfigSubscriptionCreationOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")
    customer_simulated_as: CustomerSimulatedAs | None = Field(
        "new",
        description="Determines which webhooks are sent based on whether a new or existing customer subscribes, and how their details are entered if they're an existing customer. If omitted, defaults to `new`.",
    )
    business_simulated_as: BusinessSimulatedAs | None = Field(
        "not_provided",
        description="Determines which webhooks are sent based on whether a new, existing, or no business was provided. If omitted, defaults to `not_provided`.",
    )
    discount_simulated_as: DiscountSimulatedAs | None = Field(
        "not_provided",
        description="Determines which webhooks are sent based on whether a discount is used and how it's entered. If omitted, defaults to `none`.",
    )


class Options2(BaseModel):
    model_config = ConfigDict(extra="forbid")
    effective_from: EffectiveFrom | None = Field(
        "immediately",
        description="Determines which webhooks are sent based on when the subscription is paused or canceled. If omitted, defaults to `immediately`.",
    )
    has_past_due_transaction: bool | None = Field(
        False,
        description="Whether a simulated subscription has a past due transaction (`true`) or not (`false`), which determines whether events occur for canceling past due transactions. If omitted, defaults to `false`.",
    )


class Options3(BaseModel):
    model_config = ConfigDict(extra="forbid")
    effective_from: EffectiveFrom | None = Field(
        "immediately",
        description="Determines which webhooks are sent based on when the subscription is paused or canceled. If omitted, defaults to `immediately`.",
    )
    has_past_due_transaction: bool | None = Field(
        False,
        description="Whether a simulated subscription has a past due transaction (`true`) or not (`false`), which determines whether events occur for canceling past due transactions. If omitted, defaults to `false`.",
    )


class Request(BaseModel):
    body: str | None = Field(
        None,
        description="Request body sent by Paddle.",
        title="SimulationEventRequestBody",
    )


class Response(BaseModel):
    body: str | None = Field(
        None,
        description="Response body sent by the responding server. May be empty for success responses.",
        title="SimulationEventResponseBody",
    )
    status_code: float | None = Field(
        None,
        description="HTTP status code sent by the responding server.",
        title="SimulationEventResponseStatus",
    )


class SimulationStandardEventsCreate(BaseModel):
    notification_setting_id: NotificationSettingId = Field(
        ...,
        description="Paddle ID of the notification setting where this simulation is sent, prefixed with `ntfset_`.",
    )
    name: str = Field(..., description="Name of this simulation.")
    type: EventTypeName = Field(
        ...,
        description="Single event sent for this simulation, in the format `entity.event_type`.",
    )
    payload: dict[str, Any] | None = Field(
        None,
        description="Simulation payload. Pass a JSON object that matches the schema for an event type to simulate a custom payload. If omitted, Paddle populates with a demo example.",
    )


class SimulationEventId(
    RootModel[Annotated[str, Field(pattern="^ntfsimevt_[a-z\\d]{26}$")]]
):
    root: Annotated[str, Field(pattern="^ntfsimevt_[a-z\\d]{26}$")] = Field(
        ...,
        description="Unique Paddle ID for this simulation event, prefixed with `ntfsimevt_`.",
        examples=["ntfsimevt_01hvg8ykjrcdr4jvv9rqcbkhfa"],
        title="Simulation Event ID",
    )


class SimulationEventStatus(Enum):
    pending = "pending"
    success = "success"
    failed = "failed"
    aborted = "aborted"


class SimulationId(RootModel[Annotated[str, Field(pattern="^ntfsim_[a-z\\d]{26}$")]]):
    root: Annotated[str, Field(pattern="^ntfsim_[a-z\\d]{26}$")] = Field(
        ...,
        description="Unique Paddle ID for this simulation, prefixed with `ntfsim_`.",
        examples=["ntfsim_01ghbkd0frb9k95cnhwd1bxpvk"],
        title="Simulation ID",
    )


class SimulationRunId(
    RootModel[Annotated[str, Field(pattern="^ntfsimrun_[a-z\\d]{26}$")]]
):
    root: Annotated[str, Field(pattern="^ntfsimrun_[a-z\\d]{26}$")] = Field(
        ...,
        description="Unique Paddle ID for this simulation run, prefixed with `ntfsimrun_`.",
        examples=["ntfsimrun_01ghbkd0frb9k95cnhwd1bxpvk"],
        title="Simulation Run ID",
    )


class SimulationRunStatus(Enum):
    pending = "pending"
    completed = "completed"
    canceled = "canceled"


class SimulationScenarioEventsType(Enum):
    subscription_creation = "subscription_creation"
    subscription_renewal = "subscription_renewal"
    subscription_pause = "subscription_pause"
    subscription_resume = "subscription_resume"
    subscription_cancellation = "subscription_cancellation"


class Type11(Enum):
    single_event = "single_event"
    scenario = "scenario"


class SimulationType(BaseModel):
    name: str | None = Field(
        None,
        description="Type of simulation sent by Paddle. Single event simulations are in the format `entity.event_type`; scenario simulations are in `snake_case`.",
        examples=["customer.created", "subscription_creation"],
    )
    label: str | None = Field(
        None,
        description="Descriptive label for this simulation type. Typically gives more context about a scenario. Single event simulations are in the format `entity.event_type`.",
        examples=["customer.created", "Subscription created from a checkout"],
    )
    description: str | None = Field(
        None,
        description="Short description of this simulation type.",
        examples=[
            "`subscription.created` events occur when a subscription is created."
        ],
    )
    group: str | None = Field(
        None,
        description="Group for this simulation type. Typically the entity that this event relates to.",
        examples=["Subscriptions"],
    )
    type: Type11 | None = Field(
        None,
        description="Type of simulation.",
        examples=["single_event", "scenario"],
        title="Simulation kind",
    )
    events: list[EventTypeName] | None = Field(
        None, description="List of events that will be sent for this simulation type."
    )


class Status(Enum):
    active = "active"
    archived = "archived"


class StatusAdjustment(Enum):
    pending_approval = "pending_approval"
    approved = "approved"
    rejected = "rejected"
    reversed = "reversed"


class StatusDiscount(Enum):
    active = "active"
    archived = "archived"


class StatusNotification(Enum):
    not_attempted = "not_attempted"
    needs_retry = "needs_retry"
    delivered = "delivered"
    failed = "failed"


class StatusPaymentAttempt(Enum):
    authorized = "authorized"
    authorized_flagged = "authorized_flagged"
    canceled = "canceled"
    captured = "captured"
    error = "error"
    action_required = "action_required"
    pending_no_action_required = "pending_no_action_required"
    created = "created"
    unknown = "unknown"
    dropped = "dropped"


class StatusReport(Enum):
    pending = "pending"
    ready = "ready"
    failed = "failed"
    expired = "expired"


class StatusSubscription(Enum):
    active = "active"
    canceled = "canceled"
    past_due = "past_due"
    paused = "paused"
    trialing = "trialing"


class StatusTransaction(Enum):
    draft = "draft"
    ready = "ready"
    billed = "billed"
    paid = "paid"
    completed = "completed"
    canceled = "canceled"
    past_due = "past_due"


class StatusTransactionCreate(Enum):
    draft = "draft"
    ready = "ready"
    billed = "billed"
    paid = "paid"
    completed = "completed"
    canceled = "canceled"
    past_due = "past_due"


class Discount1(BaseModel):
    id: DiscountId
    effective_from: EffectiveFrom = Field(
        ..., description="When this discount should take effect from."
    )


class SubscriptionId(RootModel[Annotated[str, Field(pattern="^sub_[a-z\\d]{26}$")]]):
    root: Annotated[str, Field(pattern="^sub_[a-z\\d]{26}$")] = Field(
        ...,
        description="Unique Paddle ID for this subscription entity, prefixed with `sub_`.",
        examples=["sub_01h04vsc0qhwtsbsxh3422wjs4"],
        title="Subscription ID",
    )


class SubscriptionItemCreateWithPriceId(BaseModel):
    quantity: Annotated[int, Field(ge=1)] = Field(
        ..., description="Quantity to bill for.", examples=[5]
    )
    price_id: Annotated[str, Field(pattern="^pri_[a-z\\d]{26}$")] = Field(
        ..., description="Paddle ID of an an existing catalog price to bill for."
    )


class SubscriptionManagementUrls(BaseModel):
    update_payment_method: AnyUrl | None = Field(
        None,
        description="Link to the page for this subscription in the customer portal with the payment method update form pre-opened. Use as part of workflows to let customers update their payment details. `null` for manually-collected subscriptions.",
        examples=[
            "https://buyer-portal.paddle.com/subscriptions/sub_01gtewvbsyeqyhtp2vtc2mctq8/update-payment-method?token="
        ],
    )
    cancel: AnyUrl = Field(
        ...,
        description="Link to the page for this subscription in the customer portal with the subscription cancellation form pre-opened. Use as part of cancel subscription workflows.",
        examples=[
            "https://buyer-portal.paddle.com/subscriptions/sub_01gtewvbsyeqyhtp2vtc2mctq8/cancel?token="
        ],
    )


class SubscriptionOnPaymentFailure(Enum):
    prevent_change = "prevent_change"
    apply_change = "apply_change"


class SubscriptionOnResume(Enum):
    continue_existing_billing_period = "continue_existing_billing_period"
    start_new_billing_period = "start_new_billing_period"


class Action(Enum):
    cancel = "cancel"
    pause = "pause"
    resume = "resume"


class SubscriptionUpdateItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    price_id: PriceId = Field(
        ...,
        description="Paddle ID for the price to add to this subscription, prefixed with `pri_`.",
    )
    quantity: Annotated[float, Field(ge=1.0)] | None = Field(
        None,
        description="Quantity of this item to add to the subscription. If updating an existing item and not changing the quantity, you may omit `quantity`.",
    )


class SubscriptionUpdateProrationBillingMode(Enum):
    prorated_immediately = "prorated_immediately"
    prorated_next_billing_period = "prorated_next_billing_period"
    full_immediately = "full_immediately"
    full_next_billing_period = "full_next_billing_period"
    do_not_bill = "do_not_bill"


class TaxCategory(Enum):
    digital_goods = "digital-goods"
    ebooks = "ebooks"
    implementation_services = "implementation-services"
    professional_services = "professional-services"
    saas = "saas"
    software_programming_services = "software-programming-services"
    standard = "standard"
    training_services = "training-services"
    website_hosting = "website-hosting"


class TaxMode(Enum):
    account_setting = "account_setting"
    external = "external"
    internal = "internal"
    location = "location"


class TimePeriod(BaseModel):
    starts_at: AwareDatetime = Field(
        ..., description="RFC 3339 datetime string of when this period starts."
    )
    ends_at: AwareDatetime = Field(
        ..., description="RFC 3339 datetime string of when this period ends."
    )


class Timestamp(RootModel[AwareDatetime]):
    root: AwareDatetime = Field(
        ...,
        description="RFC 3339 datetime string.",
        examples=["2024-10-12T07:20:50.52Z"],
        title="Timestamp",
    )


class TotalsModel(BaseModel):
    subtotal: str | None = Field(
        None,
        description="Subtotal before discount, tax, and deductions. If an item, unit price multiplied by quantity.",
        examples=["15000"],
    )
    discount: str | None = Field(
        None,
        description="""Total discount as a result of any discounts applied.

Except for percentage discounts, Paddle applies tax to discounts based on the line item `price.tax_mode`. If `price.tax_mode` for a line item is `internal`, Paddle removes tax from the discount applied.""",
        examples=["0"],
    )
    tax: str | None = Field(
        None, description="Total tax on the subtotal.", examples=["1500"]
    )
    total: str | None = Field(
        None, description="Total after discount and tax.", examples=["16500"]
    )


class TotalsWithoutDiscount(BaseModel):
    subtotal: str | None = Field(
        None,
        description="Subtotal before tax, and deductions. If an item, unit price multiplied by quantity.",
        examples=["15000"],
    )
    tax: str | None = Field(
        None, description="Total tax on the subtotal.", examples=["1500"]
    )
    total: str | None = Field(None, description="Total after tax.", examples=["16500"])


class Checkout(BaseModel):
    url: Annotated[str, Field(min_length=1, max_length=2048)] | None = Field(
        None,
        description="Paddle Checkout URL for this transaction, composed of the URL passed in the request or your default payment URL + `?_ptxn=` and the Paddle ID for this transaction.",
    )


class Checkout1(BaseModel):
    url: Annotated[str, Field(min_length=1, max_length=2048)] | None = Field(
        None,
        description="""Checkout URL to use for the payment link for this transaction. Pass the URL for an approved domain, or omit to use your default payment URL.

Paddle returns a unique payment link composed of the URL passed or your default payment URL + `?_ptxn=` and the Paddle ID for this transaction.""",
    )


class Breakdown(BaseModel):
    credit: str | None = Field(
        None, description="Total amount of credit adjustments.", examples=["8250"]
    )
    refund: str | None = Field(
        None, description="Total amount of refund adjustments.", examples=["8250"]
    )
    chargeback: str | None = Field(
        None, description="Total amount of chargeback adjustments.", examples=["0"]
    )


class AdjustmentsTotals(BaseModel):
    subtotal: str | None = Field(
        None, description="Total before tax.", examples=["15000"]
    )
    tax: str | None = Field(
        None, description="Total tax on the subtotal.", examples=["1500"]
    )
    total: str | None = Field(None, description="Total after tax.", examples=["16500"])
    fee: str | None = Field(
        None, description="Total fee taken by Paddle.", examples=["300"]
    )
    earnings: str | None = Field(
        None,
        description="""Total earnings. This is the subtotal minus the Paddle fee.
For tax adjustments, this value is negative, which means a positive effect in the transaction earnings.
This is because the fee is originally calculated from the transaction total, so if a tax adjustment is made,
then the fee portion of it is returned.
As a result, the earnings from all the adjustments performed could be either negative, positive or zero.""",
        examples=["14700"],
    )
    breakdown: Breakdown | None = Field(
        None,
        description="Breakdown of the total adjustments by adjustment action.",
        title="AdjustmentTotalsBreakdown",
    )
    currency_code: CurrencyCode | None = Field(
        None,
        description="Three-letter ISO 4217 currency code used for adjustments for this transaction.",
    )


class Contact(BaseModel):
    name: Name = Field(..., description="Full name of this contact.")
    email: Email = Field(..., description="Email address for this contact.")


class Type12(Enum):
    flat = "flat"
    flat_per_seat = "flat_per_seat"
    percentage = "percentage"


class Customer(BaseModel):
    name: Name | None = Field(
        None,
        description="Revised name of the customer for this transaction.",
        examples=["Sam Miller"],
    )


class Business2(BaseModel):
    name: Name | None = Field(
        None,
        description="Revised name of the business for this transaction.",
        examples=["ChatApp Inc."],
    )
    tax_identifier: Annotated[str, Field(max_length=1024)] | None = Field(
        None,
        description="Revised tax or VAT number for this transaction. You can't remove a valid tax or VAT number, only replace it with another valid one. Paddle automatically creates an adjustment to refund any tax where applicable.",
        examples=["AB0123456789"],
    )


class Address(BaseModel):
    first_line: Annotated[str, Field(max_length=1024)] | None = Field(
        None,
        description="Revised first line of the address for this transaction.",
        examples=["3811 Ditmars Blvd"],
    )
    second_line: Annotated[str, Field(max_length=1024)] | None = Field(
        None, description="Revised second line of the address for this transaction."
    )
    city: Annotated[str, Field(max_length=200)] | None = Field(
        None,
        description="Revised city of the address for this transaction.",
        examples=["Astoria"],
    )
    region: Annotated[str, Field(max_length=200)] | None = Field(
        None,
        description="Revised state, county, or region of the address for this transaction.",
        examples=["NY"],
    )


class TransactionRevise(BaseModel):
    model_config = ConfigDict(extra="forbid")
    customer: Customer | None = Field(
        None,
        description="Revised customer information for this transaction.",
        title="TransactionRevisionCustomer",
    )
    business: Business2 | None = Field(
        None,
        description="Revised business information for this transaction.",
        title="TransactionRevisionBusiness",
    )
    address: Address | None = Field(
        None,
        description="Revised address information for this transaction.",
        title="TransactionRevisionAddress",
    )


class TransactionSubscriptionProductCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Annotated[str, Field(min_length=1, max_length=200)] = Field(
        ..., description="Name of this product."
    )
    description: Annotated[str, Field(max_length=2048)] | None = Field(
        None, description="Short description for this product."
    )
    tax_category: TaxCategory
    image_url: Annotated[str, Field(min_length=0, max_length=0)] | AnyUrl | None = (
        Field(
            None,
            description="Image for this product. Included in the checkout and on some customer documents.",
        )
    )
    custom_data: CustomData | None = Field(
        None, description="Your own structured key-value data."
    )


class Checkout2(BaseModel):
    url: Annotated[str, Field(min_length=1, max_length=2048)] | None = Field(
        None,
        description="""Checkout URL to use for the payment link for this transaction. Pass the URL for an approved domain, or `null` to set to your default payment URL.

Paddle returns a unique payment link composed of the URL passed or your default payment URL + `?_ptxn=` and the Paddle ID for this transaction.""",
    )


class TransactionAdjustmentsTotalsInclude(BaseModel):
    subtotal: str | None = Field(
        None, description="Total before tax.", examples=["15000"]
    )
    tax: str | None = Field(
        None, description="Total tax on the subtotal.", examples=["1500"]
    )
    total: str | None = Field(None, description="Total after tax.", examples=["16500"])
    fee: str | None = Field(
        None, description="Total fee taken by Paddle.", examples=["300"]
    )
    earnings: str | None = Field(
        None,
        description="""Total earnings. This is the subtotal minus the Paddle fee.
For tax adjustments, this value is negative, which means a positive effect in the transaction earnings.
This is because the fee is originally calculated from the transaction total, so if a tax adjustment is made,
then the fee portion of it is returned.
As a result, the earnings from all the adjustments performed could be either negative, positive or zero.""",
        examples=["14700"],
    )
    breakdown: Breakdown | None = Field(
        None,
        description="Breakdown of the total adjustments by adjustment action.",
        title="AdjustmentTotalsBreakdown",
    )
    currency_code: CurrencyCode | None = Field(
        None,
        description="Three-letter ISO 4217 currency code used for adjustments for this transaction.",
    )


class TaxRatesUsedItem(BaseModel):
    tax_rate: str | None = Field(
        None,
        description="Rate used to calculate tax for this transaction.",
        examples=["0.2"],
    )
    totals: TotalsModel | None = Field(
        None, description="Calculated totals for the tax applied to this transaction."
    )


class TransactionId(RootModel[Annotated[str, Field(pattern="^txn_[a-z\\d]{26}$")]]):
    root: Annotated[str, Field(pattern="^txn_[a-z\\d]{26}$")] = Field(
        ...,
        description="Unique Paddle ID for this transaction entity, prefixed with `txn_`.",
        examples=["txn_01h04vsbhqc62t8hmd4z3b578c"],
        title="Transaction ID",
    )


class TransactionItemId(
    RootModel[Annotated[str, Field(pattern="^txnitm_[a-z\\d]{26}$")]]
):
    root: Annotated[str, Field(pattern="^txnitm_[a-z\\d]{26}$")] = Field(
        ...,
        description="Unique Paddle ID for this transaction item, prefixed with `txnitm_`. Used when working with [adjustments](https://developer.paddle.com/build/transactions/create-transaction-adjustments).",
        examples=["txnitm_01gm302t81w94gyjpjpqypkzkf"],
        title="Transaction item ID",
    )


class TransactionItemProration(BaseModel):
    rate: str | None = Field(None, description="Rate used to calculate proration.")
    billing_period: TimePeriod | None = Field(
        None, description="Billing period that proration is based on."
    )


class TransactionPaymentMethodType(Enum):
    alipay = "alipay"
    apple_pay = "apple_pay"
    bancontact = "bancontact"
    card = "card"
    google_pay = "google_pay"
    ideal = "ideal"
    korea_local = "korea_local"
    offline = "offline"
    paypal = "paypal"
    unknown = "unknown"
    wire_transfer = "wire_transfer"


class TransactionPayoutTotals(BaseModel):
    subtotal: str | None = Field(
        None, description="Total before tax and fees.", examples=["15000"]
    )
    discount: str | None = Field(
        None,
        description="""Total discount as a result of any discounts applied.
Except for percentage discounts, Paddle applies tax to discounts based on the line item `price.tax_mode`. If `price.tax_mode` for a line item is `internal`, Paddle removes tax from the discount applied.""",
        examples=["0"],
    )
    tax: str | None = Field(
        None, description="Total tax on the subtotal.", examples=["1500"]
    )
    total: str | None = Field(None, description="Total after tax.", examples=["16500"])
    credit: str | None = Field(
        None,
        description="Total credit applied to this transaction. This includes credits applied using a customer's credit balance and adjustments to a `billed` transaction.",
        examples=["0"],
    )
    credit_to_balance: str | None = Field(
        None,
        description="Additional credit generated from negative `details.line_items`. This credit is added to the customer balance.",
        examples=["0"],
    )
    balance: str | None = Field(
        None,
        description="Total due on a transaction after credits and any payments.",
        examples=["16500"],
    )
    grand_total: str | None = Field(
        None,
        description="Total due on a transaction after credits but before any payments.",
        examples=["16500"],
    )
    fee: str | None = Field(
        None, description="Total fee taken by Paddle for this payout.", examples=["825"]
    )
    earnings: str | None = Field(
        None,
        description="Total earnings for this payout. This is the subtotal minus the Paddle fee.",
        examples=["15675"],
    )
    currency_code: CurrencyCodePayout | None = Field(
        None,
        description="Three-letter ISO 4217 currency code used for the payout for this transaction. If your primary currency has changed, this reflects the primary currency at the time the transaction was billed.",
    )


class Original(BaseModel):
    amount: str | None = Field(
        None,
        description="Fee amount for this chargeback in the original currency.",
        examples=["1500"],
    )
    currency_code: CurrencyCodeChargeback | None = Field(
        None,
        description="Three-letter ISO 4217 currency code for the original chargeback fee.",
        examples=["USD"],
    )


class ChargebackFee1(BaseModel):
    amount: str | None = Field(
        None,
        description="Chargeback fee converted into the payout currency.",
        examples=["1680"],
    )
    original: Original | None = Field(
        None,
        description="Chargeback fee before conversion to the payout currency. `null` when the chargeback fee is the same as the payout currency.",
    )


class TransactionPayoutTotalsAdjusted(BaseModel):
    subtotal: str | None = Field(
        None, description="Total before tax and fees.", examples=["15000"]
    )
    tax: str | None = Field(
        None, description="Total tax on the subtotal.", examples=["1500"]
    )
    total: str | None = Field(None, description="Total after tax.", examples=["16500"])
    fee: str | None = Field(
        None, description="Total fee taken by Paddle for this payout.", examples=["825"]
    )
    chargeback_fee: ChargebackFee1 | None = Field(
        None,
        description="Details of any chargeback fees incurred for this transaction.",
    )
    earnings: str | None = Field(
        None,
        description="Total earnings for this payout. This is the subtotal minus the Paddle fee, excluding chargeback fees.",
        examples=["15675"],
    )
    currency_code: CurrencyCodePayout | None = Field(
        None,
        description="Three-letter ISO 4217 currency code used for the payout for this transaction. If your primary currency has changed, this reflects the primary currency at the time the transaction was billed.",
    )


class TaxRatesUsedItem4(BaseModel):
    tax_rate: str | None = Field(
        None,
        description="Rate used to calculate tax for this transaction preview.",
        examples=["0.2"],
    )
    totals: TotalsModel | None = Field(
        None,
        description="Calculated totals for the tax applied to this transaction preview.",
    )


class TransactionPreviewItemBase(BaseModel):
    quantity: int = Field(..., description="Quantity of this item on the transaction.")
    include_in_totals: bool | None = Field(
        True,
        description="Whether this item should be included in totals for this transaction preview. Typically used to exclude one-time charges from calculations.",
    )
    proration: TransactionItemProration | None = Field(
        None,
        description="How proration was calculated for this item. `null` for transaction previews.",
    )


class TransactionPreviewItemWithPriceId(TransactionPreviewItemBase):
    price_id: PriceId = Field(
        ...,
        description="Paddle ID of an existing catalog price to preview charging for, prefixed with `pri_`.",
    )


class TransactionPricingPreviewItem(BaseModel):
    price_id: PriceId | None = Field(
        None,
        description="Paddle ID for the price to add to this transaction, prefixed with `pri_`.",
    )
    quantity: Annotated[int, Field(ge=1)] = Field(
        ..., description="Quantity of the item to preview."
    )


class TransactionTotals(TotalsModel):
    credit: str | None = Field(
        None,
        description="Total credit applied to this transaction. This includes credits applied using a customer's credit balance and adjustments to a `billed` transaction.",
        examples=["0"],
    )
    credit_to_balance: str | None = Field(
        None,
        description="Additional credit generated from negative `details.line_items`. This credit is added to the customer balance.",
        examples=["0"],
    )
    balance: str | None = Field(
        None,
        description="Total due on a transaction after credits and any payments.",
        examples=["16500"],
    )
    grand_total: str | None = Field(
        None,
        description="Total due on a transaction after credits but before any payments.",
        examples=["16500"],
    )
    fee: str | None = Field(
        None,
        description="Total fee taken by Paddle for this transaction. `null` until the transaction is `completed` and the fee is processed.",
        examples=["825"],
    )
    earnings: str | None = Field(
        None,
        description="Total earnings for this transaction. This is the total minus the Paddle fee. `null` until the transaction is `completed` and the fee is processed.",
        examples=["15675"],
    )
    currency_code: CurrencyCode | None = Field(
        None,
        description="Three-letter ISO 4217 currency code of the currency used for this transaction.",
    )


class TransactionTotalsAdjusted(BaseModel):
    subtotal: str | None = Field(
        None,
        description="Subtotal before discount, tax, and deductions. If an item, unit price multiplied by quantity.",
        examples=["15000"],
    )
    tax: str | None = Field(
        None, description="Total tax on the subtotal.", examples=["1500"]
    )
    total: str | None = Field(None, description="Total after tax.", examples=["16500"])
    grand_total: str | None = Field(
        None,
        description="Total due after credits but before any payments.",
        examples=["16500"],
    )
    fee: str | None = Field(
        None,
        description="Total fee taken by Paddle for this transaction. `null` until the transaction is `completed` and the fee is processed.",
        examples=["825"],
    )
    earnings: str | None = Field(
        None,
        description="""Total earnings for this transaction. This is the total minus the Paddle fee.
`null` until the transaction is `completed` and the fee is processed.""",
        examples=["15675"],
    )
    currency_code: CurrencyCode | None = Field(
        None,
        description="Three-letter ISO 4217 currency code of the currency used for this transaction.",
    )


class UnderlyingDetails(BaseModel):
    korea_local: KoreaLocalUnderlyingDetails | None = None


class Action1(Enum):
    credit = "credit"
    charge = "charge"


class Result(BaseModel):
    action: Action1 | None = Field(
        None,
        description="Whether the subscription change results in a prorated credit or a charge.",
        title="UpdateSummaryResultAction",
    )
    amount: str | None = Field(
        None,
        description="Amount representing the result of this update, either a charge or a credit.",
    )
    currency_code: CurrencyCode | None = Field(
        None,
        description="Three-letter ISO 4217 currency code for the transaction or adjustment.",
    )


class UpdateSummary(BaseModel):
    credit: Money | None = Field(
        None,
        description="Details of any credit adjustments created for this update. Paddle creates adjustments against existing transactions when prorating.",
    )
    charge: Money | None = Field(
        None,
        description="Details of the transaction to be created for this update. Paddle creates a transaction to bill for new charges.",
    )
    result: Result | None = Field(
        None,
        description="Details of the result of credits and charges. Where the total of any credit adjustments is greater than the total charge, the result is a prorated credit; otherwise, the result is a prorated charge.",
        title="UpdateSummaryResult",
    )


class UpdatedAt(RootModel[AwareDatetime]):
    root: AwareDatetime = Field(
        ...,
        description="RFC 3339 datetime string of when this entity was updated. Set automatically by Paddle.",
        examples=["2024-10-13T07:20:50.52Z"],
        title="Updated at",
    )


class AdjustmentItem(BaseModel):
    item_id: TransactionItemId = Field(
        ...,
        description="Paddle ID for the transaction item that this adjustment item relates to, prefixed with `txnitm_`.",
    )
    type: Type = Field(
        ...,
        description="""Type of adjustment for this transaction item. `tax` adjustments are automatically created by Paddle.
Include `amount` when creating a `partial` adjustment.""",
        examples=["full"],
        title="AdjustmentItemType",
    )
    amount: str | None = Field(
        None,
        description="Amount adjusted for this transaction item. Required when item `type` is `partial`.",
    )
    proration: TransactionItemProration | None = Field(
        None, description="How proration was calculated for this adjustment item."
    )
    totals: AdjustmentItemTotals | None = None


class ChargebackFee(BaseModel):
    amount: str | None = Field(
        None,
        description="Chargeback fee converted into the payout currency.",
        examples=["1680"],
    )
    original: Original | None = Field(
        None,
        description="Chargeback fee before conversion to the payout currency. `null` when the chargeback fee is the same as the payout currency.",
    )


class AdjustmentPayoutTotals(BaseModel):
    subtotal: str | None = Field(
        None, description="Adjustment total before tax and fees.", examples=["15000"]
    )
    tax: str | None = Field(
        None, description="Total tax on the adjustment subtotal.", examples=["1500"]
    )
    total: str | None = Field(
        None, description="Adjustment total after tax.", examples=["16500"]
    )
    fee: str | None = Field(None, description="Adjusted Paddle fee.", examples=["300"])
    chargeback_fee: ChargebackFee | None = Field(
        None,
        description="Chargeback fees incurred for this adjustment. Only returned when the adjustment `action` is `chargeback` or `chargeback_warning`.",
    )
    earnings: str | None = Field(
        None,
        description="Adjusted payout earnings. This is the adjustment total plus adjusted Paddle fees, excluding chargeback fees.",
        examples=["15120"],
    )
    currency_code: CurrencyCodePayout | None = Field(
        None,
        description="Three-letter ISO 4217 currency code used for the payout for this transaction. If your primary currency has changed, this reflects the primary currency at the time the transaction was billed.",
    )


class AdjustmentTotals(BaseModel):
    subtotal: str | None = Field(
        None,
        description="Total before tax. For tax adjustments, the value is 0.",
        examples=["15000"],
    )
    tax: str | None = Field(
        None, description="Total tax on the subtotal.", examples=["1500"]
    )
    total: str | None = Field(None, description="Total after tax.", examples=["16500"])
    fee: str | None = Field(
        None,
        description="Total fee taken by Paddle for this adjustment.",
        examples=["300"],
    )
    earnings: str | None = Field(
        None,
        description="""Total earnings. This is the subtotal minus the Paddle fee.
For tax adjustments, this value is negative, which means a positive effect in the transaction earnings.
This is because the fee is originally calculated from the transaction total, so if a tax adjustment is made,
then the fee portion of it is returned.""",
        examples=["14700"],
    )
    currency_code: CurrencyCode | None = Field(
        None,
        description="Three-letter ISO 4217 currency code used for this adjustment.",
        examples=["USD"],
    )


class ApikeyPermission(RootModel[Permission]):
    root: Permission


class BillingDetails(BaseModel):
    enable_checkout: bool | None = Field(
        False,
        description="Whether the related transaction may be paid using Paddle Checkout. If omitted when creating a transaction, defaults to `false`.",
    )
    purchase_order_number: Annotated[str, Field(max_length=100)] | None = Field(
        None,
        description="Customer purchase order number. Appears on invoice documents.",
    )
    additional_information: Annotated[str, Field(max_length=1500)] | None = Field(
        None,
        description="Notes or other information to include on this invoice. Appears on invoice documents.",
    )
    payment_terms: Duration = Field(
        ..., description="How long a customer has to pay this invoice once issued."
    )


class BillingDetailsUpdate(BaseModel):
    enable_checkout: bool | None = Field(
        False,
        description="Whether the related transaction may be paid using Paddle Checkout.",
    )
    purchase_order_number: Annotated[str, Field(max_length=100)] | None = Field(
        None,
        description="Customer purchase order number. Appears on invoice documents.",
    )
    additional_information: Annotated[str, Field(max_length=1500)] | None = Field(
        None,
        description="Notes or other information to include on this invoice. Appears on invoice documents.",
    )
    payment_terms: Duration | None = Field(
        None, description="How long a customer has to pay this invoice once issued."
    )


class Contact1(BaseModel):
    name: Name | None = Field(None, description="Full name of this contact.")
    email: Email = Field(..., description="Email address for this contact.")


class BusinessUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Annotated[str, Field(min_length=1, max_length=1024)] | None = Field(
        None, description="Name of this business."
    )
    company_number: Annotated[str, Field(max_length=1024)] | None = Field(
        None, description="Company number for this business.", examples=["123456789"]
    )
    tax_identifier: Annotated[str, Field(max_length=1024)] | None = Field(
        None,
        description="Tax or VAT Number for this business.",
        examples=["AB0123456789"],
    )
    status: Status | None = None
    contacts: list[Contact1] | None = Field(
        None,
        description="List of contacts related to this business, typically used for sending invoices.",
        max_length=100,
    )
    custom_data: CustomData | None = Field(
        None, description="Your own structured key-value data."
    )


class Card(BaseModel):
    type: CardType | None = None
    last4: CardLast4 | None = None
    expiry_month: CardExpiryMonth | None = None
    expiry_year: CardExpiryYear | None = None
    cardholder_name: CardCardholderName | None = None


class CountryCode(RootModel[CountryCodeSupported]):
    root: CountryCodeSupported = Field(
        ...,
        description="Two-letter ISO 3166-1 alpha-2 country code.",
        title="Country code",
    )


class CreditBalance(BaseModel):
    customer_id: CustomerId | None = Field(
        None,
        description="Paddle ID of the customer that this credit balance is for, prefixed with `ctm_`.",
    )
    currency_code: CurrencyCode | None = Field(
        None, description="Three-letter ISO 4217 currency code for this credit balance."
    )
    balance: CustomerBalance | None = Field(
        None,
        description="Totals for this credit balance. Where a customer has more than one subscription in this currency with a credit balance, includes totals for all subscriptions.",
    )


class CustomerPaymentMethod(BaseModel):
    id: PaymentMethodId | None = None
    customer_id: CustomerId | None = Field(
        None,
        description="Paddle ID of the customer that this payment method is saved for, prefixed with `ctm_`.",
    )
    address_id: AddressId | None = Field(
        None,
        description="Paddle ID of the address for this payment method, prefixed with `add_`.",
    )
    type: Type1 | None = Field(
        None,
        description="Type of payment method saved.",
        title="SavedPaymentMethodType",
    )
    card: Card | None = Field(
        None,
        description="Information about the credit or debit card saved. `null` unless `type` is `card`.",
    )
    paypal: Paypal | None = Field(
        None,
        description="Information about the PayPal payment method saved. `null` unless `type` is `paypal`.",
    )
    underlying_details: UnderlyingDetails | None = None
    origin: Origin | None = Field(
        None,
        description="Describes how this payment method was saved.",
        title="PaymentMethodOrigin",
    )
    saved_at: SavedAt | None = None
    updated_at: UpdatedAt | None = None


class Subscription(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: SubscriptionId = Field(
        ...,
        description="Paddle ID of the subscription that the authenticated customer portal deep links are for.",
    )
    cancel_subscription: str = Field(
        ...,
        description="Link to the page for this subscription in the customer portal with the subscription cancellation form pre-opened. Use as part of cancel subscription workflows.",
        examples=[
            "https://customer-portal.paddle.com/cpl_01j7zbyqs3vah3aafp4jf62qaw?action=cancel_subscription&subscription_id=sub_01h04vsc0qhwtsbsxh3422wjs4&token="
        ],
    )
    update_subscription_payment_method: str = Field(
        ...,
        description="""Link to the page for this subscription in the customer portal with the payment method update form pre-opened. Use as part of workflows to let customers update their payment details.

If a manually-collected subscription, opens the overview page for this subscription.""",
        examples=[
            "https://customer-portal.paddle.com/cpl_01j7zbyqs3vah3aafp4jf62qaw?action=update_subscription_payment_method&subscription_id=sub_01h04vsc0qhwtsbsxh3422wjs4&token="
        ],
    )


class Urls(BaseModel):
    model_config = ConfigDict(extra="forbid")
    general: General = Field(
        ...,
        description="Authenticated customer portal deep links that aren't associated with a specific entity.",
        title="CustomerPortalSessionGeneralUrls",
    )
    subscriptions: list[Subscription] | None = Field(
        None,
        description="""List of generated authenticated customer portal deep links for the subscriptions passed in the `subscription_ids` array in the request.

If subscriptions are paused or canceled, links open the overview page for a subscription.

Empty if no subscriptions passed in the request.""",
        max_length=25,
    )


class CustomerPortalSession(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: CustomerPortalSessionId
    customer_id: CustomerId | None = Field(
        None,
        description="Paddle ID of the customer that this customer portal sessions is for, prefixed with `ctm_`.",
    )
    urls: Urls = Field(
        ...,
        description="Authenticated customer portal deep links. For security, the `token` appended to each link is temporary. You shouldn't store these links.",
        title="CustomerPortalSessionUrls",
    )
    created_at: Timestamp = Field(
        ...,
        description="RFC 3339 datetime string of when this customer portal session was created.",
    )


class CustomerPortalSessionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    subscription_ids: list[SubscriptionId] | None = Field(
        None,
        description="List of subscriptions to create authenticated customer portal deep links for.",
        max_length=25,
    )


class CustomerAuthenticationToken(BaseModel):
    customer_auth_token: CustomerAuthToken
    expires_at: Timestamp | None = Field(
        None,
        description="RFC 3339 datetime string of when this customer authentication token expires. The token is no longer valid after this date.",
    )


class DiscountSubscription(BaseModel):
    id: DiscountId
    starts_at: Timestamp | None = Field(
        ...,
        description="RFC 3339 datetime string of when this discount was first applied. `null` for canceled subscriptions where a discount was redeemed but never applied to a transaction.",
    )
    ends_at: Timestamp | None = Field(
        ...,
        description="RFC 3339 datetime string of when this discount no longer applies. Where a discount has `maximum_recurring_intervals`, this is the date of the last billing period where this discount applies. `null` where a discount recurs forever.",
    )


class Event(BaseModel):
    event_id: EventId | None = None
    event_type: EventTypeName | None = None
    occurred_at: Timestamp | None = Field(
        None, description="RFC 3339 datetime string of when this event occurred."
    )
    data: dict[str, Any] | None = Field(None, description="New or changed entity.")


class EventType(BaseModel):
    name: EventTypeName | None = None
    description: str | None = Field(
        None,
        description="Short description of this event type.",
        examples=[
            "The subscription.created alert is fired when a new subscription is created."
        ],
    )
    group: str | None = Field(
        None,
        description="Group for this event type. Typically the entity that this event relates to.",
        examples=["Subscriptions"],
    )
    available_versions: list[int] | None = Field(
        None, description="List of API versions that this event type supports."
    )


class ImportMetaSubscription(BaseModel):
    external_id: Annotated[str, Field(min_length=1, max_length=200)] | None = None
    imported_from: MigrationProviderPublic = Field(
        ...,
        description="Name of the platform or provider where this entity was imported from.",
    )


class Meta(BaseModel):
    request_id: RequestId


class MetaPaginated(BaseModel):
    request_id: RequestId
    pagination: Pagination


class MethodDetails(BaseModel):
    type: TransactionPaymentMethodType | None = None
    underlying_details: UnderlyingDetails | None = None
    card: Card | None = Field(
        None,
        description="Information about the credit or debit card used to pay. `null` unless `type` is `card`.",
    )


class MigrationProvider(RootModel[MigrationProviderPublic]):
    root: MigrationProviderPublic = Field(
        ...,
        description="Platform or provider that a migration is from.",
        title="MigrationProvider",
    )


class Payload(Event):
    notification_id: NotificationId | None = None


class Notification(BaseModel):
    id: NotificationId | None = None
    type: EventTypeName | None = None
    status: StatusNotification | None = None
    payload: Payload | None = None
    occurred_at: Timestamp | None = Field(
        None, description="RFC 3339 datetime string of when this notification occurred."
    )
    delivered_at: Timestamp | None = Field(
        None,
        description="RFC 3339 datetime string of when this notification was delivered. `null` if not yet delivered successfully.",
    )
    replayed_at: Timestamp | None = Field(
        None,
        description="RFC 3339 datetime string of when this notification was replayed. `null` if not replayed.",
    )
    origin: Origin1 | None = Field(
        None,
        description="Describes how this notification was created.",
        title="NotificationOrigin",
    )
    last_attempt_at: Timestamp | None = Field(
        None,
        description="RFC 3339 datetime string of when this notification was last attempted.",
    )
    retry_at: Timestamp | None = Field(
        None,
        description="RFC 3339 datetime string of when this notification is scheduled to be retried.",
    )
    times_attempted: int | None = Field(
        None,
        description="How many times delivery of this notification has been attempted. Automatically incremented by Paddle after an attempt.",
    )
    notification_setting_id: NotificationSettingId | None = None


class NotificationLog(BaseModel):
    id: NotificationLogId | None = None
    response_code: int | None = Field(
        None, description="HTTP code sent by the responding server.", examples=[200]
    )
    response_content_type: str | None = Field(
        None,
        description="Content-Type sent by the responding server.",
        examples=["text/plain; charset=UTF-8"],
    )
    response_body: str | None = Field(
        None,
        description="Response body sent by the responding server. Typically empty for success responses.",
    )
    attempted_at: Timestamp | None = Field(
        None,
        description="RFC 3339 datetime string of when Paddle attempted to deliver the related notification.",
    )


class NotificationSetting(BaseModel):
    id: NotificationSettingId | None = None
    description: Annotated[str, Field(min_length=1, max_length=500)] | None = Field(
        None,
        description="Short description for this notification destination. Shown in the Paddle dashboard.",
    )
    type: Type6 | None = Field(
        None,
        description="Where notifications should be sent for this destination.",
        title="NotificationSettingType",
    )
    destination: Annotated[str, Field(min_length=1, max_length=2048)] | None = Field(
        None, description="Webhook endpoint URL or email address."
    )
    active: bool | None = Field(
        True,
        description="Whether Paddle should try to deliver events to this notification destination.",
    )
    api_version: Annotated[int, Field(ge=1)] | None = Field(
        None,
        description="API version that returned objects for events should conform to. Must be a valid version of the Paddle API. Can't be a version older than your account default.",
    )
    include_sensitive_fields: bool | None = Field(
        False,
        description="Whether potentially sensitive fields should be sent to this notification destination.",
    )
    subscribed_events: list[EventType] | None = Field(
        None, description="Subscribed events for this notification destination."
    )
    endpoint_secret_key: (
        Annotated[str, Field(pattern="^pdl_ntfset_[a-zA-Z0-9]{26}_[a-zA-Z0-9]{32}$")]
        | None
    ) = Field(
        None,
        description="Webhook destination secret key, prefixed with `pdl_ntfset_`. Used for signature verification.",
    )
    traffic_source: TrafficSource | None = Field(
        None,
        description="Whether Paddle should deliver real platform events, simulation events or both to this notification destination.",
    )


class NotificationSettingCreate(BaseModel):
    id: NotificationSettingId | None = None
    description: Annotated[str, Field(min_length=1, max_length=500)] = Field(
        ...,
        description="Short description for this notification destination. Shown in the Paddle Dashboard.",
    )
    type: Type6 = Field(
        ...,
        description="Where notifications should be sent for this destination.",
        title="NotificationSettingType",
    )
    destination: Annotated[str, Field(min_length=1, max_length=2048)] = Field(
        ..., description="Webhook endpoint URL or email address."
    )
    active: bool | None = Field(
        True,
        description="Whether Paddle should try to deliver events to this notification destination.",
    )
    api_version: Annotated[int, Field(ge=1)] | None = Field(
        None,
        description="API version that returned objects for events should conform to. Must be a valid version of the Paddle API. Can't be a version older than your account default. If omitted, defaults to your account default version.",
    )
    include_sensitive_fields: bool | None = Field(
        False,
        description="Whether potentially sensitive fields should be sent to this notification destination. If omitted, defaults to `false`.",
    )
    subscribed_events: list[EventTypeName] = Field(
        ...,
        description="Subscribed events for this notification destination. When creating or updating a notification destination, pass an array of event type names only. Paddle returns the complete event type object.",
    )
    endpoint_secret_key: (
        Annotated[str, Field(pattern="^pdl_ntfset_[a-zA-Z0-9]{26}_[a-zA-Z0-9]{32}$")]
        | None
    ) = Field(
        None,
        description="Webhook destination secret key, prefixed with `pdl_ntfset_`. Used for signature verification.",
    )
    traffic_source: TrafficSource | None = Field(
        "platform",
        description="Whether Paddle should deliver real platform events, simulation events or both to this notification destination. If omitted, defaults to `platform`.",
    )


class ProductUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Annotated[str, Field(min_length=1, max_length=200)] | None = Field(
        None, description="Name of this product."
    )
    description: Annotated[str, Field(max_length=2048)] | None = Field(
        None, description="Short description for this product."
    )
    type: CatalogType | None = "standard"
    tax_category: TaxCategory | None = None
    image_url: Annotated[str, Field(min_length=0, max_length=0)] | AnyUrl | None = (
        Field(
            None,
            description="Image for this product. Included in the checkout and on some customer documents.",
        )
    )
    custom_data: CustomData | None = Field(
        None, description="Your own structured key-value data."
    )
    status: Status | None = None


class ReportBase(BaseModel):
    id: PaddleId | None = Field(
        None, description="Unique Paddle ID for this report, prefixed with `rep_`"
    )
    status: StatusReport | None = "pending"
    rows: int | None = Field(
        None,
        description="Number of records in this report. `null` if the report is `pending`.",
    )
    expires_at: Timestamp | None = Field(
        None,
        description="RFC 3339 datetime string of when this report expires. The report is no longer available to download after this date.",
    )
    updated_at: UpdatedAt | None = Field(
        None,
        description="RFC 3339 datetime string of when this report was last updated.",
    )
    created_at: CreatedAt | None = Field(
        None, description="RFC 3339 datetime string of when this report was created."
    )


class ReportDiscounts(ReportBase):
    type: Type9 = Field(
        ...,
        description="Type of report to create.",
        examples=["discounts"],
        title="DiscountsReportType",
    )
    filters: ReportFilterDiscounts | None = Field(
        None,
        description="Filter criteria for this report. If omitted, reports are filtered to include data updated in the last 30 days. This means `updated_at` is greater than or equal to (`gte`) the date 30 days ago from the time the report was generated.",
    )


class ReportProductsPrices(ReportBase):
    type: Type10 = Field(
        ...,
        description="Type of report to create.",
        examples=["products_prices"],
        title="ProductsPricesReportType",
    )
    filters: ReportFilterProductsPrices | None = Field(
        None,
        description="Filter criteria for this report. If omitted, reports are filtered to include data updated in the last 30 days. This means `product_updated_at` and `price_updated_at` are greater than or equal to (`gte`) the date 30 days ago from the time the report was generated.",
    )


class ReportTransactions(ReportBase):
    type: ReportTypeTransactions = Field(..., description="Type of report to create.")
    filters: ReportFilterTransactions | None = Field(
        None,
        description="Filter criteria for this report. If omitted, reports are filtered to include data updated in the last 30 days. This means `updated_at` is greater than or equal to (`gte`) the date 30 days ago from the time the report was generated.",
    )


class SimulationConfigEntitiesSubscriptionCreation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    customer_id: CustomerId | None = Field(
        None,
        description="Paddle ID of a customer. Adds customer details to webhook payloads.",
    )
    address_id: AddressId | None = Field(
        None,
        description="Paddle ID of an address. Adds address details to webhook payloads. Requires `customer_id`.",
    )
    business_id: BusinessId | None = Field(
        None,
        description="Paddle ID of a business. Adds business details to webhook payloads. Requires `customer_id`.",
    )
    payment_method_id: PaymentMethodId | None = Field(
        None,
        description="Paddle ID of a payment method. Adds payment method details to webhook payloads. Requires `customer_id`.",
    )
    discount_id: DiscountId | None = Field(
        None,
        description="Paddle ID of a discount. Adds discount details (including price calculations) to webhook payloads. Requires `items` or `transaction_id` for the discount to be applied.",
    )
    transaction_id: TransactionId | None = Field(
        None,
        description="Paddle ID of a transaction. Bases the subscription on the transaction.",
    )
    items: list[SubscriptionItemCreateWithPriceId] | None = Field(
        None,
        description="Items to include on the simulated subscription. Only existing products and prices can be simulated. Non-catalog items aren't supported. At least one recurring price must be provided.",
    )


class SimulationConfigEntitiesSubscriptionCreationItems(BaseModel):
    model_config = ConfigDict(extra="forbid")
    customer_id: CustomerId | None = Field(
        None,
        description="Paddle ID of a customer. Adds customer details to webhook payloads.",
    )
    address_id: AddressId | None = Field(
        None,
        description="Paddle ID of an address. Adds address details to webhook payloads. Requires `customer_id`.",
    )
    business_id: BusinessId | None = Field(
        None,
        description="Paddle ID of a business. Adds business details to webhook payloads. Requires `customer_id`.",
    )
    payment_method_id: PaymentMethodId | None = Field(
        None,
        description="Paddle ID of a payment method. Adds payment method details to webhook payloads. Requires `customer_id`.",
    )
    discount_id: DiscountId | None = Field(
        None,
        description="Paddle ID of a discount. Adds discount details (including price calculations) to webhook payloads. Requires `items` or `transaction_id` for the discount to be applied.",
    )
    items: list[SubscriptionItemCreateWithPriceId] | None = Field(
        None,
        description="Items to include on the simulated subscription. Only existing products and prices can be simulated. Non-catalog items aren't supported. At least one recurring price must be provided.",
        max_length=100,
        min_length=1,
    )
    transaction_id: None = Field(
        None,
        description="Paddle ID of an existing transaction. Simulates passing a transaction ID to Paddle.js.",
    )


class Entities(BaseModel):
    model_config = ConfigDict(extra="forbid")
    subscription_id: SubscriptionId | None = Field(
        None,
        description="Paddle ID of a subscription to simulate as canceled. Adds details of that subscription to webhook payloads.",
    )


class SimulationConfigSubscriptionCancellation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    entities: Entities | None = Field(
        None,
        description="Adds details of existing Paddle entities to webhook payloads sent in the simulation.",
    )
    options: Options | None = Field(
        None,
        description="Options that determine which webhooks are sent as part of a simulation.",
    )


class SubscriptionCancellation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    entities: Entities | None = Field(
        None,
        description="Adds details of existing Paddle entities to webhook payloads sent in the simulation.",
    )
    options: Options1 | None = Field(
        None,
        description="Options that determine which webhooks are sent as part of a simulation.",
    )


class SimulationConfigSubscriptionCancellationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    subscription_cancellation: SubscriptionCancellation | None = None
    subscription_creation: None = None
    subscription_pause: None = None
    subscription_renewal: None = None
    subscription_resume: None = None
    type: Literal["subscription_cancellation"]


class SimulationConfigSubscriptionCreation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    entities: SimulationConfigEntitiesSubscriptionCreation | None = Field(
        None,
        description="Adds details of existing Paddle entities to webhook payloads sent in the simulation.",
    )
    options: SimulationConfigSubscriptionCreationOptions | None = Field(
        None,
        description="Options that determine which webhooks are sent as part of a simulation.",
    )


class SubscriptionCreation(BaseModel):
    entities: (
        SimulationConfigEntitiesSubscriptionCreationNoPrices
        | SimulationConfigEntitiesSubscriptionCreationItems
        | SimulationConfigEntitiesSubscriptionCreationTransaction
        | None
    ) = Field(
        None,
        description="Adds details of existing Paddle entities to webhook payloads sent in the simulation.",
    )
    options: SimulationConfigSubscriptionCreationOptions | None = Field(
        None,
        description="Options that determine which webhooks are sent as part of a simulation.",
    )


class SimulationConfigSubscriptionCreationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    subscription_creation: SubscriptionCreation | None = Field(
        None, description="Configuration for subscription creation simulations."
    )
    subscription_cancellation: None = None
    subscription_pause: None = None
    subscription_renewal: None = None
    subscription_resume: None = None
    type: Literal["subscription_creation"]


class Entities2(BaseModel):
    model_config = ConfigDict(extra="forbid")
    subscription_id: SubscriptionId | None = Field(
        None,
        description="Paddle ID of a subscription to simulate as paused. Adds details of that subscription to webhook payloads.",
    )


class SimulationConfigSubscriptionPause(BaseModel):
    model_config = ConfigDict(extra="forbid")
    entities: Entities2 | None = Field(
        None,
        description="Adds details of existing Paddle entities to webhook payloads sent in the simulation.",
    )
    options: Options2 | None = Field(
        None,
        description="Options that determine which webhooks are sent as part of a simulation.",
    )


class SubscriptionPause(BaseModel):
    model_config = ConfigDict(extra="forbid")
    entities: Entities2 | None = Field(
        None,
        description="Adds details of existing Paddle entities to webhook payloads sent in the simulation.",
    )
    options: Options3 | None = Field(
        None,
        description="Options that determine which webhooks are sent as part of a simulation.",
    )


class SimulationConfigSubscriptionPauseCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    subscription_pause: SubscriptionPause | None = None
    subscription_cancellation: None = None
    subscription_creation: None = None
    subscription_renewal: None = None
    subscription_resume: None = None
    type: Literal["subscription_pause"]


class Entities4(BaseModel):
    model_config = ConfigDict(extra="forbid")
    subscription_id: SubscriptionId | None = Field(
        None,
        description="Paddle ID of a subscription to simulate as renewed. Adds details of that subscription to webhook payloads.",
    )


class SimulationConfigSubscriptionRenewal(BaseModel):
    model_config = ConfigDict(extra="forbid")
    entities: Entities4 | None = Field(
        None,
        description="Adds details of existing Paddle entities to webhook payloads sent in the simulation.",
    )
    options: SimulationConfigOptionsPayment | None = Field(
        None,
        description="Options that determine which webhooks are sent as part of a simulation.",
    )


class SubscriptionRenewal(BaseModel):
    entities: Entities4 | None = Field(
        None,
        description="Adds details of existing Paddle entities to webhook payloads sent in the simulation.",
    )
    options: (
        SimulationConfigOptionsPaymentSuccess
        | SimulationConfigOptionsPaymentFailed
        | SimulationConfigOptionsPaymentRecoveredExisting
        | SimulationConfigOptionsPaymentRecoveredUpdated
        | None
    ) = Field(
        None,
        description="Options that determine which webhooks are sent as part of a simulation.",
    )


class SimulationConfigSubscriptionRenewalCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    subscription_renewal: SubscriptionRenewal | None = Field(
        None, description="Configuration for subscription renewed simulations."
    )
    subscription_cancellation: None = None
    subscription_creation: None = None
    subscription_pause: None = None
    subscription_resume: None = None
    type: Literal["subscription_renewal"]


class Entities6(BaseModel):
    model_config = ConfigDict(extra="forbid")
    subscription_id: SubscriptionId | None = Field(
        None,
        description="Paddle ID of a subscription to simulate as resumed. Adds details of that subscription to webhook payloads.",
    )


class SimulationConfigSubscriptionResume(BaseModel):
    model_config = ConfigDict(extra="forbid")
    entities: Entities6 | None = Field(
        None,
        description="Adds details of existing Paddle entities to webhook payloads sent in the simulation.",
    )
    options: SimulationConfigOptionsPayment | None = Field(
        None,
        description="Options that determine which webhooks are sent as part of a simulation.",
    )


class SubscriptionResume(BaseModel):
    entities: Entities6 | None = Field(
        None,
        description="Adds details of existing Paddle entities to webhook payloads sent in the simulation.",
    )
    options: (
        SimulationConfigOptionsPaymentSuccess
        | SimulationConfigOptionsPaymentFailed
        | SimulationConfigOptionsPaymentRecoveredExisting
        | SimulationConfigOptionsPaymentRecoveredUpdated
        | None
    ) = Field(
        None,
        description="Options that determine which webhooks are sent as part of a simulation.",
    )


class SimulationConfigSubscriptionResumeCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    subscription_resume: SubscriptionResume | None = Field(
        None, description="Configuration for subscription resumed simulations."
    )
    subscription_cancellation: None = None
    subscription_creation: None = None
    subscription_pause: None = None
    subscription_renewal: None = None
    type: Literal["subscription_resume"]


class SimulationEvent(BaseModel):
    id: SimulationEventId | None = None
    status: SimulationEventStatus | None = None
    event_type: EventTypeName | None = None
    payload: dict[str, Any] | None = Field(
        None,
        description="Simulation payload. Pass a JSON object that matches the schema for an event type to simulate a custom payload. If omitted, Paddle populates with a demo example.",
    )
    request: Request | None = Field(
        None,
        description="Information about the request. Sent by Paddle as part of the simulation.",
        title="SimulationEventRequest",
    )
    response: Response | None = Field(
        None,
        description="Information about the response. Sent by the responding server for the notification setting.",
        title="SimulationEventResponse",
    )
    created_at: CreatedAt | None = None
    updated_at: UpdatedAt | None = None


class SimulationRunScenario(BaseModel):
    id: SimulationRunId | None = None
    status: SimulationRunStatus | None = None
    created_at: CreatedAt | None = None
    updated_at: UpdatedAt | None = None
    type: SimulationScenarioEventsType | None = Field(
        None,
        description="Scenario for this simulation. Scenario simulations play all events sent for a subscription lifecycle event.",
    )


class SimulationRunScenarioIncludes(SimulationRunScenario):
    events: list[SimulationEvent] | None = Field(
        None,
        description="""Events associated with this simulation run. Paddle creates a list of events for each simulation runs. Returned when the
`include` parameter is used with the `events` value.""",
        title="SimulationEvent",
    )


class SimulationRunSingleEvent(BaseModel):
    id: SimulationRunId | None = None
    status: SimulationRunStatus | None = None
    created_at: CreatedAt | None = None
    updated_at: UpdatedAt | None = None
    type: EventTypeName | None = Field(
        None,
        description="Single event sent for this simulation, in the format `entity.event_type`.",
    )


class SimulationRunSingleEventIncludes(SimulationRunSingleEvent):
    events: list[SimulationEvent] | None = Field(
        None,
        description="""Events associated with this simulation run. Paddle creates a list of events for each simulation runs. Returned when the
`include` parameter is used with the `events` value.""",
        title="SimulationEvent",
    )


class SimulationStandardEvents(BaseModel):
    id: SimulationId | None = None
    status: Status | None = "active"
    notification_setting_id: NotificationSettingId | None = Field(
        None,
        description="Paddle ID of the notification setting where this simulation is sent, prefixed with `ntfset_`.",
    )
    name: str | None = Field(None, description="Name of this simulation.")
    type: EventTypeName | None = Field(
        None,
        description="Single event sent for this simulation, in the format `entity.event_type`.",
    )
    payload: dict[str, Any] | None = Field(None, description="Simulation payload.")
    last_run_at: Timestamp | None = Field(
        None,
        description="RFC 3339 datetime string of when this simulation was last run. `null` until run. Set automatically by Paddle.",
    )
    created_at: CreatedAt | None = None
    updated_at: UpdatedAt | None = None


class SimulationStandardEventsUpdate(BaseModel):
    notification_setting_id: NotificationSettingId | None = Field(
        None,
        description="Paddle ID of the notification setting where this simulation is sent, prefixed with `ntfset_`.",
    )
    name: str | None = Field(None, description="Name of this simulation.")
    status: Status | None = None
    type: EventTypeName | None = Field(
        None,
        description="Single event sent for this simulation, in the format `entity.event_type`.",
    )
    payload: dict[str, Any] | None = Field(
        None,
        description="Simulation payload. Pass a JSON object that matches the schema for an event type to simulate a custom payload. Set to `null` to clear and populate with a demo example.",
    )


class SimulationScenarioConfig1(BaseModel):
    subscription_cancellation: SimulationConfigSubscriptionCancellation | None = None
    subscription_creation: SimulationConfigSubscriptionCreation | None = None
    subscription_pause: SimulationConfigSubscriptionPause | None = None
    subscription_renewal: SimulationConfigSubscriptionRenewal | None = None
    subscription_resume: SimulationConfigSubscriptionResume | None = None


class SimulationScenarioConfig(RootModel[SimulationScenarioConfig1 | None]):
    root: SimulationScenarioConfig1 | None = Field(
        ...,
        description="Configuration for this scenario simulation. Determines which granular flow is simulated and what entities are used to populate webhook payloads with.",
        title="SimulationScenarioConfig",
    )


class SimulationScenarioCreateConfig(
    RootModel[
        SimulationConfigSubscriptionCancellationCreate
        | SimulationConfigSubscriptionCreationCreate
        | SimulationConfigSubscriptionPauseCreate
        | SimulationConfigSubscriptionRenewalCreate
        | SimulationConfigSubscriptionResumeCreate
        | None
    ]
):
    root: (
        SimulationConfigSubscriptionCancellationCreate
        | SimulationConfigSubscriptionCreationCreate
        | SimulationConfigSubscriptionPauseCreate
        | SimulationConfigSubscriptionRenewalCreate
        | SimulationConfigSubscriptionResumeCreate
        | None
    ) = Field(
        ...,
        description="Configuration for this scenario simulation. Use to simulate more granular flows and populate payloads with your own entity data.",
        discriminator="type",
        title="SimulationScenarioCreateConfig",
    )


class SubscriptionScheduledChange(BaseModel):
    action: Action | None = Field(
        None,
        description="Kind of change that's scheduled to be applied to this subscription.",
        title="ScheduledChangeAction",
    )
    effective_at: Timestamp | None = Field(
        None,
        description="RFC 3339 datetime string of when this scheduled change takes effect.",
    )
    resume_at: Timestamp | None = Field(
        None,
        description="RFC 3339 datetime string of when a paused subscription should resume. Only used for `pause` scheduled changes.",
    )


class Address2(BaseModel):
    postal_code: Annotated[str, Field(max_length=200)] | None = Field(
        None,
        description="ZIP or postal code of this address. Include for more accurate tax calculations.",
        examples=["11105-1803"],
    )
    country_code: CountryCode = Field(
        ...,
        description="Supported two-letter ISO 3166-1 alpha-2 country code for this address.",
    )


class TransactionItemCreateBase(BaseModel):
    quantity: Annotated[int, Field(ge=1)] = Field(
        ..., description="Quantity of this item on the transaction."
    )
    proration: TransactionItemProration | None = Field(
        None,
        description="How proration was calculated for this item. Populated when a transaction is created from a subscription change, where `proration_billing_mode` was `prorated_immediately` or `prorated_next_billing_period`. Set automatically by Paddle.",
    )


class TransactionItemCreateWithPriceId(TransactionItemCreateBase):
    price_id: PriceId = Field(
        ...,
        description="Paddle ID of an existing catalog price to add to this transaction, prefixed with `pri_`.",
    )


class TransactionPaymentAttempt(BaseModel):
    payment_attempt_id: str | None = Field(
        None,
        description="UUID for this payment attempt.",
        examples=["497f776b-851d-4ebf-89ab-8ba0f75d2d6a"],
    )
    stored_payment_method_id: str | None = Field(
        None,
        description="UUID for the stored payment method used for this payment attempt. Deprecated - use `payment_method_id` instead.",
        examples=["7636e781-3969-49f4-9c77-8226232e28a6"],
    )
    payment_method_id: PaymentMethodId | None = Field(
        None,
        description="Paddle ID of the payment method used for this payment attempt, prefixed with `paymtd_`.",
    )
    amount: str | None = Field(
        None,
        description="Amount for collection in the lowest denomination of a currency (e.g. cents for USD).",
        examples=["1050"],
    )
    status: StatusPaymentAttempt | None = None
    error_code: ErrorCode | None = Field(
        None,
        description="Reason why a payment attempt failed. Returns `null` if payment captured successfully.",
    )
    method_details: MethodDetails | None = None
    created_at: CreatedAt | None = None
    captured_at: Timestamp | None = Field(
        None,
        description="RFC 3339 datetime string of when this payment was captured. `null` if `status` is not `captured`.",
    )


class UnitPriceOverride(BaseModel):
    model_config = ConfigDict(extra="forbid")
    country_codes: list[CountryCode] = Field(
        ...,
        description="Supported two-letter ISO 3166-1 alpha-2 country code. Customers located in the listed countries are charged the override price.",
        min_length=1,
    )
    unit_price: Money = Field(
        ...,
        description="Override price. This price applies to customers located in the countries for this unit price override.",
    )


class AddressPreview(BaseModel):
    postal_code: Annotated[str, Field(max_length=200)] | None = Field(
        None,
        description="ZIP or postal code of this address. Include for more accurate tax calculations.",
        examples=["11105-1803"],
    )
    country_code: CountryCode = Field(
        ...,
        description="Supported two-letter ISO 3166-1 alpha-2 country code for this address.",
    )


class AddressUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    description: Annotated[str, Field(max_length=1024)] | None = Field(
        None,
        description="Memorable description for this address.",
        examples=["Paddle.com"],
    )
    first_line: Annotated[str, Field(max_length=1024)] | None = Field(
        None, description="First line of this address.", examples=["3811 Ditmars Blvd"]
    )
    second_line: Annotated[str, Field(max_length=1024)] | None = Field(
        None, description="Second line of this address."
    )
    city: Annotated[str, Field(max_length=200)] | None = Field(
        None, description="City of this address.", examples=["Astoria"]
    )
    postal_code: Annotated[str, Field(max_length=200)] | None = Field(
        None,
        description="ZIP or postal code of this address. Required for some countries.",
        examples=["11105-1803"],
    )
    region: Annotated[str, Field(max_length=200)] | None = Field(
        None, description="State, county, or region of this address.", examples=["NY"]
    )
    country_code: CountryCode | None = Field(
        None,
        description="Supported two-letter ISO 3166-1 alpha-2 country code for this address.",
    )
    custom_data: CustomData | None = Field(
        None, description="Your own structured key-value data."
    )
    status: Status | None = None


class Item(AdjustmentItem):
    id: AdjustmentItemId | None = Field(
        None,
        description="Unique Paddle ID for this adjustment item, prefixed with `adjitm_`.",
    )


class Adjustment(BaseModel):
    id: AdjustmentId | None = None
    action: AdjustmentAction | None = None
    type: AdjustmentType | None = "partial"
    transaction_id: TransactionId | None = Field(
        None,
        description="Paddle ID of the transaction that this adjustment is for, prefixed with `txn_`.",
    )
    subscription_id: SubscriptionId | None = Field(
        None,
        description="""Paddle ID for the subscription related to this adjustment, prefixed with `sub_`.
Set automatically by Paddle based on the `subscription_id` of the related transaction.""",
    )
    customer_id: CustomerId | None = Field(
        None,
        description="""Paddle ID for the customer related to this adjustment, prefixed with `ctm_`.
Set automatically by Paddle based on the `customer_id` of the related transaction.""",
    )
    reason: str | None = Field(
        None,
        description="Why this adjustment was created. Appears in the Paddle dashboard. Retained for record-keeping purposes.",
    )
    credit_applied_to_balance: bool | None = Field(
        None,
        description="Whether this adjustment was applied to the related customer's credit balance. Only returned for `credit` adjustments.",
    )
    currency_code: CurrencyCode | None = Field(
        None,
        description="Three-letter ISO 4217 currency code for this adjustment. Set automatically by Paddle based on the `currency_code` of the related transaction.",
    )
    status: StatusAdjustment | None = None
    items: list[Item] | None = Field(
        None,
        description="List of items on this adjustment. Required if `type` is not populated or set to `partial`.",
        max_length=100,
        min_length=1,
    )
    totals: AdjustmentTotals | None = None
    payout_totals: AdjustmentPayoutTotals | None = Field(
        None,
        description="Breakdown of how this adjustment affects your payout balance.",
    )
    tax_rates_used: AdjustmentTaxRatesUsed | None = None
    created_at: CreatedAt | None = None
    updated_at: UpdatedAt | None = None


class AdjustmentCreate(BaseModel):
    id: AdjustmentId | None = None
    action: AdjustmentAction
    type: AdjustmentType | None = "partial"
    tax_mode: AdjustmentTaxMode | None = "internal"
    transaction_id: TransactionId = Field(
        ...,
        description="""Paddle ID of the transaction that this adjustment is for, prefixed with `txn_`.

Automatically-collected transactions must be `completed`; manually-collected transactions must have a status of `billed` or `past_due`

You can't create an adjustment for a transaction that has a refund that's pending approval.""",
    )
    subscription_id: SubscriptionId | None = Field(
        None,
        description="""Paddle ID for the subscription related to this adjustment, prefixed with `sub_`.
Set automatically by Paddle based on the `subscription_id` of the related transaction.""",
    )
    customer_id: CustomerId | None = Field(
        None,
        description="""Paddle ID for the customer related to this adjustment, prefixed with `ctm_`.
Set automatically by Paddle based on the `customer_id` of the related transaction.""",
    )
    reason: str = Field(
        ...,
        description="Why this adjustment was created. Appears in the Paddle dashboard. Retained for recordkeeping purposes.",
    )
    credit_applied_to_balance: bool | None = Field(
        None,
        description="Whether this adjustment was applied to the related customer's credit balance. Only returned for `credit` adjustments.",
    )
    currency_code: CurrencyCode | None = Field(
        None,
        description="Three-letter ISO 4217 currency code for this adjustment. Set automatically by Paddle based on the `currency_code` of the related transaction.",
    )
    status: StatusAdjustment | None = None
    items: list[Item] | None = Field(
        None,
        description="List of transaction items to adjust. Required if `type` is not populated or set to `partial`.",
        max_length=100,
        min_length=1,
    )
    totals: AdjustmentTotals | None = None
    payout_totals: AdjustmentPayoutTotals | None = Field(
        None,
        description="Breakdown of how this adjustment affects your payout balance.",
    )
    created_at: CreatedAt | None = None
    updated_at: UpdatedAt | None = None


class AdjustmentPreview(BaseModel):
    transaction_id: TransactionId = Field(
        ...,
        description="Paddle ID for this transaction entity that this adjustment relates to, prefixed with `txn_`.",
    )
    tax_mode: AdjustmentTaxMode | None = "internal"
    items: list[AdjustmentItem] = Field(
        ...,
        description="List of transaction items that this adjustment is for.",
        max_length=100,
    )
    totals: AdjustmentTotals | None = Field(
        None, description="Calculated totals for this adjustment."
    )


class Error(BaseModel):
    error: Error1 | None = Field(None, description="Represents an error.")
    meta: Meta | None = None


class ImportMeta(BaseModel):
    external_id: ExternalId | None = None
    imported_from: MigrationProvider = Field(
        ...,
        description="Name of the platform or provider where this entity was imported from.",
    )


class Price(BaseModel):
    id: PriceId | None = None
    product_id: ProductId | None = Field(
        None,
        description="Paddle ID for the product that this price is for, prefixed with `pro_`.",
    )
    description: Annotated[str, Field(min_length=2, max_length=500)] | None = Field(
        None,
        description="Internal description for this price, not shown to customers. Typically notes for your team.",
    )
    type: CatalogType | None = "standard"
    name: PriceName | None = None
    billing_cycle: Duration | None = Field(
        None,
        description="How often this price should be charged. `null` if price is non-recurring (one-time).",
    )
    trial_period: PriceTrialDuration | None = Field(
        None,
        description="Trial period for the product related to this price. The billing cycle begins once the trial period is over. `null` for no trial period. Requires `billing_cycle`.",
    )
    tax_mode: TaxMode | None = "account_setting"
    unit_price: Money | None = Field(
        None,
        description="Base price. This price applies to all customers, except for customers located in countries where you have `unit_price_overrides`.",
    )
    unit_price_overrides: list[UnitPriceOverride] | None = Field(
        None,
        description="List of unit price overrides. Use to override the base price with a custom price and currency for a country or group of countries.",
        max_length=250,
    )
    quantity: PriceQuantity | None = Field(
        None,
        description="Limits on how many times the related product can be purchased at this price. Useful for discount campaigns.",
    )
    status: Status | None = "active"
    custom_data: CustomData | None = Field(
        None, description="Your own structured key-value data."
    )
    import_meta: ImportMeta | None = Field(
        None,
        description="Import information for this entity. `null` if this entity is not imported.",
    )
    created_at: CreatedAt | None = None
    updated_at: UpdatedAt | None = None


class PriceCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: PriceId | None = None
    description: Annotated[str, Field(min_length=2, max_length=500)] = Field(
        ...,
        description="Internal description for this price, not shown to customers. Typically notes for your team.",
    )
    type: CatalogType | None = Field(
        "standard",
        description="Type of item. Standard items are considered part of your catalog and are shown in the Paddle dashboard. If omitted, defaults to `standard`.",
    )
    name: PriceName | None = None
    product_id: ProductId = Field(
        ...,
        description="Paddle ID for the product that this price is for, prefixed with `pro_`.",
    )
    billing_cycle: Duration | None = Field(
        None,
        description="How often this price should be charged. `null` if price is non-recurring (one-time). If omitted, defaults to `null`.",
    )
    trial_period: PriceTrialDuration | None = Field(
        None,
        description="""Trial period for the product related to this price. The billing cycle begins once the trial period is over.
`null` for no trial period. Requires `billing_cycle`. If omitted, defaults to `null`.""",
    )
    tax_mode: TaxMode | None = Field(
        "account_setting",
        description="How tax is calculated for this price. If omitted, defaults to `account_setting`.",
    )
    unit_price: Money = Field(
        ...,
        description="Base price. This price applies to all customers, except for customers located in countries where you have `unit_price_overrides`.",
    )
    unit_price_overrides: list[UnitPriceOverride] | None = Field(
        None,
        description="List of unit price overrides. Use to override the base price with a custom price and currency for a country or group of countries.",
        max_length=250,
    )
    quantity: PriceQuantity | None = Field(
        None,
        description="Limits on how many times the related product can be purchased at this price. Useful for discount campaigns. If omitted, defaults to 1-100.",
    )
    custom_data: CustomData | None = Field(
        None, description="Your own structured key-value data."
    )
    import_meta: ImportMeta | None = Field(
        None,
        description="Import information for this entity. `null` if this entity is not imported.",
    )


class Product(BaseModel):
    id: ProductId | None = None
    name: ProductName | None = None
    description: Annotated[str, Field(max_length=2048)] | None = Field(
        None, description="Short description for this product."
    )
    type: CatalogType | None = "standard"
    tax_category: TaxCategory | None = None
    image_url: ImageUrl | EmptyString | None = Field(
        None,
        description="Image for this product. Included in the checkout and on some customer documents.",
    )
    custom_data: CustomData | None = Field(
        None, description="Your own structured key-value data."
    )
    status: Status | None = "active"
    import_meta: ImportMeta | None = Field(
        None,
        description="Import information for this entity. `null` if this entity is not imported.",
    )
    created_at: CreatedAt | None = None
    updated_at: UpdatedAt | None = None


class PriceIncludes(Price):
    product: Product | None = Field(
        None,
        description="Related product for this price. Returned when the `include` parameter is used with the `product` value.",
    )


class PricePreview(BaseModel):
    id: PriceId | None = Field(
        None,
        description="""Unique Paddle ID for this price, prefixed with `pri_`.
The value is null for custom prices being previewed.""",
    )
    product_id: ProductId | None = Field(
        None,
        description="""Paddle ID for the product that this price is for, prefixed with `pro_`.
The value is null for custom products being previewed.""",
    )
    description: Annotated[str, Field(min_length=2, max_length=500)] | None = Field(
        None,
        description="Internal description for this price, not shown to customers. Typically notes for your team.",
    )
    type: CatalogType | None = "standard"
    name: PriceName | None = None
    billing_cycle: Duration | None = Field(
        None,
        description="How often this price should be charged. `null` if price is non-recurring (one-time).",
    )
    trial_period: Duration | None = Field(
        None,
        description="Trial period for the product related to this price. The billing cycle begins once the trial period is over. `null` for no trial period. Requires `billing_cycle`.",
    )
    tax_mode: TaxMode | None = "account_setting"
    unit_price: Money | None = Field(
        None,
        description="Base price. This price applies to all customers, except for customers located in countries where you have `unit_price_overrides`.",
    )
    unit_price_overrides: list[UnitPriceOverride] | None = Field(
        None,
        description="List of unit price overrides. Use to override the base price with a custom price and currency for a country or group of countries.",
        max_length=250,
    )
    quantity: PriceQuantity | None = Field(
        None,
        description="Limits on how many times the related product can be purchased at this price. Useful for discount campaigns.",
    )
    status: Status | None = "active"
    custom_data: CustomData | None = Field(
        None, description="Your own structured key-value data."
    )
    import_meta: ImportMeta | None = Field(
        None,
        description="Import information for this entity. `null` if this entity is not imported.",
    )
    created_at: CreatedAt | None = None
    updated_at: UpdatedAt | None = None


class PriceUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    description: Annotated[str, Field(min_length=2, max_length=500)] | None = Field(
        None,
        description="Internal description for this price, not shown to customers. Typically notes for your team.",
    )
    type: CatalogType | None = "standard"
    name: PriceName | None = None
    billing_cycle: Duration | None = Field(
        None,
        description="How often this price should be charged. `null` if price is non-recurring (one-time).",
    )
    trial_period: Duration | None = Field(
        None,
        description="Trial period for the product related to this price. The billing cycle begins once the trial period is over. `null` for no trial period. Requires `billing_cycle`.",
    )
    tax_mode: TaxMode | None = "account_setting"
    unit_price: Money | None = Field(
        None,
        description="Base price. This price applies to all customers, except for customers located in countries where you have `unit_price_overrides`.",
    )
    unit_price_overrides: list[UnitPriceOverride] | None = Field(
        None,
        description="List of unit price overrides. Use to override the base price with a custom price and currency for a country or group of countries.",
        max_length=250,
    )
    quantity: PriceQuantity | None = Field(
        None,
        description="Limits on how many times the related product can be purchased at this price. Useful for discount campaigns.",
    )
    status: Status | None = None
    custom_data: CustomData | None = Field(
        None, description="Your own structured key-value data."
    )


class ProductCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: ProductId | None = None
    name: Annotated[str, Field(min_length=1, max_length=200)] = Field(
        ..., description="Name of this product."
    )
    description: Annotated[str, Field(max_length=2048)] | None = Field(
        None, description="Short description for this product."
    )
    type: CatalogType | None = Field(
        "standard",
        description="Type of item. Standard items are considered part of your catalog and are shown in the Paddle dashboard. If omitted, defaults to `standard`.",
    )
    tax_category: TaxCategory
    image_url: AnyUrl | Annotated[str, Field(min_length=0, max_length=0)] | None = (
        Field(
            None,
            description="Image for this product. Included in the checkout and on some customer documents.",
        )
    )
    custom_data: CustomData | None = Field(
        None, description="Your own structured key-value data."
    )
    import_meta: ImportMeta | None = Field(
        None,
        description="Import information for this entity. `null` if this entity is not imported.",
    )


class ProductIncludes(Product):
    prices: list[Price] | None = Field(
        None,
        description="Prices for this product. Returned when the `include` parameter is used with the `prices` value.",
    )


class ProductPreview(BaseModel):
    id: ProductId | None = Field(
        None,
        description="""Unique Paddle ID for this product, prefixed with `pro_`.
The value is null for custom products being previewed.""",
    )
    name: ProductName | None = None
    description: Annotated[str, Field(max_length=2048)] | None = Field(
        None, description="Short description for this product."
    )
    type: CatalogType | None = "standard"
    tax_category: TaxCategory | None = None
    image_url: ImageUrl | EmptyString | None = Field(
        None,
        description="Image for this product. Included in the checkout and on some customer documents.",
    )
    custom_data: CustomData | None = Field(
        None, description="Your own structured key-value data."
    )
    status: Status | None = "active"
    import_meta: ImportMeta | None = Field(
        None,
        description="Import information for this entity. `null` if this entity is not imported.",
    )
    created_at: CreatedAt | None = None
    updated_at: UpdatedAt | None = None


class ReportAdjustments(ReportBase):
    type: ReportTypeAdjustments = Field(..., description="Type of report to create.")
    filters: ReportFilterAdjustments | None = Field(
        None,
        description="Filter criteria for this report. If omitted, reports are filtered to include data updated in the last 30 days. This means `updated_at` is greater than or equal to (`gte`) the date 30 days ago from the time the report was generated.",
    )


class ReportBalance(ReportBase):
    type: Type8 = Field(
        ...,
        description="Type of report to create.",
        examples=["balance"],
        title="BalanceReportType",
    )
    filters: ReportFilterBalance | None = Field(
        None,
        description="Filter criteria for this report. If omitted, reports are filtered to include data updated in the last 30 days. This means `updated_at` is greater than or equal to (`gte`) the date 30 days ago from the time the report was generated.",
    )


class SimulationRun(RootModel[SimulationRunSingleEvent | SimulationRunScenario]):
    root: SimulationRunSingleEvent | SimulationRunScenario = Field(
        ..., description="Represents a simulation run entity.", title="SimulationRun"
    )


class SimulationRunIncludes(
    RootModel[SimulationRunSingleEventIncludes | SimulationRunScenarioIncludes]
):
    root: SimulationRunSingleEventIncludes | SimulationRunScenarioIncludes = Field(
        ...,
        description="Represents a simulation run entity.",
        title="SimulationRunIncludes",
    )


class SimulationScenarioEvents(BaseModel):
    id: SimulationId | None = None
    status: Status | None = "active"
    notification_setting_id: NotificationSettingId | None = Field(
        None,
        description="Paddle ID of the notification setting where this simulation is sent, prefixed with `ntfset_`.",
    )
    name: str | None = Field(None, description="Name of this simulation.")
    type: SimulationScenarioEventsType | None = Field(
        None,
        description="Scenario for this simulation. Scenario simulations play all events sent for a subscription lifecycle event.",
    )
    config: SimulationScenarioConfig | None = Field(
        None,
        description="Configuration for this scenario simulation. Determines which granular flow is simulated and what entities are used to populate webhook payloads with.",
    )
    last_run_at: Timestamp | None = Field(
        None,
        description="RFC 3339 datetime string of when this simulation was last run. `null` until run. Set automatically by Paddle.",
    )
    created_at: CreatedAt | None = None
    updated_at: UpdatedAt | None = None


class SimulationScenarioEventsCreate(BaseModel):
    notification_setting_id: NotificationSettingId = Field(
        ...,
        description="Paddle ID of the notification setting where this simulation is sent, prefixed with `ntfset_`.",
    )
    name: str = Field(..., description="Name of this simulation.")
    type: SimulationScenarioEventsType = Field(
        ...,
        description="Scenario for this simulation. Scenario simulations play all events sent for a subscription lifecycle event.",
    )
    config: SimulationScenarioCreateConfig | None = Field(
        None,
        description="Configuration for this scenario simulation. Use to simulate more granular flows and populate payloads with your own entity data. If omitted, Paddle simulates the default scenario flow and populates payloads with demo examples.",
    )


class SimulationScenarioEventsUpdate(BaseModel):
    notification_setting_id: NotificationSettingId | None = Field(
        None,
        description="Paddle ID of the notification setting where this simulation is sent, prefixed with `ntfset_`.",
    )
    name: str | None = Field(None, description="Name of this simulation.")
    status: Status | None = None
    type: SimulationScenarioEventsType | None = Field(
        None,
        description="Scenario for this simulation. Scenario simulations play all events sent for a subscription lifecycle event.",
    )
    config: SimulationScenarioCreateConfig | None = Field(
        None,
        description="Configuration for this scenario simulation. Use to simulate more granular flows and populate payloads with your own entity data. If omitted, Paddle simulates the default scenario flow and populates payloads with demo examples.",
    )


class SimulationUpdate(
    RootModel[SimulationStandardEventsUpdate | SimulationScenarioEventsUpdate]
):
    root: SimulationStandardEventsUpdate | SimulationScenarioEventsUpdate = Field(
        ...,
        description="Represents a simulation entity when updating.",
        title="SimulationUpdate",
    )


class Price2(BaseModel):
    product_id: ProductId = Field(
        ...,
        description="Paddle ID for the product that this price is for, prefixed with `pro_`.",
    )
    description: Annotated[str, Field(min_length=2, max_length=200)] = Field(
        ...,
        description="Internal description for this price, not shown to customers. Typically notes for your team.",
    )
    name: Annotated[str, Field(min_length=1, max_length=50)] | None = Field(
        None,
        description="Name of this price, shown to customers at checkout and on invoices. Typically describes how often the related product bills.",
    )
    tax_mode: TaxMode | None = "account_setting"
    unit_price: Money = Field(
        ...,
        description="Base price. This price applies to all customers, except for customers located in countries where you have `unit_price_overrides`.",
    )
    unit_price_overrides: list[UnitPriceOverride] | None = Field(
        None,
        description="List of unit price overrides. Use to override the base price with a custom price and currency for a country or group of countries.",
    )
    quantity: PriceQuantity | None = Field(
        None,
        description="Limits on how many times the related product can be purchased at this price. Useful for discount campaigns. If omitted, defaults to 1-100.",
    )
    custom_data: CustomData | None = Field(
        None, description="Your own structured key-value data."
    )


class SubscriptionChargeCreateWithPrice(BaseModel):
    quantity: Annotated[int, Field(ge=1)] = Field(
        ..., description="Quantity to bill for.", examples=[5]
    )
    price: Price2 = Field(
        ...,
        description="Price object for a non-catalog item to bill for. Include a `product_id` to relate this non-catalog price to an existing catalog price.",
        title="SubscriptionChargeCreateWithPrice",
    )


class Price3(BaseModel):
    description: Annotated[str, Field(min_length=2, max_length=200)] = Field(
        ...,
        description="Internal description for this price, not shown to customers. Typically notes for your team.",
    )
    name: Annotated[str, Field(min_length=1, max_length=50)] | None = Field(
        None,
        description="Name of this price, shown to customers at checkout and on invoices. Typically describes how often the related product bills.",
    )
    tax_mode: TaxMode | None = "account_setting"
    unit_price: Money = Field(
        ...,
        description="Base price. This price applies to all customers, except for customers located in countries where you have `unit_price_overrides`.",
    )
    unit_price_overrides: list[UnitPriceOverride] | None = Field(
        None,
        description="List of unit price overrides. Use to override the base price with a custom price and currency for a country or group of countries.",
    )
    quantity: PriceQuantity | None = Field(
        None,
        description="Limits on how many times the related product can be purchased at this price. Useful for discount campaigns. If omitted, defaults to 1-100.",
    )
    custom_data: CustomData | None = Field(
        None, description="Your own structured key-value data."
    )
    product: TransactionSubscriptionProductCreate = Field(
        ..., description="Product object for a non-catalog item to charge for."
    )


class SubscriptionChargeCreateWithPriceAndProduct(BaseModel):
    quantity: Annotated[int, Field(ge=1)] = Field(
        ..., description="Quantity to bill for.", examples=[5]
    )
    price: Price3 = Field(
        ...,
        description="Price object for a non-catalog item to charge for. Include a `product` object to create a non-catalog product for this non-catalog price.",
        title="SubscriptionChargeCreateWithProduct",
    )


class Address1(BaseModel):
    id: AddressId | None = None
    customer_id: CustomerId | None = Field(
        None,
        description="Paddle ID for the customer related to this address, prefixed with `cus_`.",
    )
    description: AddressDescription | None = None
    first_line: AddressFirstLine | None = None
    second_line: AddressSecondLine | None = None
    city: AddressCity | None = None
    postal_code: AddressPostalCode | None = None
    region: AddressRegion | None = None
    country_code: CountryCode | None = Field(
        None,
        description="Supported two-letter ISO 3166-1 alpha-2 country code for this address.",
    )
    custom_data: CustomData | None = Field(
        None, description="Your own structured key-value data."
    )
    status: Status | None = "active"
    created_at: CreatedAt | None = None
    updated_at: UpdatedAt | None = None
    import_meta: ImportMeta | None = Field(
        None,
        description="Import information for this entity. `null` if this entity is not imported.",
    )


class Business1(BaseModel):
    id: BusinessId | None = None
    customer_id: CustomerId | None = Field(
        None,
        description="Paddle ID for the customer related to this business, prefixed with `cus_`.",
    )
    name: Annotated[str, Field(min_length=1, max_length=1024)] | None = Field(
        None, description="Name of this business."
    )
    company_number: Annotated[str, Field(max_length=1024)] | None = Field(
        None, description="Company number for this business.", examples=["123456789"]
    )
    tax_identifier: Annotated[str, Field(max_length=1024)] | None = Field(
        None,
        description="Tax or VAT Number for this business.",
        examples=["AB0123456789"],
    )
    status: Status | None = "active"
    contacts: list[Contact] | None = Field(
        None,
        description="List of contacts related to this business, typically used for sending invoices.",
        max_length=100,
    )
    created_at: CreatedAt | None = None
    updated_at: UpdatedAt | None = None
    custom_data: CustomData | None = Field(
        None, description="Your own structured key-value data."
    )
    import_meta: ImportMeta | None = Field(
        None,
        description="Import information for this entity. `null` if this entity is not imported.",
    )


class Customer1(BaseModel):
    id: CustomerId | None = None
    name: Name | None = Field(
        None,
        description="Full name of this customer. Required when creating transactions where `collection_mode` is `manual` (invoices).",
    )
    email: Email | None = Field(None, description="Email address for this customer.")
    marketing_consent: bool | None = Field(
        False,
        description="""Whether this customer opted into marketing from you. `false` unless customers check the marketing consent box
when using Paddle Checkout. Set automatically by Paddle.""",
    )
    status: Status | None = "active"
    custom_data: CustomData | None = Field(
        None, description="Your own structured key-value data."
    )
    locale: str | None = Field(
        "en",
        description="Valid IETF BCP 47 short form locale tag. If omitted, defaults to `en`.",
    )
    created_at: CreatedAt | None = None
    updated_at: UpdatedAt | None = None
    import_meta: ImportMeta | None = Field(
        None,
        description="Import information for this entity. `null` if this entity is not imported.",
    )


class Discount2(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: DiscountId | None = None
    status: StatusDiscount | None = "active"
    description: Annotated[str, Field(min_length=1, max_length=500)] | None = Field(
        None,
        description="Short description for this discount for your reference. Not shown to customers.",
    )
    enabled_for_checkout: bool | None = Field(
        True,
        description="Whether this discount can be redeemed by customers at checkout (`true`) or not (`false`).",
    )
    code: DiscountCode | None = Field(
        None,
        description="Unique code that customers can use to redeem this discount at checkout. Not case-sensitive.",
    )
    type: Type12 | None = Field(
        None,
        description="Type of discount. Determines how this discount impacts the checkout or transaction total.",
        title="DiscountType",
    )
    mode: DiscountMode | None = "standard"
    amount: str | None = Field(
        None,
        description="Amount to discount by. For `percentage` discounts, must be an amount between `0.01` and `100`. For `flat` and `flat_per_seat` discounts, amount in the lowest denomination for a currency.",
    )
    currency_code: CurrencyCode | None = Field(
        None,
        description="Supported three-letter ISO 4217 currency code. Required where discount type is `flat` or `flat_per_seat`.",
    )
    recur: bool | None = Field(
        False,
        description="Whether this discount applies for multiple subscription billing periods (`true`) or not (`false`).",
    )
    maximum_recurring_intervals: Annotated[int, Field(ge=1)] | None = Field(
        None,
        description="""Number of subscription billing periods that this discount recurs for. Requires `recur`. `null` if this discount recurs forever.

Subscription renewals, midcycle changes, and one-time charges billed to a subscription aren't considered a redemption. `times_used` is not incremented in these cases.""",
    )
    usage_limit: Annotated[int, Field(ge=1)] | None = Field(
        None,
        description="""Maximum number of times this discount can be redeemed. This is an overall limit for this discount, rather than a per-customer limit. `null` if this discount can be redeemed an unlimited amount of times.

Paddle counts a usage as a redemption on a checkout, transaction, or the initial application against a subscription. Transactions created for subscription renewals, midcycle changes, and one-time charges aren't considered a redemption.""",
    )
    restrict_to: list[RestrictToItem] | None = Field(
        None,
        description="Product or price IDs that this discount is for. When including a product ID, all prices for that product can be discounted. `null` if this discount applies to all products and prices.",
    )
    expires_at: Timestamp | None = Field(
        None,
        description="""RFC 3339 datetime string of when this discount expires. Discount can no longer be redeemed after this date has elapsed. `null` if this discount can be redeemed forever.

Expired discounts can't be redeemed against transactions or checkouts, but can be applied when updating subscriptions.""",
    )
    custom_data: CustomData | None = Field(
        None, description="Your own structured key-value data."
    )
    times_used: int | None = Field(
        None,
        description="""How many times this discount has been redeemed. Automatically incremented by Paddle.

Paddle counts a usage as a redemption on a checkout, transaction, or subscription. Transactions created for subscription renewals, midcycle changes, and one-time charges aren't considered a redemption.""",
    )
    created_at: CreatedAt | None = None
    updated_at: UpdatedAt | None = None
    import_meta: ImportMeta | None = Field(
        None,
        description="Import information for this entity. `null` if this entity is not imported.",
    )


class TransactionPriceCreateBase(BaseModel):
    description: Annotated[str, Field(min_length=2, max_length=500)] = Field(
        ...,
        description="Internal description for this price, not shown to customers. Typically notes for your team.",
    )
    name: Annotated[str, Field(min_length=1, max_length=150)] | None = Field(
        None,
        description="Name of this price, shown to customers at checkout and on invoices. Typically describes how often the related product bills.",
    )
    billing_cycle: Duration | None = Field(
        None,
        description="How often this price should be charged. `null` if price is non-recurring (one-time).",
    )
    trial_period: Duration | None = Field(
        None,
        description="Trial period for the product related to this price. The billing cycle begins once the trial period is over. `null` for no trial period. Requires `billing_cycle`.",
    )
    tax_mode: TaxMode | None = "account_setting"
    unit_price: Money = Field(
        ...,
        description="Base price. This price applies to all customers, except for customers located in countries where you have `unit_price_overrides`.",
    )
    unit_price_overrides: list[UnitPriceOverride] | None = Field(
        None,
        description="List of unit price overrides. Use to override the base price with a custom price and currency for a country or group of countries.",
        max_length=250,
    )
    quantity: PriceQuantity | None = Field(
        None,
        description="Limits on how many times the related product can be purchased at this price. Useful for discount campaigns. If omitted, defaults to 1-100.",
    )
    custom_data: CustomData | None = Field(
        None, description="Your own structured key-value data."
    )


class TransactionPriceCreateWithProduct(TransactionPriceCreateBase):
    product: TransactionSubscriptionProductCreate = Field(
        ..., description="Product object for a non-catalog item to charge for."
    )


class TransactionPriceCreateWithProductId(TransactionPriceCreateBase):
    product_id: ProductId = Field(
        ...,
        description="Paddle ID for the product that this price is for, prefixed with `pro_`.",
    )


class TransactionItem(BaseModel):
    price_id: PriceId | None = Field(
        None,
        description="Paddle ID for the price to add to this transaction, prefixed with `pri_`.",
    )
    price: Price | None = None
    quantity: int = Field(..., description="Quantity of this item on the transaction.")
    proration: TransactionItemProration | None = Field(
        None,
        description="How proration was calculated for this item. Populated when a transaction is created from a subscription change, where `proration_billing_mode` was `prorated_immediately` or `prorated_next_billing_period`. Set automatically by Paddle.",
    )


class TransactionItemCreateWithPrice(TransactionItemCreateBase):
    price: TransactionPriceCreateWithProductId = Field(
        ...,
        description="Price object for a non-catalog item to charge for. Include a `product_id` to relate this non-catalog price to an existing catalog price.",
    )


class TransactionItemCreateWithPriceAndProduct(TransactionItemCreateBase):
    price: TransactionPriceCreateWithProduct = Field(
        ...,
        description="Price object for a non-catalog item to charge for. Include a `product` object to create a non-catalog product for this non-catalog price.",
    )


class TransactionLineItem(BaseModel):
    price_id: PriceId | None = Field(
        None,
        description="Paddle ID for the price related to this transaction line item, prefixed with `pri_`.",
    )
    quantity: int | None = Field(
        None, description="Quantity of this transaction line item."
    )
    proration: TransactionItemProration | None = Field(
        None,
        description="How proration was calculated for this item. Populated when a transaction is created from a subscription change, where `proration_billing_mode` was `prorated_immediately` or `prorated_next_billing_period`. Set automatically by Paddle.",
    )
    tax_rate: str | None = Field(
        None,
        description="Rate used to calculate tax for this transaction line item.",
        examples=["0.2"],
    )
    unit_totals: TotalsModel | None = Field(
        None,
        description="Breakdown of the charge for one unit in the lowest denomination of a currency (e.g. cents for USD).",
    )
    totals: TotalsModel | None = None
    product: Product | None = Field(
        None,
        description="Related product entity for this transaction line item price. Reflects the entity at the time it was added to the transaction.",
    )


class TransactionPreviewItem(TransactionPreviewItemBase):
    price: PricePreview


class TransactionPreviewItemWithPrice(TransactionPreviewItemBase):
    price: TransactionPriceCreateWithProductId = Field(
        ...,
        description="Price object for a non-catalog item to preview charging for. Include a `product_id` to relate this non-catalog price to an existing catalog price.",
    )


class TransactionPreviewItemWithPriceAndProduct(TransactionPreviewItemBase):
    price: TransactionPriceCreateWithProduct = Field(
        ...,
        description="Price object for a non-catalog item to preview charging for. Include a `product` object to create a non-catalog product for this non-catalog price.",
    )


class TransactionPreviewLineItem(BaseModel):
    price_id: PriceId | None = Field(
        None,
        description="""Paddle ID for the price related to this transaction line item, prefixed with `pri_`.
The value is null for custom prices being previewed.""",
    )
    quantity: int | None = Field(
        None, description="Quantity of this transaction line item."
    )
    tax_rate: str | None = Field(
        None,
        description="Rate used to calculate tax for this transaction line item.",
        examples=["0.2"],
    )
    unit_totals: TotalsModel | None = Field(
        None,
        description="Breakdown of the charge for one unit in the lowest denomination of a currency (e.g. cents for USD).",
    )
    totals: TotalsModel | None = None
    product: ProductPreview | None = Field(
        None, description="Related product entity for this transaction line item price."
    )
    proration: TransactionItemProration | None = Field(
        None, description="How proration was calculated for this item."
    )


class TransactionPricingPreviewBase(BaseModel):
    customer_id: CustomerId | None = Field(
        None,
        description="Paddle ID of the customer that this preview is for, prefixed with `ctm_`.",
    )
    address_id: AddressId | None = Field(
        None,
        description="Paddle ID of the address that this preview is for, prefixed with `add_`. Send one of `address_id`, `customer_ip_address`, or the `address` object when previewing.",
    )
    business_id: BusinessId | None = Field(
        None,
        description="Paddle ID of the business that this preview is for, prefixed with `biz_`.",
    )
    currency_code: CurrencyCode | None = Field(
        None, description="Supported three-letter ISO 4217 currency code."
    )
    discount_id: DiscountId | None = Field(
        None,
        description="Paddle ID of the discount applied to this preview, prefixed with `dsc_`.",
    )
    address: AddressPreview | None = Field(
        None,
        description="Address for this preview. Send one of `address_id`, `customer_ip_address`, or the `address` object when previewing.",
    )
    customer_ip_address: str | None = Field(
        None,
        description="IP address for this transaction preview. Send one of `address_id`, `customer_ip_address`, or the `address` object when previewing.",
    )


class TransactionPricingPreviewRequest(TransactionPricingPreviewBase):
    items: list[TransactionPricingPreviewItem] = Field(
        ...,
        description="List of items to preview price calculations for.",
        max_length=100,
        min_length=1,
    )


class AddressCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: AddressId | None = None
    description: Annotated[str, Field(max_length=1024)] | None = Field(
        None,
        description="Memorable description for this address.",
        examples=["Paddle.com"],
    )
    first_line: Annotated[str, Field(max_length=1024)] | None = Field(
        None, description="First line of this address.", examples=["3811 Ditmars Blvd"]
    )
    second_line: Annotated[str, Field(max_length=1024)] | None = Field(
        None, description="Second line of this address."
    )
    city: Annotated[str, Field(max_length=200)] | None = Field(
        None, description="City of this address.", examples=["Astoria"]
    )
    postal_code: Annotated[str, Field(max_length=200)] | None = Field(
        None,
        description="ZIP or postal code of this address. Required for some countries.",
        examples=["11105-1803"],
    )
    region: Annotated[str, Field(max_length=200)] | None = Field(
        None, description="State, county, or region of this address.", examples=["NY"]
    )
    country_code: CountryCode = Field(
        ...,
        description="Supported two-letter ISO 3166-1 alpha-2 country code for this address.",
    )
    custom_data: CustomData | None = Field(
        None, description="Your own structured key-value data."
    )
    import_meta: ImportMeta | None = Field(
        None,
        description="Import information for this entity. `null` if this entity is not imported.",
    )


class Business(BaseModel):
    id: BusinessId | None = None
    customer_id: CustomerId | None = Field(
        None,
        description="Paddle ID for the customer related to this business, prefixed with `cus_`.",
    )
    name: Annotated[str, Field(min_length=1, max_length=1024)] | None = Field(
        None, description="Name of this business."
    )
    company_number: Annotated[str, Field(max_length=1024)] | None = Field(
        None, description="Company number for this business.", examples=["123456789"]
    )
    tax_identifier: Annotated[str, Field(max_length=1024)] | None = Field(
        None,
        description="Tax or VAT Number for this business.",
        examples=["AB0123456789"],
    )
    status: Status | None = "active"
    contacts: list[Contact] | None = Field(
        None,
        description="List of contacts related to this business, typically used for sending invoices.",
        max_length=100,
    )
    created_at: CreatedAt | None = None
    updated_at: UpdatedAt | None = None
    custom_data: CustomData | None = Field(
        None, description="Your own structured key-value data."
    )
    import_meta: ImportMeta | None = Field(
        None,
        description="Import information for this entity. `null` if this entity is not imported.",
    )


class BusinessCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: BusinessId | None = None
    name: Annotated[str, Field(min_length=1, max_length=1024)] = Field(
        ..., description="Name of this business."
    )
    company_number: Annotated[str, Field(max_length=1024)] | None = Field(
        None, description="Company number for this business.", examples=["123456789"]
    )
    tax_identifier: Annotated[str, Field(max_length=1024)] | None = Field(
        None,
        description="Tax or VAT Number for this business.",
        examples=["AB0123456789"],
    )
    contacts: list[Contact1] | None = Field(
        None,
        description="List of contacts related to this business, typically used for sending invoices.",
        max_length=100,
    )
    custom_data: CustomData | None = Field(
        None, description="Your own structured key-value data."
    )
    import_meta: ImportMeta | None = Field(
        None,
        description="Import information for this entity. `null` if this entity is not imported.",
    )


class CustomerCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: CustomerId | None = None
    name: Name | None = Field(
        None,
        description="Full name of this customer. Required when creating transactions where `collection_mode` is `manual` (invoices).",
    )
    email: Email = Field(..., description="Email address for this customer.")
    marketing_consent: bool | None = Field(
        False,
        description="""Whether this customer opted into marketing from you. `false` unless customers check the marketing consent box
when using Paddle Checkout. Set automatically by Paddle.""",
    )
    custom_data: CustomData | None = Field(
        None, description="Your own structured key-value data."
    )
    locale: str | None = Field(
        "en",
        description="Valid IETF BCP 47 short form locale tag. If omitted, defaults to `en`.",
    )
    import_meta: ImportMeta | None = Field(
        None,
        description="Import information for this entity. `null` if this entity is not imported.",
    )


CustomerIncludes = Customer1


class CustomerUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Name | None = Field(
        None,
        description="Full name of this customer. Required when creating transactions where `collection_mode` is `manual` (invoices).",
    )
    email: Email | None = Field(None, description="Email address for this customer.")
    marketing_consent: bool | None = Field(
        False,
        description="""Whether this customer opted into marketing from you. `false` unless customers check the marketing consent box
when using Paddle Checkout. Set automatically by Paddle.""",
    )
    status: Status | None = None
    custom_data: CustomData | None = Field(
        None, description="Your own structured key-value data."
    )
    locale: str | None = Field(
        "en", description="Valid IETF BCP 47 short form locale tag."
    )
    import_meta: ImportMeta | None = Field(
        None,
        description="Import information for this entity. `null` if this entity is not imported.",
    )


class Discount(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: DiscountId | None = None
    status: StatusDiscount | None = "active"
    description: Annotated[str, Field(min_length=1, max_length=500)] | None = Field(
        None,
        description="Short description for this discount for your reference. Not shown to customers.",
    )
    enabled_for_checkout: bool | None = Field(
        True,
        description="Whether this discount can be redeemed by customers at checkout (`true`) or not (`false`).",
    )
    code: DiscountCode | None = Field(
        None,
        description="Unique code that customers can use to redeem this discount at checkout. Not case-sensitive.",
    )
    type: Type2 | None = Field(
        None,
        description="Type of discount. Determines how this discount impacts the checkout or transaction total.",
        title="DiscountType",
    )
    mode: DiscountMode | None = "standard"
    amount: str | None = Field(
        None,
        description="Amount to discount by. For `percentage` discounts, must be an amount between `0.01` and `100`. For `flat` and `flat_per_seat` discounts, amount in the lowest denomination for a currency.",
    )
    currency_code: CurrencyCode | None = Field(
        None,
        description="Supported three-letter ISO 4217 currency code. Required where discount type is `flat` or `flat_per_seat`.",
    )
    recur: bool | None = Field(
        False,
        description="Whether this discount applies for multiple subscription billing periods (`true`) or not (`false`).",
    )
    maximum_recurring_intervals: Annotated[int, Field(ge=1)] | None = Field(
        None,
        description="""Number of subscription billing periods that this discount recurs for. Requires `recur`. `null` if this discount recurs forever.

Subscription renewals, midcycle changes, and one-time charges billed to a subscription aren't considered a redemption. `times_used` is not incremented in these cases.""",
    )
    usage_limit: Annotated[int, Field(ge=1)] | None = Field(
        None,
        description="""Maximum number of times this discount can be redeemed. This is an overall limit for this discount, rather than a per-customer limit. `null` if this discount can be redeemed an unlimited amount of times.

Paddle counts a usage as a redemption on a checkout, transaction, or the initial application against a subscription. Transactions created for subscription renewals, midcycle changes, and one-time charges aren't considered a redemption.""",
    )
    restrict_to: list[RestrictToItem] | None = Field(
        None,
        description="Product or price IDs that this discount is for. When including a product ID, all prices for that product can be discounted. `null` if this discount applies to all products and prices.",
    )
    expires_at: Timestamp | None = Field(
        None,
        description="""RFC 3339 datetime string of when this discount expires. Discount can no longer be redeemed after this date has elapsed. `null` if this discount can be redeemed forever.

Expired discounts can't be redeemed against transactions or checkouts, but can be applied when updating subscriptions.""",
    )
    custom_data: CustomData | None = Field(
        None, description="Your own structured key-value data."
    )
    times_used: int | None = Field(
        None,
        description="""How many times this discount has been redeemed. Automatically incremented by Paddle.

Paddle counts a usage as a redemption on a checkout, transaction, or subscription. Transactions created for subscription renewals, midcycle changes, and one-time charges aren't considered a redemption.""",
    )
    created_at: CreatedAt | None = None
    updated_at: UpdatedAt | None = None
    import_meta: ImportMeta | None = Field(
        None,
        description="Import information for this entity. `null` if this entity is not imported.",
    )


class DiscountCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: DiscountId | None = None
    status: StatusDiscount | None = "active"
    description: Annotated[str, Field(min_length=1, max_length=500)] = Field(
        ...,
        description="Short description for this discount for your reference. Not shown to customers.",
    )
    enabled_for_checkout: bool | None = Field(
        True,
        description="Whether this discount can be redeemed by customers at checkout (`true`) or not (`false`).",
    )
    code: DiscountCode | None = Field(
        None,
        description="""Unique code that customers can use to redeem this discount at checkout. Use letters and numbers only, up to 32 characters. Not case-sensitive.

If omitted and `enabled_for_checkout` is `true`, Paddle generates a random 10-character code.""",
    )
    type: Type2 = Field(
        ...,
        description="Type of discount. Determines how this discount impacts the checkout or transaction total.",
        title="DiscountType",
    )
    mode: DiscountMode | None = Field(
        "standard",
        description="Discount mode. Standard discounts are considered part of your catalog and are shown in the Paddle dashboard. If omitted, defaults to `standard`.",
    )
    amount: str = Field(
        ...,
        description="Amount to discount by. For `percentage` discounts, must be an amount between `0.01` and `100`. For `flat` and `flat_per_seat` discounts, amount in the lowest denomination for a currency.",
    )
    currency_code: CurrencyCode | None = Field(
        None,
        description="Supported three-letter ISO 4217 currency code. Required where discount type is `flat` or `flat_per_seat`.",
    )
    recur: bool | None = Field(
        False,
        description="Whether this discount applies for multiple subscription billing periods (`true`) or not (`false`). If omitted, defaults to `false`.",
    )
    maximum_recurring_intervals: Annotated[int, Field(ge=1)] | None = Field(
        None,
        description="""Number of subscription billing periods that this discount recurs for. Requires `recur`. `null` if this discount recurs forever.

Subscription renewals, midcycle changes, and one-time charges billed to a subscription aren't considered a redemption. `times_used` is not incremented in these cases.""",
    )
    usage_limit: Annotated[int, Field(ge=1)] | None = Field(
        None,
        description="""Maximum number of times this discount can be redeemed. This is an overall limit for this discount, rather than a per-customer limit. `null` if this discount can be redeemed an unlimited amount of times.

Paddle counts a usage as a redemption on a checkout, transaction, or the initial application against a subscription. Transactions created for subscription renewals, midcycle changes, and one-time charges aren't considered a redemption.""",
    )
    restrict_to: list[RestrictToItem] | None = Field(
        None,
        description="Product or price IDs that this discount is for. When including a product ID, all prices for that product can be discounted. `null` if this discount applies to all products and prices.",
    )
    expires_at: Timestamp | None = Field(
        None,
        description="""RFC 3339 datetime string of when this discount expires. Discount can no longer be redeemed after this date has elapsed. `null` if this discount can be redeemed forever.

Expired discounts can't be redeemed against transactions or checkouts, but can be applied when updating subscriptions.""",
    )
    custom_data: CustomData | None = Field(
        None, description="Your own structured key-value data."
    )
    times_used: int | None = Field(
        None,
        description="""How many times this discount has been redeemed. Automatically incremented by Paddle.

Paddle counts a usage as a redemption on a checkout, transaction, or subscription. Transactions created for subscription renewals, midcycle changes, and one-time charges aren't considered a redemption.""",
    )
    created_at: CreatedAt | None = None
    updated_at: UpdatedAt | None = None
    import_meta: ImportMeta | None = Field(
        None,
        description="Import information for this entity. `null` if this entity is not imported.",
    )


class ItemSubscription(BaseModel):
    status: Status1 | None = Field(
        None,
        description="Status of this subscription item. Set automatically by Paddle.",
        title="SubscriptionItemStatus",
    )
    quantity: Annotated[float, Field(ge=1.0)] | None = Field(
        None, description="Quantity of this item on the subscription."
    )
    recurring: bool | None = Field(
        None, description="Whether this is a recurring item. `false` if one-time."
    )
    created_at: CreatedAt | None = Field(
        None,
        description="RFC 3339 datetime string of when this item was added to this subscription.",
    )
    updated_at: UpdatedAt | None = Field(
        None,
        description="RFC 3339 datetime string of when this item was last updated on this subscription.",
    )
    previously_billed_at: Timestamp | None = Field(
        None, description="RFC 3339 datetime string of when this item was last billed."
    )
    next_billed_at: Timestamp | None = Field(
        None,
        description="RFC 3339 datetime string of when this item is next scheduled to be billed.",
    )
    trial_dates: TimePeriod | None = Field(
        None, description="Trial dates for this item."
    )
    price: Price | None = Field(
        None,
        description="Related price entity for this item. This reflects the price entity at the time it was added to the subscription.",
    )
    product: Product | None = Field(
        None,
        description="Related product entity for this item. This reflects the product entity at the time it was added to the subscription.",
    )


class Report(
    RootModel[
        ReportAdjustments
        | ReportTransactions
        | ReportProductsPrices
        | ReportDiscounts
        | ReportBalance
    ]
):
    root: (
        ReportAdjustments
        | ReportTransactions
        | ReportProductsPrices
        | ReportDiscounts
        | ReportBalance
    ) = Field(..., description="Represents a report entity.", title="Report")


class Simulation(RootModel[SimulationStandardEvents | SimulationScenarioEvents]):
    root: SimulationStandardEvents | SimulationScenarioEvents = Field(
        ..., description="Represents a simulation entity.", title="Simulation"
    )


class SimulationCreate(
    RootModel[SimulationStandardEventsCreate | SimulationScenarioEventsCreate]
):
    root: SimulationStandardEventsCreate | SimulationScenarioEventsCreate = Field(
        ...,
        description="Represents a simulation entity when creating.",
        title="SimulationCreate",
    )


class Subscription1(BaseModel):
    id: SubscriptionId | None = None
    status: StatusSubscription | None = None
    customer_id: CustomerId | None = Field(
        None,
        description="Paddle ID of the customer that this subscription is for, prefixed with `ctm_`.",
    )
    address_id: AddressId | None = Field(
        None,
        description="Paddle ID of the address that this subscription is for, prefixed with `add_`.",
    )
    business_id: BusinessId | None = Field(
        None,
        description="Paddle ID of the business that this subscription is for, prefixed with `biz_`.",
    )
    currency_code: CurrencyCode | None = Field(
        None,
        description="Supported three-letter ISO 4217 currency code. Transactions for this subscription are created in this currency. Must be `USD`, `EUR`, or `GBP` if `collection_mode` is `manual`.",
    )
    created_at: CreatedAt | None = None
    updated_at: UpdatedAt | None = None
    started_at: Timestamp | None = Field(
        None,
        description="RFC 3339 datetime string of when this subscription started. This may be different from `first_billed_at` if the subscription started in trial.",
    )
    first_billed_at: Timestamp | None = Field(
        None,
        description="RFC 3339 datetime string of when this subscription was first billed. This may be different from `started_at` if the subscription started in trial.",
    )
    next_billed_at: Timestamp | None = Field(
        None,
        description="RFC 3339 datetime string of when this subscription is next scheduled to be billed.",
    )
    paused_at: Timestamp | None = Field(
        None,
        description="RFC 3339 datetime string of when this subscription was paused. Set automatically by Paddle when the pause subscription operation is used. `null` if not paused.",
    )
    canceled_at: Timestamp | None = Field(
        None,
        description="RFC 3339 datetime string of when this subscription was canceled. Set automatically by Paddle when the cancel subscription operation is used. `null` if not canceled.",
    )
    discount: DiscountSubscription | None = Field(
        None, description="Details of the discount applied to this subscription."
    )
    collection_mode: CollectionMode | None = Field(
        "automatic",
        description="How payment is collected for transactions created for this subscription. `automatic` for checkout, `manual` for invoices.",
    )
    billing_details: BillingDetails | None = Field(
        None,
        description="Details for invoicing. Required if `collection_mode` is `manual`.",
    )
    current_billing_period: TimePeriod | None = Field(
        None,
        description="Current billing period for this subscription. Set automatically by Paddle based on the billing cycle. `null` for `paused` and `canceled` subscriptions.",
    )
    billing_cycle: Duration | None = Field(
        None,
        description="How often this subscription renews. Set automatically by Paddle based on the prices on this subscription.",
    )
    scheduled_change: SubscriptionScheduledChange | None = Field(
        None,
        description="Change that's scheduled to be applied to a subscription. Use the pause subscription, cancel subscription, and resume subscription operations to create scheduled changes. `null` if no scheduled changes.",
    )
    management_urls: SubscriptionManagementUrls | None = None
    items: list[ItemSubscription] | None = Field(
        None,
        description="List of items on this subscription. Only recurring items are returned.",
        max_length=100,
        min_length=1,
    )
    custom_data: CustomData | None = Field(
        None, description="Your own structured key-value data."
    )
    import_meta: ImportMetaSubscription | None = Field(
        None,
        description="Import information for this entity. `null` if this entity is not imported.",
    )


class SubscriptionCharge(BaseModel):
    model_config = ConfigDict(extra="forbid")
    effective_from: EffectiveFrom = Field(
        ..., description="When one-time charges should be billed."
    )
    items: list[
        SubscriptionItemCreateWithPriceId
        | SubscriptionChargeCreateWithPrice
        | SubscriptionChargeCreateWithPriceAndProduct
    ] = Field(
        ...,
        description="""List of one-time charges to bill for. Only prices where the `billing_cycle` is `null` may be added.

You can charge for items that you've added to your catalog by passing the Paddle ID of an existing price entity, or you can charge for non-catalog items by passing a price object.

Non-catalog items can be for existing products, or you can pass a product object as part of your price to charge for a non-catalog product.""",
        max_length=100,
        min_length=1,
    )
    on_payment_failure: SubscriptionOnPaymentFailure | None = "prevent_change"


class LineItem(TransactionPreviewLineItem):
    proration: TransactionItemProration | None = Field(
        None, description="How proration was calculated for this item."
    )


class RecurringTransactionDetails(BaseModel):
    tax_rates_used: list[TaxRatesUsedItem4] | None = Field(
        None, description="List of tax rates applied to this transaction preview."
    )
    totals: TransactionTotals | None = Field(
        None,
        description="Breakdown of the total for a transaction preview. `fee` and `earnings` always return `null` for transaction previews.",
    )
    line_items: list[LineItem] | None = Field(
        None,
        description="Information about line items for this transaction preview. Different from transaction preview `items` as they include totals calculated by Paddle. Considered the source of truth for line item totals.",
    )


class SubscriptionItemCreateWithPrice(BaseModel):
    quantity: Annotated[int, Field(ge=1)] = Field(
        ..., description="Quantity to bill for.", examples=[5]
    )
    price: TransactionPriceCreateWithProductId = Field(
        ...,
        description="Price object for a non-catalog item to bill for. Include a `product_id` to relate this non-catalog price to an existing catalog price.",
    )


class SubscriptionItemCreateWithPriceAndProduct(BaseModel):
    quantity: Annotated[int, Field(ge=1)] = Field(
        ..., description="Quantity to bill for.", examples=[5]
    )
    price: TransactionPriceCreateWithProduct = Field(
        ...,
        description="Price object for a non-catalog item to charge for. Include a `product` object to create a non-catalog product for this non-catalog price.",
    )


class SubscriptionRecurringTransactionDetails(BaseModel):
    tax_rates_used: list[TaxRatesUsedItem4] | None = Field(
        None, description="List of tax rates applied to this transaction preview."
    )
    totals: TransactionTotals | None = Field(
        None,
        description="Breakdown of the total for a transaction preview. `fee` and `earnings` always return `null` for transaction previews.",
    )
    line_items: list[LineItem] | None = Field(
        None,
        description="Information about line items for this transaction preview. Different from transaction preview `items` as they include totals calculated by Paddle. Considered the source of truth for line item totals.",
    )


class SubscriptionTransactionPreviewDetails(BaseModel):
    tax_rates_used: list[TaxRatesUsedItem4] | None = Field(
        None, description="List of tax rates applied to this transaction preview."
    )
    totals: TransactionTotals | None = Field(
        None,
        description="Breakdown of the total for a transaction preview. `fee` and `earnings` always return `null` for transaction previews.",
    )
    line_items: list[LineItem] | None = Field(
        None,
        description="Information about line items for this transaction preview. Different from transaction preview `items` as they include totals calculated by Paddle. Considered the source of truth for line item totals.",
    )


class TransactionPreviewCreate(BaseModel):
    customer_id: CustomerId | None = Field(
        None,
        description="Paddle ID of the customer that this transaction preview is for, prefixed with `ctm_`.",
    )
    currency_code: CurrencyCode | None = Field(
        None, description="Supported three-letter ISO 4217 currency code."
    )
    discount_id: DiscountId | None = Field(
        None,
        description="Paddle ID of the discount applied to this transaction preview, prefixed with `dsc_`.",
    )
    ignore_trials: bool | None = Field(
        False,
        description="""Whether trials should be ignored for transaction preview calculations.

By default, recurring items with trials are considered to have a zero charge when previewing. Set to `true` to disable this.""",
    )
    items: list[
        TransactionPreviewItemWithPriceId
        | TransactionPreviewItemWithPrice
        | TransactionPreviewItemWithPriceAndProduct
    ] = Field(
        ...,
        description="""List of items to preview charging for. You can preview charging for items that you've added to your catalog by passing the Paddle ID of an existing price entity, or you can preview charging for non-catalog items by passing a price object.

Non-catalog items can be for existing products, or you can pass a product object as part of your price to preview charging for a non-catalog product.""",
    )


class TransactionPreviewCreateAddress(TransactionPreviewCreate):
    address: Address2 = Field(..., description="Address for this transaction preview.")


class TransactionPreviewCreateIpAddress(TransactionPreviewCreate):
    customer_ip_address: str = Field(
        ..., description="IP address for this transaction preview."
    )


class TransactionPreviewCreatePaddleIds(TransactionPreviewCreate):
    address_id: Annotated[str, Field(pattern="^add_[a-z\\d]{26}$")] = Field(
        ...,
        description="Paddle ID of the address that this transaction preview is for, prefixed with `add_`. Requires `customer_id`.",
    )
    business_id: BusinessId | None = Field(
        None,
        description="Paddle ID of the business that this transaction preview is for, prefixed with `biz_`.",
    )
    customer_id: CustomerId | None


class LineItem3(TransactionLineItem):
    id: TransactionItemId | None = None


class TransactionDetails(BaseModel):
    tax_rates_used: list[TaxRatesUsedItem] | None = Field(
        None, description="List of tax rates applied for this transaction."
    )
    totals: TransactionTotals | None = None
    adjusted_totals: TransactionTotalsAdjusted | None = None
    payout_totals: TransactionPayoutTotals | None = Field(
        None,
        description="Breakdown of the payout total for a transaction. `null` until the transaction is `completed`. Returned in your payout currency.",
    )
    adjusted_payout_totals: TransactionPayoutTotalsAdjusted | None = Field(
        None,
        description="Breakdown of the payout total for a transaction after adjustments. `null` until the transaction is `completed`.",
    )
    line_items: list[LineItem3] | None = Field(
        None,
        description="Information about line items for this transaction. Different from transaction `items` as they include totals calculated by Paddle. Considered the source of truth for line item totals.",
    )


class TransactionPreviewDetails(BaseModel):
    tax_rates_used: list[TaxRatesUsedItem4] | None = Field(
        None, description="List of tax rates applied to this transaction preview."
    )
    totals: TransactionTotals | None = Field(
        None,
        description="Breakdown of the total for a transaction preview. `fee` and `earnings` always return `null` for transaction previews.",
    )
    line_items: list[TransactionPreviewLineItem] | None = Field(
        None,
        description="Information about line items for this transaction preview. Different from transaction preview `items` as they include totals calculated by Paddle. Considered the source of truth for line item totals.",
    )


class TransactionPricingPreviewLineItemDiscount(BaseModel):
    discount: Discount | None = Field(
        None, description="Related discount entity for this preview line item."
    )
    total: str | None = Field(
        None,
        description="Total amount discounted as a result of this discount.",
        examples=["0"],
    )
    formatted_total: str | None = Field(
        None,
        description="Total amount discounted as a result of this discount in the format of a given currency. '",
        examples=["$0"],
    )


class SubscriptionUpdate(BaseModel):
    customer_id: CustomerId | None = Field(
        None,
        description="Paddle ID of the customer that this subscription is for, prefixed with `ctm_`. Include to change the customer for a subscription.",
    )
    address_id: AddressId | None = Field(
        None,
        description="Paddle ID of the address that this subscription is for, prefixed with `add_`. Include to change the address for a subscription.",
    )
    business_id: BusinessId | None = Field(
        None,
        description="Paddle ID of the business that this subscription is for, prefixed with `biz_`. Include to change the business for a subscription.",
    )
    currency_code: CurrencyCode | None = Field(
        None,
        description="Supported three-letter ISO 4217 currency code. Include to change the currency that a subscription bills in. When changing `collection_mode` to `manual`, you may need to change currency code to `USD`, `EUR`, or `GBP`.",
    )
    next_billed_at: AwareDatetime | None = Field(
        None,
        description="RFC 3339 datetime string of when this subscription is next scheduled to be billed. Include to change the next billing date.",
    )
    discount: Discount1 | None = Field(
        None,
        description="Details of the discount applied to this subscription. Include to add a discount to a subscription. `null` to remove a discount.",
        title="SubscriptionDiscountEffectiveFrom",
    )
    collection_mode: CollectionMode | None = Field(
        "automatic",
        description="How payment is collected for transactions created for this subscription. `automatic` for checkout, `manual` for invoices.",
    )
    billing_details: BillingDetailsUpdate | None = Field(
        None,
        description="Details for invoicing. Required if `collection_mode` is `manual`. `null` if changing `collection_mode` to `automatic`.",
    )
    scheduled_change: None = Field(
        None,
        description="Change that's scheduled to be applied to a subscription. When updating, you may only set to `null` to remove a scheduled change. Use the pause subscription, cancel subscription, and resume subscription operations to create scheduled changes.",
    )
    items: (
        list[
            SubscriptionUpdateItem
            | SubscriptionItemCreateWithPrice
            | SubscriptionItemCreateWithPriceAndProduct
        ]
        | None
    ) = Field(
        None,
        description="List of items on this subscription. Only recurring items may be added. Send the complete list of items that should be on this subscription, including existing items to retain.",
        max_length=100,
        min_length=1,
    )
    custom_data: CustomData | None = Field(
        None, description="Your own structured key-value data."
    )
    proration_billing_mode: SubscriptionUpdateProrationBillingMode | None = None
    on_payment_failure: SubscriptionOnPaymentFailure | None = "prevent_change"


class SubscriptionNextTransaction(BaseModel):
    billing_period: TimePeriod | None = Field(
        None, description="Billing period for the next transaction."
    )
    details: SubscriptionTransactionPreviewDetails | None = None
    adjustments: list[AdjustmentPreview] | None = Field(
        None, description="Preview of adjustments for the next transaction."
    )


class Transaction(BaseModel):
    id: TransactionId | None = None
    status: StatusTransaction | None = None
    customer_id: CustomerId | None = Field(
        None,
        description="Paddle ID of the customer that this transaction is for, prefixed with `ctm_`.",
    )
    address_id: AddressId | None = Field(
        None,
        description="Paddle ID of the address that this transaction is for, prefixed with `add_`.",
    )
    business_id: BusinessId | None = Field(
        None,
        description="Paddle ID of the business that this transaction is for, prefixed with `biz_`.",
    )
    custom_data: CustomData | None = Field(
        None, description="Your own structured key-value data."
    )
    currency_code: CurrencyCode | None = Field(
        None,
        description="Supported three-letter ISO 4217 currency code. Must be `USD`, `EUR`, or `GBP` if `collection_mode` is `manual`.",
    )
    origin: OriginTransaction | None = None
    subscription_id: SubscriptionId | None = Field(
        None,
        description="Paddle ID of the subscription that this transaction is for, prefixed with `sub_`.",
    )
    invoice_id: Annotated[str, Field(pattern="^inv_[a-z\\d]{26}$")] | None = Field(
        None,
        description="Paddle ID of the invoice that this transaction is related to, prefixed with `inv_`. Used for compatibility with the Paddle Invoice API, which is now deprecated. This field is scheduled to be removed in the next version of the Paddle API.",
        examples=["inv_01ghbk4xjn4qdsmstcwzgcgg35"],
    )
    invoice_number: DocumentNumber | None = Field(
        None,
        description="Invoice number for this transaction. Automatically generated by Paddle when you mark a transaction as `billed` where `collection_mode` is `manual`.",
    )
    collection_mode: CollectionMode | None = Field(
        "automatic",
        description="How payment is collected for this transaction. `automatic` for checkout, `manual` for invoices.",
    )
    discount_id: DiscountId | None = Field(
        None,
        description="Paddle ID of the discount applied to this transaction, prefixed with `dsc_`.",
    )
    billing_details: BillingDetails | None = Field(
        None,
        description="Details for invoicing. Required if `collection_mode` is `manual`.",
    )
    billing_period: TimePeriod | None = Field(
        None,
        description="Time period that this transaction is for. Set automatically by Paddle for subscription renewals to describe the period that charges are for.",
    )
    items: list[TransactionItem] | None = Field(
        None,
        description="List of items on this transaction. For calculated totals, use `details.line_items`.",
        max_length=100,
        min_length=1,
    )
    details: TransactionDetails | None = None
    payments: list[TransactionPaymentAttempt] | None = Field(
        None,
        description="List of payment attempts for this transaction, including successful payments. Sorted by `created_at` in descending order, so most recent attempts are returned first.",
    )
    checkout: Checkout | None = Field(
        None,
        description="Paddle Checkout details for this transaction. Returned for automatically-collected transactions and where `billing_details.enable_checkout` is `true` for manually-collected transactions; `null` otherwise.",
        title="TransactionCheckout",
    )
    created_at: CreatedAt | None = None
    updated_at: UpdatedAt | None = None
    billed_at: Timestamp | None = Field(
        None,
        description="RFC 3339 datetime string of when this transaction was marked as `billed`. `null` for transactions that aren't `billed` or `completed`. Set automatically by Paddle.",
    )
    revised_at: Timestamp | None = Field(
        None,
        description="RFC 3339 datetime string of when a transaction was revised. Revisions describe an update to customer information for a billed or completed transaction. `null` if not revised. Set automatically by Paddle.",
    )


class TransactionCreate(BaseModel):
    id: TransactionId | None = None
    status: StatusTransactionCreate | None = Field(
        None,
        description="""Status of this transaction. You may set a transaction to `billed` when creating,
or omit to let Paddle set the status. Transactions are created as `ready` if they have
an `address_id`, `customer_id`, and `items`, otherwise they are created as `draft`.

Marking as `billed` when creating is typically used when working with manually-collected
transactions as part of an invoicing workflow. Billed transactions cannot be updated, only canceled.""",
    )
    customer_id: CustomerId | None = Field(
        None,
        description="Paddle ID of the customer that this transaction is for, prefixed with `ctm_`. If omitted, transaction status is `draft`.",
    )
    address_id: AddressId | None = Field(
        None,
        description="Paddle ID of the address that this transaction is for, prefixed with `add_`. Requires `customer_id`. If omitted, transaction status is `draft`.",
    )
    business_id: BusinessId | None = Field(
        None,
        description="Paddle ID of the business that this transaction is for, prefixed with `biz_`. Requires `customer_id`. ",
    )
    custom_data: CustomData | None = Field(
        None, description="Your own structured key-value data."
    )
    currency_code: CurrencyCode | None = Field(
        None,
        description="Supported three-letter ISO 4217 currency code. Must be `USD`, `EUR`, or `GBP` if `collection_mode` is `manual`.",
    )
    origin: OriginTransaction | None = None
    subscription_id: SubscriptionId | None = Field(
        None,
        description="Paddle ID of the subscription that this transaction is for, prefixed with `sub_`.",
    )
    invoice_id: Annotated[str, Field(pattern="^inv_[a-z\\d]{26}$")] | None = Field(
        None,
        description="Paddle ID of the invoice that this transaction is related to, prefixed with `inv_`. Used for compatibility with the Paddle Invoice API, which is now deprecated. This field is scheduled to be removed in the next version of the Paddle API.",
        examples=["inv_01ghbk4xjn4qdsmstcwzgcgg35"],
    )
    invoice_number: str | None = Field(
        None,
        description="Invoice number for this transaction. Automatically generated by Paddle when you mark a transaction as `billed` where `collection_mode` is `manual`.",
        examples=["123-45678"],
    )
    collection_mode: CollectionMode | None = Field(
        "automatic",
        description="How payment is collected for this transaction. `automatic` for checkout, `manual` for invoices. If omitted, defaults to `automatic`.",
    )
    discount_id: DiscountId | None = Field(
        None,
        description="Paddle ID of the discount applied to this transaction, prefixed with `dsc_`.",
    )
    billing_details: BillingDetails | None = Field(
        None,
        description="Details for invoicing. Required if `collection_mode` is `manual`.",
    )
    billing_period: TimePeriod | None = Field(
        None,
        description="Time period that this transaction is for. Set automatically by Paddle for subscription renewals to describe the period that charges are for.",
    )
    items: list[
        TransactionItemCreateWithPriceId
        | TransactionItemCreateWithPrice
        | TransactionItemCreateWithPriceAndProduct
    ] = Field(
        ...,
        description="""List of items to charge for. You can charge for items that you've added to your catalog by passing the Paddle ID of an existing price entity, or you can charge for non-catalog items by passing a price object.

Non-catalog items can be for existing products, or you can pass a product object as part of your price to charge for a non-catalog product.""",
        max_length=100,
        min_length=1,
    )
    details: TransactionDetails | None = None
    payments: list[TransactionPaymentAttempt] | None = Field(
        None,
        description="List of payment attempts for this transaction, including successful payments. Sorted by `created_at` in descending order, so most recent attempts are returned first.",
    )
    checkout: Checkout1 | None = Field(
        None,
        description="Paddle Checkout details for this transaction. You may pass a URL when creating or updating an automatically-collected transaction, or when creating or updating a manually-collected transaction where `billing_details.enable_checkout` is `true`.",
        title="TransactionCheckout",
    )
    created_at: CreatedAt | None = None
    updated_at: UpdatedAt | None = None
    billed_at: Timestamp | None = Field(
        None,
        description="RFC 3339 datetime string of when this transaction was marked as `billed`. `null` for transactions that aren't `billed` or `completed`. Set automatically by Paddle.",
    )


class TransactionIncludes(Transaction):
    address: Address1 | None = Field(
        None,
        description="Address for this transaction. Reflects the entity at the time it was added to the transaction, or its revision if `revised_at` is not `null`. Returned when the `include` parameter is used with the `address` value and the transaction has an `address_id`.",
    )
    adjustments: list[Adjustment] | None = Field(
        None,
        description="List of adjustments for this transaction. Returned when the `include` parameter is used with the `adjustment` value and the transaction has adjustments.",
    )
    adjustments_totals: AdjustmentsTotals | None = Field(
        None,
        description="Object containing totals for all adjustments on a transaction. Returned when the `include` parameter is used with the `adjustments_totals` value.",
    )
    business: Business1 | None = Field(
        None,
        description="Business for this transaction. Reflects the entity at the time it was added to the transaction, or its revision if `revised_at` is not `null`. Returned when the `include` parameter is used with the `business` value and the transaction has a `business_id`.",
    )
    customer: Customer1 | None = Field(
        None,
        description="Customer for this transaction. Reflects the entity at the time it was added to the transaction, or its revision if `revised_at` is not `null`. Returned when the `include` parameter is used with the `customer` value and the transaction has a `customer_id`.",
    )
    discount: Discount2 | None = Field(
        None,
        description="Discount for this transaction. Reflects the entity at the time it was added to the transaction. Returned when the `include` parameter is used with the `discount` value and the transaction has a `discount_id`.",
    )
    available_payment_methods: list[PaymentMethodType] | None = None


class TransactionPreview(BaseModel):
    customer_id: CustomerId | None = Field(
        None,
        description="Paddle ID of the customer that this transaction preview is for, prefixed with `ctm_`.",
    )
    address_id: AddressId | None = Field(
        None,
        description="Paddle ID of the address that this transaction preview is for, prefixed with `add_`. Send one of `address_id`, `customer_ip_address`, or the `address` object when previewing.",
    )
    business_id: BusinessId | None = Field(
        None,
        description="Paddle ID of the business that this transaction preview is for, prefixed with `biz_`.",
    )
    currency_code: CurrencyCode | None = Field(
        None, description="Supported three-letter ISO 4217 currency code."
    )
    discount_id: DiscountId | None = Field(
        None,
        description="Paddle ID of the discount applied to this transaction preview, prefixed with `dsc_`.",
    )
    customer_ip_address: str | None = Field(
        None,
        description="IP address for this transaction preview. Send one of `address_id`, `customer_ip_address`, or the `address` object when previewing.",
    )
    address: AddressPreview | None = Field(
        None,
        description="Address for this transaction preview. Send one of `address_id`, `customer_ip_address`, or the `address` object when previewing.",
    )
    ignore_trials: bool | None = Field(
        False,
        description="""Whether trials should be ignored for transaction preview calculations.

By default, recurring items with trials are considered to have a zero charge when previewing. Set to `true` to disable this.""",
    )
    items: list[TransactionPreviewItem] = Field(
        ...,
        description="List of items to preview transaction calculations for.",
        max_length=100,
        min_length=1,
    )
    details: TransactionPreviewDetails | None = None
    available_payment_methods: list[PaymentMethodType] | None = None


class TransactionUpdate(BaseModel):
    id: TransactionId | None = None
    status: StatusTransaction | None = Field(
        None,
        description="""Status of this transaction. You may set a transaction to `billed` or `canceled`. Billed transactions cannot be changed.

For manually-collected transactions, marking as `billed` is essentially issuing an invoice.""",
    )
    customer_id: CustomerId | None = Field(
        None,
        description="Paddle ID of the customer that this transaction is for, prefixed with `ctm_`.",
    )
    address_id: AddressId | None = Field(
        None,
        description="Paddle ID of the address that this transaction is for, prefixed with `add_`.",
    )
    business_id: BusinessId | None = Field(
        None,
        description="Paddle ID of the business that this transaction is for, prefixed with `biz_`.",
    )
    custom_data: CustomData | None = Field(
        None, description="Your own structured key-value data."
    )
    currency_code: CurrencyCode | None = Field(
        None,
        description="Supported three-letter ISO 4217 currency code. Must be `USD`, `EUR`, or `GBP` if `collection_mode` is `manual`.",
    )
    origin: OriginTransaction | None = None
    subscription_id: SubscriptionId | None = Field(
        None,
        description="Paddle ID of the subscription that this transaction is for, prefixed with `sub_`.",
    )
    invoice_id: Annotated[str, Field(pattern="^inv_[a-z\\d]{26}$")] | None = Field(
        None,
        description="Paddle ID of the invoice that this transaction is related to, prefixed with `inv_`. Used for compatibility with the Paddle Invoice API, which is now deprecated. This field is scheduled to be removed in the next version of the Paddle API.",
        examples=["inv_01ghbk4xjn4qdsmstcwzgcgg35"],
    )
    invoice_number: str | None = Field(
        None,
        description="Invoice number for this transaction. Automatically generated by Paddle when you mark a transaction as `billed` where `collection_mode` is `manual`.",
        examples=["123-45678"],
    )
    collection_mode: CollectionMode | None = Field(
        "automatic",
        description="How payment is collected for this transaction. `automatic` for checkout, `manual` for invoices.",
    )
    discount_id: DiscountId | None = Field(
        None,
        description="Paddle ID of the discount applied to this transaction, prefixed with `dsc_`.",
    )
    billing_details: BillingDetailsUpdate | None = Field(
        None,
        description="Details for invoicing. Required if `collection_mode` is `manual`.",
    )
    billing_period: TimePeriod | None = Field(
        None,
        description="Time period that this transaction is for. Set automatically by Paddle for subscription renewals to describe the period that charges are for.",
    )
    items: (
        list[
            TransactionItemCreateWithPriceId
            | TransactionItemCreateWithPrice
            | TransactionItemCreateWithPriceAndProduct
        ]
        | None
    ) = Field(
        None,
        description="""List of items on this transaction.

When making a request, each object must contain either a `price_id` or a `price` object, and a `quantity`.

Include a `price_id` to charge for an existing catalog item, or a `price` object to charge for a non-catalog item.""",
        max_length=100,
        min_length=1,
    )
    details: TransactionDetails | None = None
    payments: list[TransactionPaymentAttempt] | None = Field(
        None,
        description="List of payment attempts for this transaction, including successful payments. Sorted by `created_at` in descending order, so most recent attempts are returned first.",
    )
    checkout: Checkout2 | None = Field(
        None,
        description="Paddle Checkout details for this transaction. You may pass a URL when creating or updating an automatically-collected transaction, or when creating or updating a manually-collected transaction where `billing_details.enable_checkout` is `true`.",
        title="TransactionCheckout",
    )
    created_at: CreatedAt | None = None
    updated_at: UpdatedAt | None = None
    billed_at: Timestamp | None = Field(
        None,
        description="RFC 3339 datetime string of when this transaction was marked as `billed`. `null` for transactions that aren't `billed` or `completed`. Set automatically by Paddle.",
    )


class TransactionPricingPreviewLineItem(BaseModel):
    price: Price | None = Field(
        None, description="Related price entity for this preview line item."
    )
    quantity: int | None = Field(
        None, description="Quantity of this preview line item."
    )
    tax_rate: str | None = Field(
        None,
        description="Rate used to calculate tax for this preview line item.",
        examples=["0.2"],
    )
    unit_totals: TotalsModel | None = Field(
        None,
        description="Breakdown of the charge for one unit in the lowest denomination of a currency (e.g. cents for USD).",
    )
    formatted_unit_totals: TotalsModel | None = Field(
        None,
        description="Breakdown of the charge for one unit in the format of a given currency.",
    )
    totals: TotalsModel | None = None
    formatted_totals: TotalsModel | None = Field(
        None,
        description="The financial breakdown of a charge in the format of a given currency.",
    )
    product: Product | None = Field(
        None, description="Related product entity for this preview line item price."
    )
    discounts: list[TransactionPricingPreviewLineItemDiscount] | None = None


class SubscriptionIncludes(Subscription1):
    next_transaction: SubscriptionNextTransaction | None = Field(
        None,
        description="Preview of the next transaction for this subscription. May include prorated charges that aren't yet billed and one-time charges. Returned when the `include` parameter is used with the `next_transaction` value. `null` if the subscription is scheduled to cancel or pause.",
    )
    recurring_transaction_details: RecurringTransactionDetails | None = Field(
        None,
        description="Preview of the recurring transaction for this subscription. This is what the customer can expect to be billed when there are no prorated or one-time charges. Returned when the `include` parameter is used with the `recurring_transaction_details` value.",
    )


class SubscriptionPreview(BaseModel):
    status: StatusSubscription | None = None
    customer_id: CustomerId | None = Field(
        None,
        description="Paddle ID of the customer that this subscription is for, prefixed with `ctm_`.",
    )
    address_id: AddressId | None = Field(
        None,
        description="Paddle ID of the address that this subscription is for, prefixed with `add_`.",
    )
    business_id: BusinessId | None = Field(
        None,
        description="Paddle ID of the business that this subscription is for, prefixed with `biz_`.",
    )
    currency_code: CurrencyCode | None = Field(
        None,
        description="Supported three-letter ISO 4217 currency code. Transactions for this subscription are created in this currency. Must be `USD`, `EUR`, or `GBP` if `collection_mode` is `manual`.",
    )
    created_at: CreatedAt | None = None
    updated_at: UpdatedAt | None = None
    started_at: Timestamp | None = Field(
        None,
        description="RFC 3339 datetime string of when this subscription started. This may be different from `first_billed_at` if the subscription started in trial.",
    )
    first_billed_at: Timestamp | None = Field(
        None,
        description="RFC 3339 datetime string of when this subscription was first billed. This may be different from `started_at` if the subscription started in trial.",
    )
    next_billed_at: Timestamp | None = Field(
        None,
        description="RFC 3339 datetime string of when this subscription is next scheduled to be billed.",
    )
    paused_at: Timestamp | None = Field(
        None,
        description="RFC 3339 datetime string of when this subscription was paused. Set automatically by Paddle when the pause subscription operation is used. `null` if not paused.",
    )
    canceled_at: Timestamp | None = Field(
        None,
        description="RFC 3339 datetime string of when this subscription was canceled. Set automatically by Paddle when the cancel subscription operation is used. `null` if not canceled.",
    )
    discount: DiscountSubscription | None = Field(
        None, description="Details of the discount applied to this subscription."
    )
    collection_mode: CollectionMode | None = Field(
        "automatic",
        description="How payment is collected for transactions created for this subscription. `automatic` for checkout, `manual` for invoices.",
    )
    billing_details: BillingDetails | None = Field(
        None,
        description="Details for invoicing. Required if `collection_mode` is `manual`.",
    )
    current_billing_period: TimePeriod | None = Field(
        None,
        description="Current billing period for this subscription. Set automatically by Paddle based on the billing cycle. `null` for `paused` and `canceled` subscriptions.",
    )
    billing_cycle: Duration | None = Field(
        None,
        description="How often this subscription renews. Set automatically by Paddle based on the prices on this subscription.",
    )
    scheduled_change: SubscriptionScheduledChange | None = Field(
        None,
        description="Change that's scheduled to be applied to a subscription. Use the pause subscription, cancel subscription, and resume subscription operations to create scheduled changes. `null` if no scheduled changes.",
    )
    management_urls: SubscriptionManagementUrls | None = None
    items: list[ItemSubscription] | None = Field(
        None,
        description="List of items on this subscription. Only recurring items are returned.",
        max_length=100,
        min_length=1,
    )
    custom_data: CustomData | None = Field(
        None, description="Your own structured key-value data."
    )
    immediate_transaction: SubscriptionNextTransaction | None = Field(
        None,
        description="Preview of the immediate transaction created as a result of changes to the subscription. Returns a complete object where `proration_billing_mode` is `prorated_immediately` or `full_immediately`; `null` otherwise.",
    )
    next_transaction: SubscriptionNextTransaction | None = Field(
        None,
        description="Preview of the next transaction for this subscription. Includes charges created where `proration_billing_mode` is `prorated_next_billing_period` or `full_next_billing_period`, as well as one-time charges. `null` if the subscription is scheduled to cancel or pause.",
    )
    recurring_transaction_details: SubscriptionRecurringTransactionDetails | None = (
        Field(
            None,
            description="Preview of the recurring transaction for this subscription. This is what the customer can expect to be billed when there are no prorated or one-time charges.",
        )
    )
    update_summary: UpdateSummary | None = None
    import_meta: ImportMetaSubscription | None = Field(
        None,
        description="Import information for this entity. `null` if this entity is not imported.",
    )


class TransactionPricingPreviewDetails(BaseModel):
    line_items: list[TransactionPricingPreviewLineItem] | None = None


class TransactionPricingPreviewResponse(TransactionPricingPreviewBase):
    details: TransactionPricingPreviewDetails | None = None
    available_payment_methods: list[PaymentMethodType] | None = None

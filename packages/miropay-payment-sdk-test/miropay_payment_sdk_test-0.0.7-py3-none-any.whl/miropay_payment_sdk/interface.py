from dataclasses import dataclass
from typing import Generic, Optional, TypeVar

from .enum import GATEWAY, PAYMENT_STATUS


T = TypeVar('T')

@dataclass
class IHttpResponse(Generic[T]):
    body: T
    headers: dict[str,str]
    statusCode: int

@dataclass
class ICreatePayment:
    amount: str
    gateways: list[GATEWAY]
    title: str
    description: str
    redirectUrl: str
    collectFeeFromCustomer: bool
    collectCustomerEmail: bool
    collectCustomerPhoneNumber: bool


@dataclass
class ICreatePaymentResponseBody:
    referenceCode: str
    amount: str
    paidVia: Optional[str]
    paidAt: Optional[str]
    redirectUrl:str
    status: PAYMENT_STATUS
    payoutAmount: Optional[str]

@dataclass
class ICreatePaymentResponse(IHttpResponse[ICreatePaymentResponseBody]):
    pass

@dataclass
class IPaymentDetailsResponseBody:
    referenceCode: str
    amount: str
    paidVia: Optional[str]
    paidAt: Optional[str]
    callbackUrl:str
    status: PAYMENT_STATUS
    payoutAmount: Optional[str]

@dataclass
class IPaymentDetailsResponse(IHttpResponse[IPaymentDetailsResponseBody]):
    pass

@dataclass
class ICancelPaymentResponseBody:
    referenceCode: str
    amount: str
    paidVia: Optional[str]
    paidAt: Optional[str]
    callbackUrl:str
    status: PAYMENT_STATUS
    payoutAmount: Optional[str]

@dataclass
class ICancelPaymentResponse(IHttpResponse[ICancelPaymentResponseBody]):
    pass

@dataclass
class IPublicKeyResponseBody:
    id: str
    key: str

@dataclass
class IPublicKeysResponse(IHttpResponse[list[IPublicKeyResponseBody]]):
    pass

@dataclass
class IVerifyPayload:
    keyId: str
    content: Optional[str]


@dataclass
class IVerifyPaymentResponseBody:
    referenceCode: str
    status : PAYMENT_STATUS
    payoutAmount: Optional[str]

@dataclass
class IVerifyPaymentResponse(IHttpResponse[IVerifyPaymentResponseBody]):
    pass
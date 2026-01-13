import enum


class GATEWAY(enum.Enum):
    FIB = "FIB"
    ZAIN = "ZAIN"
    ASIA_PAY = "ASIA_PAY"
    FAST_PAY = "FAST_PAY"
    SUPER_QI = "SUPER_QI"
    NASS_WALLET = "NASS_WALLET"
    YANA = "YANA"

class PAYMENT_STATUS(enum.Enum):
    TIMED_OUT = "TIMED_OUT"
    PENDING = "PENDING"
    PAID = "PAID"
    CANCELED = "CANCELED"
    FAILED = "FAILED"
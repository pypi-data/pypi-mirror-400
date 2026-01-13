from pydantic.dataclasses import dataclass
from tink_python_api_types.common import Amount
from typing import List


@dataclass
class Balance:
    amount: Amount


@dataclass
class Balances:
    booked: Balance
    available: Balance = None


@dataclass
class Iban:
    iban: str
    bban: str


@dataclass
class FinancialInstitution:
    account_number: str
    # reference_numbers: any


@dataclass
class Identifiers:
    financial_institution: FinancialInstitution
    iban: Iban = None


@dataclass
class Dates:
    last_refreshed: str


@dataclass
class Account:
    id: str
    name: str
    type: str
    balances: Balances
    identifiers: Identifiers
    dates: Dates
    financial_institution_id: str
    customer_segment: str


@dataclass
class AccountsPage:
    accounts: List[Account]
    next_page_token: str

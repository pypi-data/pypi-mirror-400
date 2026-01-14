from typing import Dict, Any, List, Optional, Tuple, Union, TypedDict

TimeoutType = Union[float, Tuple[float, float]]

class Address(TypedDict, total=False):
    address1: Optional[str]
    address2: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str]
    country: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]

class DonationCharge(TypedDict, total=False):
    amount: float
    processing_fee: Optional[float]
    external_donation_id: str
    external_donation_source: str
    external_donation_date: Optional[str]  # ISO8601

class CreateUserPayload(TypedDict, total=False):
    phone_number: Optional[str]
    email: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    preferred_language: Optional[str]
    second_language: Optional[str]
    chapter_id: Optional[int]
    custom_user_properties: Optional[Dict[str, Any]]
    add_tags: Optional[List[str]]
    remove_tags: Optional[List[str]]
    donation_charge: Optional[DonationCharge]
    address: Optional[Address]
    sms_permission: Optional[bool]
    call_permission: Optional[bool]
    email_permission: Optional[bool]

class UpdateUserPayload(TypedDict, total=False):
    phone_number: Optional[str]
    email: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    preferred_language: Optional[str]
    second_language: Optional[str]
    chapter_id: Optional[int]
    referred_by_user_id: Optional[int]
    custom_user_properties: Optional[Dict[str, Any]]
    address: Optional[Address]
    sms_permission: Optional[bool]
    call_permission: Optional[bool]
    email_permission: Optional[bool]
    chapter_ids: Optional[List[int]]
    add_chapter_ids: Optional[List[int]]
    remove_chapter_ids: Optional[List[int]]
    set_exclusive_chapter: Optional[bool]

class UserActionData(TypedDict, total=False):
    phone_number: Optional[str]
    email: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    preferred_language: Optional[str]
    second_language: Optional[str]
    custom_user_properties: Optional[Dict[str, Any]]
    address: Optional[Address]
    sms_permission: Optional[bool]
    call_permission: Optional[bool]
    email_permission: Optional[bool]

class UserActionPayload(TypedDict, total=False):
    data: Optional[UserActionData]
    page_id: int
    user_id: int
    created_at: Optional[int]

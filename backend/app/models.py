from typing import List, Optional, Literal
from pydantic import BaseModel

Role = Literal["super_admin", "admin", "staff", "read_only"]
ROLE_LEVEL = {"read_only": 1, "staff": 2, "admin": 3, "super_admin": 4}


class UserPublic(BaseModel):
    id: str
    username: str
    full_name: str
    role: Role
    is_active: bool
    last_login: Optional[str] = None
    created_at: str


class LoginIn(BaseModel):
    username: str
    password: str


class UserCreateIn(BaseModel):
    username: str
    password: str
    full_name: str
    role: Role = "staff"


class UserUpdateIn(BaseModel):
    full_name: Optional[str] = None
    role: Optional[Role] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


class MemberIn(BaseModel):
    first_name: str
    middle_name: Optional[str] = ""
    last_name: str
    gender: Literal["Male", "Female", "Other"]
    date_of_birth: str
    membership_status: Literal["Active", "Inactive", "Visitor", "Transferred"] = "Active"
    membership_date: Optional[str] = None
    baptism_date: Optional[str] = None
    ministries: List[str] = []
    cell_group: Optional[str] = ""
    marital_status: Literal["Single", "Married", "Widowed", "Divorced"] = "Single"
    wedding_anniversary: Optional[str] = None
    occupation: Optional[str] = ""
    employer: Optional[str] = ""
    notes: Optional[str] = ""
    phone_primary: Optional[str] = ""
    phone_secondary: Optional[str] = ""
    whatsapp: Optional[str] = ""
    email: Optional[str] = ""
    address_street: Optional[str] = ""
    address_city: Optional[str] = ""
    country_origin: Optional[str] = ""
    country_current: Optional[str] = ""
    photo_url: Optional[str] = ""


class FamilyIn(BaseModel):
    family_name: str
    head_member_id: str
    members: List[dict] = []


class ContributionIn(BaseModel):
    member_id: str
    contribution_date: str
    contribution_type: Literal["Tithe", "Offering", "Seed", "Pledge", "First Fruit", "Special"]
    amount: float
    payment_mode: Literal["Cash", "Bank Transfer", "Cheque", "Online", "POS"]
    reference_no: Optional[str] = ""
    notes: Optional[str] = ""

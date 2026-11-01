from dataclasses import dataclass

@dataclass
class User:
    id: int
    username: str
    password_hash: str
    role_id: int

@dataclass
class Client:
    id: int
    user_id: int | None
    first_name: str
    last_name: str
    middle_name: str | None
    phone: str
    email: str | None = None
    birth_day: str | None = None
    status: str | None = "ACTIVE"
    created_at: str | None = None

@dataclass
class ClientMembership:
    id: int
    client_id: int
    membership_type_id: int
    card_number: str
    start_date: str
    end_date: str
    remaining_visits: int
    status: str

@dataclass
class Visit:
    id: int
    client_id: int
    client_membership_id: int
    registered_by_staff_id: int
    check_in_at: str
    client_name: str | None = None


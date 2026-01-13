import json
from datetime import date
from enum import Enum
from pydantic import BaseModel, Field, RootModel, ValidationError, field_validator


class ExternalAPIError(Exception):
    pass


class CardStatus(Enum):
    ACTIVE = "active"
    AVAILABLE = "available"
    EXPIRED = "expired"


class ESNCard(BaseModel):
    code: str
    tid: int
    expiration_date: date | None = Field(alias="expiration-date")
    status: CardStatus
    section_code: str | None = Field(alias="section-code")
    activation_date: date | None = Field(alias="activation date")

    @field_validator(
        "expiration_date", "section_code", "activation_date", mode="before"
    )
    def normalize_empty(cls, value: str):
        if isinstance(value, list):
            if len(value) == 0:
                return None
            if len(value) > 1:
                raise ValueError(f"Expected at most one value, got {value}")
            value = value[0]

        if value == "":
            return None

        return value


class ESNCardResponse(RootModel):
    root: list[ESNCard] = Field(max_length=1)


with open("../card_example.json", "r") as f:
    data = json.load(f)


try:
    esncards = ESNCardResponse.model_validate(data).root

    if not esncards:
        print("")
    else:
        print(esncards[0])
except ValidationError as e:
    print("API returned incorrect data model: %s", e.json())

"""Strict public API schemas."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class CreditApplication(BaseModel):
    model_config = ConfigDict(extra="forbid")

    age: int = Field(ge=18, le=100)
    credit_amount: float = Field(gt=0, le=1_000_000)
    duration_months: int = Field(ge=1, le=120)
    installment_rate: int = Field(ge=1, le=4)
    existing_credits: int = Field(ge=1, le=4)
    dependents: int = Field(ge=1, le=2)
    checking_status: Literal["none", "negative", "low", "high"]
    credit_history: Literal["critical", "delayed", "existing_paid", "all_paid", "no_credits"]
    purpose: Literal["car", "furniture", "education", "business", "other"]
    savings_status: Literal["unknown", "low", "medium", "high"]
    employment_duration: Literal["unemployed", "short", "medium", "long"]
    housing: Literal["rent", "own", "free"]
    foreign_worker: bool


class Prediction(BaseModel):
    probability: float = Field(ge=0, le=1)
    predicted_default: bool
    threshold: float
    model_version: str


class BatchRequest(BaseModel):
    records: list[CreditApplication]


class BatchResponse(BaseModel):
    predictions: list[Prediction]


class Contribution(BaseModel):
    feature: str
    contribution: float
    value: float


class ExplanationResponse(BaseModel):
    base_value: float
    contributions: list[Contribution]
    note: str
    model_version: str

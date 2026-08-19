"""Request and response models for the API.

Pydantic validates every incoming body against these definitions before the
endpoint runs, so malformed input is rejected with a 422 and never reaches the
model. These classes also generate the schema shown in the /docs Swagger UI.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# The three Enums below pin the categorical features to the exact strings seen
# during training. This matters: the fitted OneHotEncoder uses
# handle_unknown="ignore", so an unrecognised value like "Sometimes" would be
# silently encoded as all-zeros and produce a confident but meaningless
# prediction. Rejecting it up front with a 422 is far safer than guessing.

class BusinessTravel(str, Enum):
    non_travel = "Non-Travel"
    travel_rarely = "Travel_Rarely"
    travel_frequently = "Travel_Frequently"


class Department(str, Enum):
    sales = "Sales"
    research_development = "Research & Development"
    human_resources = "Human Resources"


class OverTime(str, Enum):
    yes = "Yes"
    no = "No"


class EmployeeFeatures(BaseModel):
    """One employee's details, as accepted by POST /predict.

    Field(...) marks a field as required; ge/le set inclusive bounds. The bounds
    reflect what the dataset actually contains, so the model is never asked to
    extrapolate to inputs it has never seen.
    """

    # Passed through to the response for the caller's convenience, but excluded
    # before scoring - the model was never trained on names.
    EmployeeName: Optional[str] = Field(None, description="Label only, not used by the model")

    Age: int = Field(..., ge=18, le=75)
    DailyRate: int = Field(..., ge=0)
    DistanceFromHome: int = Field(..., ge=0)
    MonthlyIncome: int = Field(..., ge=0)
    TotalWorkingYears: int = Field(..., ge=0, le=60)
    TrainingTimesLastYear: int = Field(..., ge=0, le=10)
    YearsAtCompany: int = Field(..., ge=0, le=60)

    # Categorical - constrained to the training vocabulary (see Enums above).
    BusinessTravel: BusinessTravel
    Department: Department
    OverTime: OverTime

    # Survey scores that IBM already encoded as 1-4 ordinals in the raw dataset,
    # which is why they pass through the pipeline unscaled.
    EnvironmentSatisfaction: int = Field(..., ge=1, le=4)
    JobSatisfaction: int = Field(..., ge=1, le=4)
    WorkLifeBalance: int = Field(..., ge=1, le=4)

    # Stock options are graded 0-3, not 1-4 like the survey scores above.
    StockOptionLevel: int = Field(..., ge=0, le=3)

    # Pre-fills the "Try it out" form in the Swagger UI with a valid body, so
    # /docs is usable without hand-typing all 14 fields.
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "EmployeeName": "Jane Doe",
                "Age": 34,
                "DailyRate": 800,
                "DistanceFromHome": 5,
                "MonthlyIncome": 5500,
                "TotalWorkingYears": 8,
                "TrainingTimesLastYear": 2,
                "YearsAtCompany": 4,
                "BusinessTravel": "Travel_Rarely",
                "Department": "Sales",
                "OverTime": "No",
                "EnvironmentSatisfaction": 3,
                "JobSatisfaction": 3,
                "StockOptionLevel": 1,
                "WorkLifeBalance": 3,
            }
        }
    )


class PredictionResponse(BaseModel):
    """What POST /predict returns.

    The verdict is given three ways so callers can use whichever suits them:
    a boolean to branch on, a label to display, and the raw probability for
    ranking employees by risk or applying a custom threshold.
    """

    EmployeeName: Optional[str] = None      # echoed back from the request, if provided
    attrition: bool                          # True == predicted to leave
    attrition_label: str                     # "Yes" / "No", matching the dataset's wording
    attrition_probability: float             # P(leaves), between 0.0 and 1.0

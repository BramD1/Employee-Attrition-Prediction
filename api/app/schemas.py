from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


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
    EmployeeName: Optional[str] = Field(None, description="Label only, not used by the model")
    Age: int = Field(..., ge=18, le=75)
    DailyRate: int = Field(..., ge=0)
    DistanceFromHome: int = Field(..., ge=0)
    MonthlyIncome: int = Field(..., ge=0)
    TotalWorkingYears: int = Field(..., ge=0, le=60)
    TrainingTimesLastYear: int = Field(..., ge=0, le=10)
    YearsAtCompany: int = Field(..., ge=0, le=60)
    BusinessTravel: BusinessTravel
    Department: Department
    OverTime: OverTime
    EnvironmentSatisfaction: int = Field(..., ge=1, le=4)
    JobSatisfaction: int = Field(..., ge=1, le=4)
    StockOptionLevel: int = Field(..., ge=0, le=3)
    WorkLifeBalance: int = Field(..., ge=1, le=4)

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
    EmployeeName: Optional[str] = None
    attrition: bool
    attrition_label: str
    attrition_probability: float

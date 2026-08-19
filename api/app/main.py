from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.ml.predictor import get_model
from app.schemas import EmployeeFeatures, PredictionResponse


def client_ip(request: Request) -> str:
    """Real client IP, even behind Cloud Run's proxy.

    Cloud Run puts the caller's IP first in X-Forwarded-For; request.client.host
    would otherwise be the load balancer, so every caller would share one bucket.
    """
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return get_remote_address(request)


limiter = Limiter(key_func=client_ip)


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_model()  # load once at startup instead of on the first request
    yield


app = FastAPI(
    title="Employee Attrition Prediction API",
    version="1.0.0",
    description="Predicts whether an employee is likely to leave, based on a tuned SVC pipeline.",
    lifespan=lifespan,
)

# Wire up rate limiting: attach the limiter and register the 429 handler.
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/predict", response_model=PredictionResponse)
@limiter.limit("10/minute")
def predict(request: Request, features: EmployeeFeatures) -> PredictionResponse:
    model = get_model()
    data = features.model_dump(exclude={"EmployeeName"}, mode="json")
    prediction, probability = model.predict(data)
    return PredictionResponse(
        EmployeeName=features.EmployeeName,
        attrition=prediction,
        attrition_label="Yes" if prediction else "No",
        attrition_probability=round(probability, 4),
    )

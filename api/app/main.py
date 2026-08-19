"""FastAPI application entry point.

Exposes the trained attrition model over HTTP:
    GET  /health   - liveness probe for Docker / Cloud Run
    POST /predict  - single-employee attrition prediction

Run locally with:  uvicorn app.main:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
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
        # Header format is "client, proxy1, proxy2" - the first entry is the caller.
        return forwarded.split(",")[0].strip()
    # No proxy in front (e.g. running locally), so the socket address is accurate.
    return get_remote_address(request)


# Buckets rate limits per client IP, using the resolver defined above.
limiter = Limiter(key_func=client_ip)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown hook.

    Loading the pickle takes a moment, so do it once while the app boots rather
    than letting the first unlucky request pay the cost (and risk a timeout).
    """
    get_model()
    yield
    # Nothing to tear down - the model is just an in-memory object.


app = FastAPI(
    title="Employee Attrition Prediction API",
    version="1.0.0",
    description="Predicts whether an employee is likely to leave, based on a tuned SVC pipeline.",
    lifespan=lifespan,
)

# Wire up rate limiting: attach the limiter and register the 429 handler.
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Let the browser frontend call this API from a different origin.
# Browsers block cross-origin fetch() by default, so without this the request
# fails in the browser before it ever reaches FastAPI - and the browser sends a
# preflight OPTIONS request first, which also needs to be answered here.
#
# "*" is appropriate while this API is public and token-less: there are no
# cookies or credentials to steal, so any site being able to call it grants no
# access a plain curl wouldn't already have. If you later switch to
# --no-allow-unauthenticated, replace this with your frontend's exact origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/health")
def health() -> dict:
    """Liveness probe.

    Kept trivial and unthrottled on purpose: Docker's HEALTHCHECK and Cloud Run
    poll this frequently, and it must never fail for reasons unrelated to the
    process being alive.
    """
    return {"status": "ok"}


@app.post("/predict", response_model=PredictionResponse)
@limiter.limit("10/minute")
def predict(request: Request, features: EmployeeFeatures) -> PredictionResponse:
    """Score one employee's attrition risk.

    FastAPI has already validated the body against EmployeeFeatures by the time
    this runs, so anything reaching here is known to be well-formed - a bad
    category or out-of-range score is rejected with a 422 before we get called.

    Note: the `request` parameter is required by slowapi to identify the caller,
    even though this function never reads it directly. Removing it breaks the
    rate limiter.
    """
    model = get_model()  # cached after startup, so this is just a dict lookup

    # EmployeeName is a human-facing label the model was never trained on -
    # drop it before scoring. mode="json" converts the Enum members back to
    # their plain string values ("Sales", not Department.sales), which is what
    # the fitted encoders expect.
    data = features.model_dump(exclude={"EmployeeName"}, mode="json")

    prediction, probability = model.predict(data)

    return PredictionResponse(
        EmployeeName=features.EmployeeName,  # echoed back so callers can match up batches
        attrition=prediction,
        attrition_label="Yes" if prediction else "No",  # mirrors the dataset's original labels
        attrition_probability=round(probability, 4),
    )

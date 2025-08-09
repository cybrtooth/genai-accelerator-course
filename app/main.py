# Import packages
import hashlib
import hmac
import os
from typing import Optional
import uuid
from pathlib import Path

from fastapi import FastAPI, Header, Request, status
from fastapi.responses import PlainTextResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from schemas.nylas_email_schema import EmailObject
from schemas.nylas_webhook_schema import WebhookEvent

load_dotenv(override=True)

# Array to hold webhook dataclass
webhooks = []

# Create the FastAPI app
app = FastAPI()

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")


# Read and insert webhook data
@app.api_route("/events", methods=["GET", "POST"])
async def webhook(
    request: Request,
    event: WebhookEvent = None,
    x_nylas_signature: Optional[str] = Header(None),
):
    if request.method == "GET":
        challenge = request.query_params.get("challenge")
        if challenge:
            print(" * Nylas connected to the webhook!")
            return PlainTextResponse(challenge)
        return PlainTextResponse(
            "No challenge", status_code=status.HTTP_400_BAD_REQUEST
        )
    # POST method
    body = await request.body()
    is_genuine = verify_signature(
        message=body,
        key=os.environ.get("WEBHOOK_SECRET").encode("utf8"),
        signature=x_nylas_signature,
    )
    if not is_genuine:
        return PlainTextResponse("Signature verification failed!", status_code=401)

    # Store the raw event JSON
    store_event_json(event)

    email_obj = EmailObject(**event.data["object"])

    webhooks.append(email_obj)
    return PlainTextResponse("Webhook received", status_code=200)

# from fastapi import Header

# @app.api_route("/events", methods=["GET", "POST"])
# async def webhook(
#     request: Request,
#     x_nylas_signature: str | None = Header(None, alias="X-Nylas-Signature"),
# ):
#     if request.method == "GET":
#         challenge = request.query_params.get("challenge")
#         return PlainTextResponse(challenge) if challenge else PlainTextResponse("No challenge", status_code=400)

#     body = await request.body()

#     # DEBUG: show what we’re comparing
#     computed = hmac.new(
#         os.environ["WEBHOOK_SECRET"].encode("utf8"),
#         msg=body,
#         digestmod=hashlib.sha256,
#     ).hexdigest()
#     print("Computed:", computed)
#     print("Header  :", x_nylas_signature)

#     if not x_nylas_signature or not hmac.compare_digest(computed.lower(), x_nylas_signature.strip().lower()):
#         return PlainTextResponse("Signature verification failed!", status_code=401)

#     # If you want, now parse:
#     # from pydantic import ValidationError
#     # try:
#     #     event = WebhookEvent.model_validate_json(body)
#     # except ValidationError as e:
#     #     print("Validation error:", e)
#     #     return PlainTextResponse("OK", status_code=200)  # still ack so Nylas stops retrying

#     # Store raw first:
#     store_event_json(WebhookEvent.model_validate_json(body))  # or store the raw bytes/string
#     return PlainTextResponse("Webhook received", status_code=200)



# Main page
@app.get("/")
def index(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "webhooks": webhooks}
    )


# Signature verification
def verify_signature(message, key, signature):
    digest = hmac.new(key, msg=message, digestmod=hashlib.sha256).hexdigest()

    return hmac.compare_digest(digest, signature)


def store_event_json(event: WebhookEvent):
    base_dir = Path(__file__).resolve().parent.parent
    events_dir = base_dir / "requests" / "events"
    events_dir.mkdir(parents=True, exist_ok=True)
    filename = events_dir / f"{uuid.uuid1()}.json"
    with open(filename, "w") as f:
        f.write(event.model_dump_json())


# Run our application
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

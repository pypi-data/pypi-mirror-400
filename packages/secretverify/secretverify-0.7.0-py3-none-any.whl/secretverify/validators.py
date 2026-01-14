import json
import os
import requests
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from google.oauth2 import service_account
from google.auth.exceptions import GoogleAuthError
from google.auth.transport.requests import Request as GCPRequest


# ────────────────────────── helper ────────────────────────── #

def http_token_check(
        url: str,
        auth_header: str | None = None,
        *,
        method: str = "GET",
        headers: dict[str, str] | None = None,
        auth: tuple[str, str] | None = None,
) -> tuple[bool, str]:
    """
    Returns (True, msg) if rotated (4xx/5xx).
    Returns (False, msg) if live (2xx/3xx).
    """
    hdrs = headers.copy() if headers else {}
    if auth_header:
        hdrs["Authorization"] = auth_header

    try:
        r = requests.request(method, url, headers=hdrs, auth=auth, timeout=10)
        code = r.status_code
        msg = f"[{code}] {url}"

        # If we get a 2xx or 3xx, the system accepted the request = NOT ROTATED
        if 200 <= code < 400:
            return False, f"LEAK LIVE: {msg}"

        # 4xx (Unauthorized/Forbidden) or 5xx (Server Error on bad auth) = ROTATED
        return True, f"ROTATED/INACTIVE: {msg}"

    except requests.RequestException as exc:
        # Connection failures or timeouts usually imply the endpoint/cred is dead
        return True, f"Request failed: {exc} (treating as rotated)"


# ────────────────────────── AWS ────────────────────────── #

def aws_check(access_key: str, secret_key: str):
    try:
        sts = boto3.client(
            "sts",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name="us-east-1",
        )
        sts.get_caller_identity()
        return False, "LEAK LIVE: AWS creds valid"
    except (ClientError, BotoCoreError) as e:
        return True, f"ROTATED: AWS auth failed: {e}"


# ────────────────────────── GCP ────────────────────────── #

def _read_json_input(data: str) -> dict:
    if os.path.isfile(data):
        with open(data, "r", encoding="utf-8") as f:
            data = f.read()
    return json.loads(data)


def gcp_sa_check(sa_json: str):
    try:
        info = _read_json_input(sa_json)
        creds = service_account.Credentials.from_service_account_info(info)
        creds.refresh(GCPRequest())
        return False, "LEAK LIVE: GCP service-account valid"
    except (json.JSONDecodeError, KeyError) as e:
        return True, f"ROTATED: JSON problem: {e}"
    except (GoogleAuthError, Exception) as e:
        return True, f"ROTATED: GCP auth failed: {e}"


# ────────────────────────── GitHub ────────────────────────── #

def github_check(token: str):
    # Endpoint depends on token type (ghs_ vs others)
    ep = "/rate_limit" if token.startswith("ghs_") else "/user"
    return http_token_check(
        f"https://api.github.com{ep}",
        f"Bearer {token}",
        headers={"Accept": "application/vnd.github+json"},
    )


# ───────────────────────── Bearer-style APIs ───────────────────────── #

def stripe_check(k):   return http_token_check("https://api.stripe.com/v1/account", f"Bearer {k}")


def openai_check(k):   return http_token_check("https://api.openai.com/v1/models", f"Bearer {k}")


def buildkite_check(t): return http_token_check("https://api.buildkite.com/v2/organizations", f"Bearer {t}")


def hf_check(t):       return http_token_check("https://huggingface.co/api/whoami-v2", f"Bearer {t}")


def netlify_check(t):  return http_token_check("https://api.netlify.com/api/v1/sites", f"Bearer {t}")


def npm_check(t):      return http_token_check("https://registry.npmjs.org/-/npm/v1/user", f"Bearer {t}")


def sendgrid_check(k): return http_token_check("https://api.sendgrid.com/v3/scopes", f"Bearer {k}")


# ───────────────────────── Custom/Basic Auth APIs ───────────────────────── #

def twilio_check(sid, token):
    # Simplest GET check for an account resource
    return http_token_check(f"https://api.twilio.com/2010-04-01/Accounts/{sid}.json", auth=(sid, token))


def zendesk_check(token, subdomain, email):
    url = f"https://{subdomain}.zendesk.com/api/v2/users/me.json"
    return http_token_check(url, auth=(f"{email}/token", token))


def jira_check(token, email):
    return http_token_check("https://api.atlassian.com/me", auth=(email, token))


def okta_check(token, domain):
    return http_token_check(f"https://{domain}/api/v1/users/me", f"SSWS {token}")


# ───────────────────────── registry ───────────────────────── #

class Validator:
    def __init__(self, func, params):
        self.func = func
        self.params = params

    def __call__(self, **kw):
        return self.func(**kw)


VALIDATORS = {
    "AWS Access Key & Secret": Validator(aws_check, ["access_key", "secret_key"]),
    "Buildkite": Validator(buildkite_check, ["token"]),
    "GCP Service Account": Validator(gcp_sa_check, ["sa_json"]),
    "GitHub": Validator(github_check, ["token"]),
    "Hugging Face": Validator(hf_check, ["token"]),
    "Jira": Validator(jira_check, ["token", "email"]),
    "Netlify": Validator(netlify_check, ["token"]),
    "NPM": Validator(npm_check, ["token"]),
    "Okta": Validator(okta_check, ["token", "domain"]),
    "OpenAI": Validator(openai_check, ["key"]),
    "SendGrid": Validator(sendgrid_check, ["k"]),
    "Stripe": Validator(stripe_check, ["key"]),
    "Twilio": Validator(twilio_check, ["sid", "token"]),
    "Zendesk": Validator(zendesk_check, ["token", "subdomain", "email"]),
}
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
        live_codes: tuple[int, ...] = (200,),
        rotated_codes: tuple[int, ...] = (401, 403, 404)
) -> tuple[bool, str]:
    hdrs = headers.copy() if headers else {}
    if auth_header:
        hdrs["Authorization"] = auth_header
    try:
        r = requests.request(method, url, headers=hdrs, auth=auth, timeout=10)
    except requests.RequestException as exc:
        return True, f"Request failed: {exc} (treating as rotated)"

    code = r.status_code
    msg = f"[{code}] {url}"
    if code in live_codes:
        return False, msg
    if code in rotated_codes:
        return True, msg
    return False, msg  # conservative default


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
        return False, "AWS creds valid (leak live)"
    except (ClientError, BotoCoreError) as e:
        return True, f"AWS auth failed: {e} (rotated)"


# ────────────────────────── GCP ────────────────────────── #

def _read_json_input(data: str) -> dict:
    """Accept raw JSON or a path to a .json file."""
    if os.path.isfile(data):
        with open(data, "r", encoding="utf-8") as f:
            data = f.read()
    return json.loads(data)


def gcp_sa_check(sa_json: str):
    try:
        info = _read_json_input(sa_json)
        creds = service_account.Credentials.from_service_account_info(info)
        creds.refresh(GCPRequest())
        return False, "GCP service-account valid (leak live)"
    except (json.JSONDecodeError, KeyError) as e:
        return True, f"JSON problem: {e}. Likely truncated (rotated/invalid)."
    except (GoogleAuthError, Exception) as e:
        return True, f"GCP auth failed: {e} (rotated)"


# ────────────────────────── GitHub ────────────────────────── #

_GH_API = "https://api.github.com"


def _gh_endpoint(tok: str) -> str:
    return "/rate_limit" if tok.startswith("ghs_") else "/user"


def github_check(token: str):
    ep = _gh_endpoint(token)
    return http_token_check(
        f"{_GH_API}{ep}",
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


def travis_check(t):   return http_token_check(
    "https://api.travis-ci.com/user",
    f"token {t}",
    headers={"Accept": "application/vnd.travis-ci.2+json"},
)


# ───────────────────────── Custom Header/Auth APIs ───────────────────────── #

def postman_check(k):
    return http_token_check("https://api.getpostman.com/me", headers={"X-Api-Key": k})


def twilio_check(sid, token):
    return http_token_check(f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Tokens.json", auth=(sid, token))


# ───────────────────────── Domain-based APIs ───────────────────────── #

def zendesk_check(token, subdomain, email):
    url = f"https://{subdomain}.zendesk.com/api/v2/users/me.json"
    return http_token_check(url, auth=(f"{email}/token", token))


def jira_check(token, email):
    return http_token_check("https://api.atlassian.com/me", auth=(email, token))


def okta_check(token, domain):
    return http_token_check(f"https://{domain}/api/v1/users/me", f"SSWS {token}")


# ───────────────────────── registry ───────────────────────── #

class Validator:
    def __init__(self, func, params):  # order = prompt order
        self.func = func;
        self.params = params

    def __call__(self, **kw):  # allows direct call
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
    "Postman": Validator(postman_check, ["k"]),
    "SendGrid": Validator(sendgrid_check, ["k"]),
    "Stripe": Validator(stripe_check, ["key"]),
    "Travis CI": Validator(travis_check, ["token"]),
    "Twilio": Validator(twilio_check, ["sid", "token"]),
    "Zendesk": Validator(zendesk_check, ["token", "subdomain", "email"]),
}
"""Data loader for cloud inventory JSON files."""

import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

from infralens.config import DATA_DIR as CONFIG_DATA_DIR

# Use local data/ if it exists (development), otherwise use config dir
_LOCAL_DATA = Path(__file__).parent.parent / "data"
DATA_DIR = _LOCAL_DATA if _LOCAL_DATA.exists() else CONFIG_DATA_DIR


@dataclass
class Domain:
    name: str
    registrar: str
    expires: datetime | None
    auto_renew: bool
    status: str


@dataclass
class HostingProject:
    name: str
    provider: str  # vercel or flyio
    url: str | None
    status: str
    last_deploy: datetime | None


@dataclass
class AIWorkspace:
    name: str
    provider: str  # openai or anthropic
    id: str


def load_json(filename: str) -> dict | list:
    path = DATA_DIR / filename
    if not path.exists():
        return {}
    with open(path) as f:
        data = json.load(f)
    return data.get("data", data)


def get_fetch_time(filename: str) -> datetime | None:
    path = DATA_DIR / filename
    if not path.exists():
        return None
    with open(path) as f:
        data = json.load(f)
    if "fetched_at" in data:
        return datetime.fromisoformat(data["fetched_at"])
    return None


def get_last_refresh() -> datetime | None:
    times = []
    for f in DATA_DIR.glob("*.json"):
        t = get_fetch_time(f.name)
        if t:
            times.append(t)
    return min(times) if times else None


def is_data_stale(hours: int = 24) -> bool:
    last = get_last_refresh()
    if not last:
        return True
    return (datetime.now() - last).total_seconds() > hours * 3600


def load_domains() -> list[Domain]:
    domains = []

    # GoDaddy
    for d in load_json("godaddy-domains.json"):
        if isinstance(d, dict):
            exp = None
            if d.get("expires"):
                try:
                    exp = datetime.fromisoformat(d["expires"].replace("Z", "+00:00"))
                except:
                    pass
            domains.append(Domain(
                name=d.get("domain", ""),
                registrar="GoDaddy",
                expires=exp,
                auto_renew=d.get("renewAuto", False),
                status=d.get("status", "UNKNOWN"),
            ))

    # Namecheap
    for d in load_json("namecheap-domains.json"):
        if isinstance(d, dict):
            exp = None
            if d.get("expires"):
                try:
                    exp = datetime.strptime(d["expires"], "%m/%d/%Y")
                except:
                    pass
            domains.append(Domain(
                name=d.get("name", ""),
                registrar="Namecheap",
                expires=exp,
                auto_renew=d.get("auto_renew", False),
                status="ACTIVE",
            ))

    # Cloudflare Registrar
    for d in load_json("cloudflare-registrar.json"):
        if isinstance(d, dict):
            exp = None
            if d.get("expires_at"):
                try:
                    exp = datetime.fromisoformat(d["expires_at"].replace("Z", "+00:00"))
                except:
                    pass
            domains.append(Domain(
                name=d.get("name", ""),
                registrar="Cloudflare",
                expires=exp,
                auto_renew=d.get("auto_renew", False),
                status=d.get("status", "UNKNOWN").upper(),
            ))

    def sort_key(d: Domain) -> datetime:
        if d.expires is None:
            return datetime.max
        # Normalize to naive datetime for comparison
        if d.expires.tzinfo is not None:
            return d.expires.replace(tzinfo=None)
        return d.expires

    return sorted(domains, key=sort_key)


def load_cloudflare_zones() -> list[dict]:
    return load_json("cloudflare-zones.json") or []


def load_hosting() -> list[HostingProject]:
    projects = []

    # Vercel
    vercel_data = load_json("vercel-projects.json")
    if isinstance(vercel_data, list):
        for p in vercel_data:
            projects.append(HostingProject(
                name=p.get("name", ""),
                provider="Vercel",
                url=p.get("url"),
                status="active",
                last_deploy=None,
            ))
    elif isinstance(vercel_data, dict):
        for p in vercel_data.get("projects", []):
            projects.append(HostingProject(
                name=p.get("name", ""),
                provider="Vercel",
                url=p.get("url"),
                status="active",
                last_deploy=None,
            ))

    # Fly.io
    for app in load_json("flyio-apps.json"):
        if isinstance(app, dict):
            projects.append(HostingProject(
                name=app.get("Name", app.get("name", "")),
                provider="Fly.io",
                url=f"https://{app.get('Name', '')}.fly.dev",
                status=app.get("Status", "unknown"),
                last_deploy=None,
            ))

    return projects


def load_ai_workspaces() -> list[AIWorkspace]:
    workspaces = []

    # OpenAI
    for p in load_json("openai-projects.json"):
        if isinstance(p, dict):
            workspaces.append(AIWorkspace(
                name=p.get("name", ""),
                provider="OpenAI",
                id=p.get("id", ""),
            ))

    # Anthropic
    for w in load_json("anthropic-workspaces.json"):
        if isinstance(w, dict):
            workspaces.append(AIWorkspace(
                name=w.get("name", ""),
                provider="Anthropic",
                id=w.get("id", ""),
            ))

    return workspaces


def load_ai_costs() -> dict:
    costs = {"openai": 0.0, "anthropic": 0.0, "total": 0.0}

    # OpenAI costs
    openai_costs = load_json("openai-costs.json")
    if isinstance(openai_costs, dict):
        for bucket in openai_costs.get("data", []):
            for r in bucket.get("results", []):
                try:
                    costs["openai"] += float(r.get("amount", {}).get("value", 0))
                except:
                    pass

    # Anthropic costs
    anthropic_costs = load_json("anthropic-costs.json")
    if isinstance(anthropic_costs, dict):
        for bucket in anthropic_costs.get("data", []):
            for r in bucket.get("results", []):
                try:
                    costs["anthropic"] += float(r.get("amount", 0))
                except:
                    pass

    costs["total"] = costs["openai"] + costs["anthropic"]
    return costs


def load_ai_usage() -> dict:
    """Load usage data aggregated by model."""
    usage = {"anthropic": {}, "openai": {}}

    # Anthropic usage by model
    anthropic_usage = load_json("anthropic-usage.json")
    if isinstance(anthropic_usage, dict):
        for bucket in anthropic_usage.get("data", []):
            for r in bucket.get("results", []):
                model = r.get("model", "unknown")
                input_tokens = r.get("uncached_input_tokens", 0)
                output_tokens = r.get("output_tokens", 0)
                if model not in usage["anthropic"]:
                    usage["anthropic"][model] = {"input": 0, "output": 0}
                usage["anthropic"][model]["input"] += input_tokens
                usage["anthropic"][model]["output"] += output_tokens

    # OpenAI usage by model
    openai_usage = load_json("openai-usage.json")
    if isinstance(openai_usage, dict):
        for bucket in openai_usage.get("data", []):
            for r in bucket.get("results", []):
                model = r.get("model", "unknown")
                input_tokens = r.get("input_tokens", 0)
                output_tokens = r.get("output_tokens", 0)
                if model not in usage["openai"]:
                    usage["openai"][model] = {"input": 0, "output": 0}
                usage["openai"][model]["input"] += input_tokens
                usage["openai"][model]["output"] += output_tokens

    return usage


def get_domain_alerts() -> list[tuple[str, str, str]]:
    """Returns list of (level, domain, message)."""
    alerts = []
    now = datetime.now()

    for d in load_domains():
        if d.status != "ACTIVE":
            continue

        if d.expires:
            days = (d.expires.replace(tzinfo=None) - now).days
            if days < 0:
                alerts.append(("critical", d.name, "EXPIRED"))
            elif days < 30:
                alerts.append(("critical", d.name, f"Expires in {days} days"))
            elif days < 90:
                alerts.append(("warning", d.name, f"Expires in {days} days"))

        if not d.auto_renew and d.status == "ACTIVE":
            alerts.append(("warning", d.name, "Auto-renew disabled"))

    return alerts

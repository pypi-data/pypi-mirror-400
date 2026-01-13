"""Fetch data from all cloud providers."""

import os
import json
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path

from infralens.config import load_env, DATA_DIR, get_config_dir

# Ensure data directory exists
get_config_dir()

# Also support local data/ for development
_LOCAL_DATA = Path(__file__).parent.parent / "data"
_DATA_DIR = _LOCAL_DATA if _LOCAL_DATA.exists() else DATA_DIR


def save_json(filename: str, data) -> None:
    """Save data to JSON file with timestamp."""
    filepath = _DATA_DIR / filename
    with open(filepath, "w") as f:
        json.dump({
            "fetched_at": datetime.now().isoformat(),
            "data": data
        }, f, indent=2)
    print(f"  Saved: {filename}")


def api_request(url: str, headers: dict, method: str = "GET"):
    """Make API request and return JSON response."""
    req = urllib.request.Request(url, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": e.code, "message": e.read().decode()[:500]}
    except Exception as e:
        return {"error": str(e)}


def fetch_vercel() -> None:
    """Fetch Vercel projects via CLI."""
    print("\n=== Vercel ===")
    import subprocess
    import re
    import shutil

    if not shutil.which("vercel"):
        print("  Vercel CLI not installed")
        return

    all_projects = []
    next_cursor = None

    while True:
        cmd = ["vercel", "project", "ls"]
        if next_cursor:
            cmd.extend(["--next", next_cursor])

        result = subprocess.run(cmd, capture_output=True, text=True)
        output = result.stdout + result.stderr

        for line in output.split("\n"):
            line = line.strip()
            if not line:
                continue
            if any(line.startswith(s) for s in [">", "Vercel", "Fetching", "Project Name"]):
                continue
            parts = line.split()
            if len(parts) >= 2:
                name = parts[0]
                url = parts[1] if parts[1].startswith("http") else None
                if name and not name.startswith("-") and name != "Project":
                    all_projects.append({"name": name, "url": url})

        match = re.search(r'--next (\d+)', output)
        if match:
            next_cursor = match.group(1)
        else:
            break

    save_json("vercel-projects.json", all_projects)
    print(f"  Projects: {len(all_projects)}")


def fetch_flyio() -> None:
    """Fetch Fly.io apps via CLI."""
    print("\n=== Fly.io ===")
    import subprocess
    import shutil

    if not shutil.which("fly") and not shutil.which("flyctl"):
        print("  Fly CLI not installed")
        return

    cmd = "fly" if shutil.which("fly") else "flyctl"
    result = subprocess.run([cmd, "apps", "list", "--json"], capture_output=True, text=True)

    try:
        apps = json.loads(result.stdout)
        save_json("flyio-apps.json", apps)
        print(f"  Apps: {len(apps)}")
    except:
        save_json("flyio-apps.json", [])
        print("  Could not parse apps list")


def fetch_cloudflare() -> None:
    """Fetch Cloudflare zones and registrar domains."""
    print("\n=== Cloudflare ===")
    token = os.environ.get("CLOUDFLARE_API_TOKEN")
    if not token:
        print("  CLOUDFLARE_API_TOKEN not set")
        return

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Get all zones
    all_zones = []
    for page in range(1, 5):
        data = api_request(
            f"https://api.cloudflare.com/client/v4/zones?page={page}&per_page=50",
            headers
        )
        zones = data.get("result", [])
        if not zones:
            break
        all_zones.extend(zones)
    save_json("cloudflare-zones.json", all_zones)
    print(f"  Zones: {len(all_zones)}")

    # Get registrar domains - need to get account ID first
    account_data = api_request("https://api.cloudflare.com/client/v4/accounts", headers)
    accounts = account_data.get("result", [])
    if accounts:
        account_id = accounts[0].get("id")
        data = api_request(
            f"https://api.cloudflare.com/client/v4/accounts/{account_id}/registrar/domains",
            headers
        )
        registrar = data.get("result", [])
        save_json("cloudflare-registrar.json", registrar)
        print(f"  Registrar domains: {len(registrar) if isinstance(registrar, list) else 'error'}")


def fetch_godaddy() -> None:
    """Fetch GoDaddy domains."""
    print("\n=== GoDaddy ===")
    api_key = os.environ.get("GODADDY_API_KEY")
    api_secret = os.environ.get("GODADDY_API_SECRET")
    if not api_key or not api_secret:
        print("  GODADDY credentials not set")
        return

    headers = {
        "Authorization": f"sso-key {api_key}:{api_secret}",
        "Content-Type": "application/json"
    }
    data = api_request("https://api.godaddy.com/v1/domains", headers)
    save_json("godaddy-domains.json", data)
    if isinstance(data, list):
        active = [d for d in data if isinstance(d, dict) and d.get("status") == "ACTIVE"]
        print(f"  Domains: {len(data)} total, {len(active)} active")
    else:
        print(f"  Error fetching domains")


def fetch_namecheap() -> None:
    """Fetch Namecheap domains."""
    print("\n=== Namecheap ===")
    api_key = os.environ.get("NAMECHEAP_API_KEY")
    username = os.environ.get("NAMECHEAP_USERNAME")
    if not api_key or not username:
        print("  NAMECHEAP credentials not set")
        return

    try:
        with urllib.request.urlopen("https://api.ipify.org") as resp:
            client_ip = resp.read().decode()
    except:
        print("  Could not get public IP")
        return

    url = f"https://api.namecheap.com/xml.response?ApiUser={username}&ApiKey={api_key}&UserName={username}&Command=namecheap.domains.getList&ClientIp={client_ip}&PageSize=100"

    try:
        with urllib.request.urlopen(url) as resp:
            xml_data = resp.read().decode()

        root = ET.fromstring(xml_data)
        ns = {'nc': 'http://api.namecheap.com/xml.response'}

        domains = []
        for d in root.findall('.//nc:Domain', ns):
            domains.append({
                "name": d.attrib.get("Name"),
                "expires": d.attrib.get("Expires"),
                "auto_renew": d.attrib.get("AutoRenew") == "true",
                "is_locked": d.attrib.get("IsLocked") == "true"
            })
        save_json("namecheap-domains.json", domains)
        print(f"  Domains: {len(domains)}")
    except Exception as e:
        print(f"  Error: {e}")


def fetch_openai() -> None:
    """Fetch OpenAI projects and usage."""
    print("\n=== OpenAI ===")
    api_key = os.environ.get("OPENAI_ADMIN_KEY")
    if not api_key:
        print("  OPENAI_ADMIN_KEY not set")
        return

    headers = {"Authorization": f"Bearer {api_key}"}

    # Get projects
    data = api_request(
        "https://api.openai.com/v1/organization/projects?limit=100",
        headers
    )
    projects = data.get("data", [])
    save_json("openai-projects.json", projects)
    print(f"  Projects: {len(projects)}")

    # Get usage (this month)
    start_ts = int(datetime.now().replace(day=1, hour=0, minute=0, second=0).timestamp())
    data = api_request(
        f"https://api.openai.com/v1/organization/usage/completions?start_time={start_ts}&limit=30&bucket_width=1d",
        headers
    )
    save_json("openai-usage.json", data)

    # Get costs
    data = api_request(
        f"https://api.openai.com/v1/organization/costs?start_time={start_ts}&limit=30&bucket_width=1d",
        headers
    )
    save_json("openai-costs.json", data)


def fetch_anthropic() -> None:
    """Fetch Anthropic workspaces, API keys, usage, and costs."""
    print("\n=== Anthropic ===")
    api_key = os.environ.get("ANTHROPIC_ADMIN_KEY")
    if not api_key:
        print("  ANTHROPIC_ADMIN_KEY not set")
        return

    headers = {"x-api-key": api_key, "anthropic-version": "2023-06-01"}

    # Get workspaces
    data = api_request("https://api.anthropic.com/v1/organizations/workspaces", headers)
    workspaces = data.get("data", [])
    save_json("anthropic-workspaces.json", workspaces)
    print(f"  Workspaces: {len(workspaces)}")

    # Get API keys
    data = api_request("https://api.anthropic.com/v1/organizations/api_keys?limit=100", headers)
    api_keys = data.get("data", [])
    save_json("anthropic-api-keys.json", api_keys)
    print(f"  API Keys: {len(api_keys)}")

    # Get usage (last 7 days)
    end = datetime.now()
    start = end - timedelta(days=7)
    url = f"https://api.anthropic.com/v1/organizations/usage_report/messages?starting_at={start.strftime('%Y-%m-%dT00:00:00Z')}&ending_at={end.strftime('%Y-%m-%dT23:59:59Z')}&bucket_width=1d&group_by[]=model"
    data = api_request(url, headers)
    save_json("anthropic-usage.json", data)
    print(f"  Usage: {len(data.get('data', []))} days")

    # Get costs (last 30 days)
    start = end - timedelta(days=30)
    url = f"https://api.anthropic.com/v1/organizations/cost_report?starting_at={start.strftime('%Y-%m-%dT00:00:00Z')}&ending_at={end.strftime('%Y-%m-%dT23:59:59Z')}&group_by[]=workspace_id"
    data = api_request(url, headers)
    save_json("anthropic-costs.json", data)

    total_cost = 0
    for bucket in data.get("data", []):
        for r in bucket.get("results", []):
            try:
                total_cost += float(r.get("amount", 0))
            except:
                pass
    print(f"  Cost (30d): ${total_cost:.2f}")


def fetch_all() -> None:
    """Fetch data from all configured providers."""
    print("=" * 50)
    print("Infralens - Fetching Data")
    print(f"Time: {datetime.now().isoformat()}")
    print("=" * 50)

    load_env()

    fetch_vercel()
    fetch_flyio()
    fetch_cloudflare()
    fetch_godaddy()
    fetch_namecheap()
    fetch_openai()
    fetch_anthropic()

    print("\n" + "=" * 50)
    print(f"Data saved to: {_DATA_DIR}")
    print("=" * 50)


if __name__ == "__main__":
    fetch_all()

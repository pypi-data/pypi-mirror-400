"""Configuration management for Infralens."""

import os
from pathlib import Path
from dataclasses import dataclass

CONFIG_DIR = Path.home() / ".infralens"
ENV_FILE = CONFIG_DIR / ".env"
DATA_DIR = CONFIG_DIR / "data"


@dataclass
class Provider:
    name: str
    env_vars: list[str]
    guide_url: str
    guide_steps: list[str]


PROVIDERS = {
    "godaddy": Provider(
        name="GoDaddy",
        env_vars=["GODADDY_API_KEY", "GODADDY_API_SECRET"],
        guide_url="https://developer.godaddy.com/keys",
        guide_steps=[
            "Go to https://developer.godaddy.com/keys",
            "Click 'Create New API Key'",
            "Select 'Production' environment",
            "Copy the Key and Secret",
        ],
    ),
    "cloudflare": Provider(
        name="Cloudflare",
        env_vars=["CLOUDFLARE_API_TOKEN"],
        guide_url="https://dash.cloudflare.com/profile/api-tokens",
        guide_steps=[
            "Go to https://dash.cloudflare.com/profile/api-tokens",
            "Click 'Create Token'",
            "Use 'Read all resources' template (or custom with Zone:Read, DNS:Read)",
            "Copy the token (shown only once)",
        ],
    ),
    "namecheap": Provider(
        name="Namecheap",
        env_vars=["NAMECHEAP_API_KEY", "NAMECHEAP_USERNAME"],
        guide_url="https://ap.www.namecheap.com/settings/tools/apiaccess",
        guide_steps=[
            "Go to https://ap.www.namecheap.com/settings/tools/apiaccess",
            "Enable API Access (may require support ticket)",
            "Add your IP to the whitelist",
            "Copy your API Key and Username",
        ],
    ),
    "vercel": Provider(
        name="Vercel",
        env_vars=[],  # Uses CLI authentication
        guide_url="",
        guide_steps=[
            "Install Vercel CLI: npm i -g vercel",
            "Run: vercel login",
            "No API key needed - uses CLI auth",
        ],
    ),
    "flyio": Provider(
        name="Fly.io",
        env_vars=[],  # Uses CLI authentication
        guide_url="",
        guide_steps=[
            "Install Fly CLI: brew install flyctl (or curl installer)",
            "Run: fly auth login",
            "No API key needed - uses CLI auth",
        ],
    ),
    "openai": Provider(
        name="OpenAI",
        env_vars=["OPENAI_ADMIN_KEY"],
        guide_url="https://platform.openai.com/settings/organization/admin-keys",
        guide_steps=[
            "Go to https://platform.openai.com/settings/organization/admin-keys",
            "Click 'Create new admin key'",
            "Copy the key (starts with sk-admin-)",
            "Note: Requires organization Owner role",
        ],
    ),
    "anthropic": Provider(
        name="Anthropic",
        env_vars=["ANTHROPIC_ADMIN_KEY"],
        guide_url="https://console.anthropic.com/settings/admin-keys",
        guide_steps=[
            "Go to https://console.anthropic.com/settings/admin-keys",
            "Click 'Create Key'",
            "Copy the key (starts with sk-ant-admin-)",
            "Note: Requires organization Admin role",
        ],
    ),
}


def get_config_dir() -> Path:
    """Get or create the config directory."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return CONFIG_DIR


def load_env() -> dict[str, str]:
    """Load environment variables from config file and local .env."""
    env = {}

    # First load from ~/.infralens/.env
    if ENV_FILE.exists():
        env.update(_parse_env_file(ENV_FILE))

    # Then load from local .env (for development)
    local_env = Path.cwd() / ".env"
    if local_env.exists():
        env.update(_parse_env_file(local_env))

    # Apply to os.environ
    for key, value in env.items():
        os.environ.setdefault(key, value)

    return env


def _parse_env_file(path: Path) -> dict[str, str]:
    """Parse a .env file into a dict."""
    env = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                env[key.strip()] = value.strip()
    return env


def save_env(values: dict[str, str]) -> None:
    """Save environment variables to config file."""
    get_config_dir()

    # Load existing values
    existing = {}
    if ENV_FILE.exists():
        existing = _parse_env_file(ENV_FILE)

    # Merge with new values
    existing.update(values)

    # Write back with restrictive permissions (owner read/write only)
    with open(ENV_FILE, "w") as f:
        for key, value in sorted(existing.items()):
            f.write(f"{key}={value}\n")

    # Set file permissions to 600 (owner only)
    ENV_FILE.chmod(0o600)


def get_configured_providers() -> dict[str, bool]:
    """Check which providers are configured."""
    load_env()
    result = {}

    for provider_id, provider in PROVIDERS.items():
        if not provider.env_vars:
            # CLI-based providers - check if command exists
            result[provider_id] = _check_cli(provider_id)
        else:
            # API-based providers - check if all env vars are set
            result[provider_id] = all(
                os.environ.get(var) for var in provider.env_vars
            )

    return result


def _check_cli(provider_id: str) -> bool:
    """Check if a CLI tool is available."""
    import shutil

    cli_map = {
        "vercel": "vercel",
        "flyio": "fly",
    }
    cmd = cli_map.get(provider_id)
    return shutil.which(cmd) is not None if cmd else False

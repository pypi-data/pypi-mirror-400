# Infralens

Terminal dashboard for cloud infrastructure - domains, hosting, and AI spend.

## Quick Reference

```bash
uv run infralens          # Launch TUI dashboard
uv run infralens setup    # Run setup wizard
uv run infralens fetch    # Refresh data from APIs
```

## Architecture

```
infralens/
├── cli.py           # Entry point, command routing
├── app.py           # Main Textual TUI app
├── setup.py         # Interactive setup wizard
├── config.py        # Credentials (~/.infralens/.env)
├── data.py          # JSON loader, domain types, alerts
└── fetch.py         # Data fetcher (7 providers)
```

## Data Sources

| Provider | Type | Method | Data |
|----------|------|--------|------|
| Vercel | Hosting | CLI | Projects |
| Fly.io | Hosting | CLI | Apps |
| Cloudflare | DNS/CDN | REST | Zones, registrar domains |
| GoDaddy | Registrar | REST | Domains |
| Namecheap | Registrar | XML | Domains (requires IP whitelist) |
| OpenAI | AI API | REST | Projects, usage, costs |
| Anthropic | AI API | REST | Workspaces, API keys, usage |

## TUI Navigation

| Key | Action |
|-----|--------|
| `1-5` | Jump to screen |
| `Tab` | Next screen / panel |
| `Enter` | Activate Panel Mode |
| `Esc` | Exit Panel Mode |
| `r` | Refresh data |
| `q` | Quit |

## Configuration

User credentials: `~/.infralens/.env`
Data cache: `~/.infralens/data/` (or local `data/` in dev)

## Code Style

- Python 3.12+, Textual for TUI
- Fetch module uses stdlib only (no deps beyond textual)
- JSON files are cache, not source of truth

## Development

```bash
# Install dependencies
uv sync

# Run locally
uv run infralens
uv run infralens setup
uv run infralens fetch

# Test changes to setup wizard
uv run infralens setup
```

## Publishing

```bash
uv build
uv publish
```

## Contributing

- Keep fetch module stdlib-only (no external deps)
- Use coral theme colors: `#a65d40` (primary), `#cc7755` (accent)
- All focus states need `border: tall transparent` when unfocused to prevent size shifts

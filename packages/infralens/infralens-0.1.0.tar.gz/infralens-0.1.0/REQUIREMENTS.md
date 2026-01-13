# Cloud Inventory TUI - Requirements

## Overview

Terminal-based dashboard for daily infrastructure monitoring with light management actions.

**Framework:** Textual (Python)
**Usage Pattern:** Daily check-in, quick visibility into all cloud resources

---

## Core Views

### 0. Projects View (Primary)

**Project = linked set of resources:**
```
Project: "myapp"
├── Local repo: ~/dev/myapp
├── Remote: github.com/user/myapp
├── Domain(s): myapp.com, www.myapp.com
├── DNS: Cloudflare zone
└── Hosting: Vercel project / Fly.io app
```

**Auto-detection:**
1. Scan local repos (~/dev/**)
2. Match to Vercel/Fly projects by name
3. Match domains by name similarity
4. Present matches for confirmation
5. Save to `projects.json`

**Project List View:**
- Project name
- Status indicators (all green = healthy)
- Last deploy date
- Domain status

**Project Detail View:**
- All linked resources
- One-click open any dashboard
- Deploy button (Vercel/Fly)
- DNS record editor

**Actions:**
| Action | Description |
|--------|-------------|
| Create project | Wizard: name, init repo, pick domain, setup DNS, deploy |
| Link existing | Connect existing repo to domain/hosting |
| Quick deploy | `vercel --prod` or `fly deploy` |
| Manage DNS | Add/edit/delete records in Cloudflare |
| Unlink | Remove associations (not delete resources) |

**New Project Wizard:**
1. Project name
2. Create local repo or select existing
3. Init git remote (GitHub)
4. Register/select domain
5. Create Cloudflare zone + DNS
6. Deploy to Vercel or Fly.io
7. Verify everything connected

---

### 1. Unified Dashboard (Home)

Single-screen overview showing:
- **Status bar:** Last refresh time, total monthly spend
- **Domain summary:** X domains, Y expiring soon, Z without auto-renew
- **Hosting summary:** X Vercel projects, Y Fly.io apps, active/inactive counts
- **AI spend widget:** Current month spend (OpenAI + Anthropic combined)
- **Alerts panel:** Critical items needing attention

### 2. Domains View

Tabbed by registrar (GoDaddy | Namecheap | Cloudflare) or unified list.

For each domain:
- Domain name
- Registrar
- Expiry date (with color coding: red <30d, yellow <90d)
- Auto-renew status (flag if disabled)
- DNS provider (if different from registrar)

**Alerts:**
- Domains expiring within 30/60/90 days
- Domains without auto-renew enabled
- Missing expected DNS records (future)

**Actions:**
- Open domain in registrar dashboard
- Copy domain name
- Filter by status/registrar

### 3. DNS Zones View

Cloudflare zones with:
- Zone name
- Status (active/pending)
- Record count
- Plan type

**Actions:**
- Open zone in Cloudflare
- List records (expandable)

### 4. Hosting View

**Vercel Projects:**
- Project name
- Framework detected
- Last deployment date
- Production URL

**Fly.io Apps:**
- App name
- Status (running/stopped)
- Region
- Machine count

**Actions:**
- Open project/app dashboard
- Copy production URL

### 5. AI Spend View

**Summary panel:**
- Total spend this month (all providers)
- Daily average
- Projected month-end

**Drill-down tabs:**

| Level | OpenAI | Anthropic |
|-------|--------|-----------|
| Total | $X.XX | $Y.YY |
| By Project/Workspace | Table | Table |
| By Model | gpt-4o, gpt-4, etc | claude-3-opus, etc |
| Daily trend | Sparkline/chart | Sparkline/chart |

**Alerts:**
- Unusual spend spike (>2x daily average)
- Approaching budget threshold (if set)

---

## Quick Actions

| Key | Action |
|-----|--------|
| `r` | Refresh all data |
| `R` | Refresh current view only |
| `o` | Open selected item in browser |
| `y` | Copy selected item details to clipboard |
| `?` | Show help/keybindings |
| `q` | Quit |
| `/` | Filter/search |
| `Tab` | Switch views |

---

## Data Layer

- Read from `data/*.json` files (already fetched)
- Background refresh option (call fetch-all.py)
- Show "stale" indicator if data >24h old
- No direct API calls from TUI (delegate to fetcher)

---

## Alerts System

Priority levels:
1. **Critical (red):** Domain expiring <30 days, unusual spend
2. **Warning (yellow):** Domain expiring <90 days, auto-renew off
3. **Info (blue):** Data stale, new items detected

Alerts shown in:
- Dashboard alerts panel
- View-specific inline indicators
- Optional: Desktop notification for critical

---

## Write Operations (API Requirements)

For full CRUD functionality, these APIs need write access:

| Operation | Provider | API Required |
|-----------|----------|--------------|
| Deploy | Vercel | CLI (`vercel --prod`) |
| Deploy | Fly.io | CLI (`fly deploy`) |
| DNS records | Cloudflare | REST (current token may be read-only) |
| Create zone | Cloudflare | REST |
| Git remote | GitHub | CLI (`gh repo create`) or SSH |

**Note:** Current `.env` tokens are read-only. For write operations:
- Cloudflare: Need token with Zone:Edit, DNS:Edit permissions
- GitHub: Use `gh` CLI (already authenticated) or add PAT

---

## Nice-to-Have (Future)

- [ ] Budget setting for AI spend
- [ ] Domain purchase history
- [ ] SSL certificate monitoring
- [ ] Deployment logs viewer
- [ ] Multi-account support
- [ ] Export to CSV
- [ ] Scheduled refresh via cron
- [ ] Webhook/notification integrations

---

## Technical Notes

**Dependencies:**
- `textual` - TUI framework
- `rich` - Formatting (bundled with textual)
- `pyperclip` - Clipboard (optional)

**Structure:**
```
cloud-inventory/
├── fetch-all.py          # Data fetcher (existing)
├── projects.json         # Linked project definitions
├── tui/
│   ├── __init__.py
│   ├── app.py            # Main Textual app
│   ├── screens/
│   │   ├── projects.py   # Project list + detail
│   │   ├── dashboard.py
│   │   ├── domains.py
│   │   ├── dns.py
│   │   ├── hosting.py
│   │   └── spend.py
│   ├── widgets/
│   │   ├── alerts.py
│   │   ├── summary.py
│   │   ├── table.py
│   │   └── wizard.py     # Multi-step forms
│   ├── data.py           # JSON loading/parsing
│   └── actions.py        # Deploy, DNS, etc.
├── actions/
│   ├── deploy.py         # Vercel/Fly deploy wrappers
│   ├── dns.py            # Cloudflare DNS management
│   ├── git.py            # Repo init, remote setup
│   └── detect.py         # Auto-link detection
└── pyproject.toml
```

**Entry point:**
```bash
uv run python -m tui.app
# or alias: uv run cloud-tui
```

"""Infralens - Infrastructure monitoring dashboard."""

from datetime import datetime

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import (
    DataTable,
    Footer,
    Header,
    Label,
    Static,
    TabbedContent,
    TabPane,
)

from infralens.data import (
    get_domain_alerts,
    get_last_refresh,
    is_data_stale,
    load_ai_costs,
    load_ai_usage,
    load_ai_workspaces,
    load_cloudflare_zones,
    load_domains,
    load_hosting,
)


class SummaryCard(Static):
    DEFAULT_CSS = """
    SummaryCard {
        width: 1fr;
        height: auto;
        border: solid #a65d40;
        padding: 1 2;
        margin: 0 1 0 0;
        background: #2d2d2d;
    }
    SummaryCard:last-of-type {
        margin-right: 0;
    }
    """

    def __init__(self, title: str, value: str, subtitle: str = "") -> None:
        super().__init__()
        self._title = title
        self._value = value
        self._subtitle = subtitle

    def compose(self) -> ComposeResult:
        yield Label(self._title, classes="card-title")
        yield Label(self._value, classes="card-value")
        if self._subtitle:
            yield Label(self._subtitle, classes="card-subtitle")


class InfralensApp(App):
    CSS = """
    * {
        scrollbar-color: #a65d40;
        scrollbar-background: #2d2d2d;
    }

    Screen {
        background: #1e1e1e;
    }

    Header {
        background: #2d2d2d;
        color: #cc7755;
    }

    Footer {
        background: #2d2d2d;
    }

    Footer > .footer-key--key {
        background: #a65d40;
        color: #1e1e1e;
    }

    Footer > .footer-key--description {
        color: #d4d4d4;
    }

    TabbedContent {
        height: 1fr;
    }

    ContentSwitcher {
        height: 1fr;
    }

    TabPane {
        height: 1fr;
        padding: 1;
        background: #1e1e1e;
    }

    Tabs {
        background: #2d2d2d;
    }

    Tab {
        color: #808080;
        background: #2d2d2d;
    }

    Tab:hover {
        color: #d4d4d4;
    }

    Tab.-active {
        color: #cc7755;
        text-style: bold;
        background: #3d3d3d;
    }

    Underline {
        height: 0;
    }

    VerticalScroll {
        height: 1fr;
    }

    .cards-row {
        height: auto;
        margin-bottom: 1;
    }

    .card-title {
        color: #808080;
    }

    .card-value {
        color: #cc7755;
        text-style: bold;
    }

    .card-subtitle {
        color: #808080;
    }

    .section-title {
        color: #cc7755;
        text-style: bold;
        margin: 1 0 0 0;
    }

    .meta-info {
        color: #808080;
        margin: 0 0 1 0;
    }

    .muted {
        color: #808080;
    }

    .success {
        color: #6a9955;
    }

    .alert-critical {
        color: #f14c4c;
    }

    .alert-warning {
        color: #dcdcaa;
    }

    DataTable {
        height: auto;
        max-height: 20;
        margin: 1 0;
        background: #2d2d2d;
    }

    DataTable > .datatable--header {
        background: #2d2d2d;
        color: #cc7755;
        text-style: bold;
    }

    DataTable > .datatable--cursor {
        background: #a65d40;
        color: #d4d4d4;
    }
    """

    BINDINGS = [
        Binding("1", "switch_tab('dashboard')", "1", priority=True),
        Binding("2", "switch_tab('domains')", "2", priority=True),
        Binding("3", "switch_tab('dns')", "3", priority=True),
        Binding("4", "switch_tab('hosting')", "4", priority=True),
        Binding("5", "switch_tab('spend')", "5", priority=True),
        Binding("tab", "next_tab", "Tab", priority=True),
        Binding("shift+tab", "prev_tab", show=False, priority=True),
        Binding("enter", "activate_panel", "Enter", priority=True),
        Binding("escape", "deactivate_panel", "Esc", priority=True),
        Binding("r", "refresh", "Refresh", priority=True),
        Binding("q", "quit", "Quit", priority=True),
    ]

    TITLE = "Cloud Inventory"

    def __init__(self, first_run: bool = False) -> None:
        super().__init__()
        self._panel_active = False
        self._tab_order = ["dashboard", "domains", "dns", "hosting", "spend"]
        self._first_run = first_run

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent():
            with TabPane("[1] Dashboard", id="dashboard"):
                yield from self._dashboard_content()
            with TabPane("[2] Domains", id="domains"):
                yield from self._domains_content()
            with TabPane("[3] DNS", id="dns"):
                yield from self._dns_content()
            with TabPane("[4] Hosting", id="hosting"):
                yield from self._hosting_content()
            with TabPane("[5] Spend", id="spend"):
                yield from self._spend_content()
        yield Footer()

    def _dashboard_content(self) -> ComposeResult:
        domains = load_domains()
        active_domains = [d for d in domains if d.status == "ACTIVE"]
        alerts = get_domain_alerts()
        hosting = load_hosting()
        costs = load_ai_costs()
        last_refresh = get_last_refresh()

        refresh_str = "Never"
        if last_refresh:
            refresh_str = last_refresh.strftime("%Y-%m-%d %H:%M")
            if is_data_stale():
                refresh_str += " (stale)"

        with Horizontal(classes="cards-row"):
            yield SummaryCard("Domains", str(len(active_domains)), "active")
            yield SummaryCard("Alerts", str(len(alerts)), "pending")
            yield SummaryCard("Projects", str(len(hosting)), "hosted")
            yield SummaryCard("AI Spend", f"${costs['total']:.2f}", "this month")

        yield Label(f"Last refresh: {refresh_str}", classes="meta-info")
        yield Label("Alerts", classes="section-title")

        if alerts:
            for level, domain, message in alerts[:10]:
                cls = "alert-critical" if level == "critical" else "alert-warning"
                yield Label(f"  {domain}: {message}", classes=cls)
        else:
            yield Label("  All clear - no alerts", classes="success")

    def _domains_content(self) -> ComposeResult:
        yield Label("Active Domains", classes="section-title")

        table = DataTable()
        table.add_columns("Domain", "Registrar", "Expires", "Auto-Renew")

        now = datetime.now()
        for d in load_domains():
            if d.status != "ACTIVE":
                continue
            exp_str = "-"
            if d.expires:
                days = (d.expires.replace(tzinfo=None) - now).days
                exp_str = f"{d.expires.strftime('%Y-%m-%d')} ({days}d)"
            renew = "Yes" if d.auto_renew else "No"
            table.add_row(d.name, d.registrar, exp_str, renew)

        yield table

    def _dns_content(self) -> ComposeResult:
        yield Label("Cloudflare Zones", classes="section-title")

        table = DataTable()
        table.add_columns("Zone", "Status", "Plan")

        for zone in load_cloudflare_zones():
            if isinstance(zone, dict):
                table.add_row(
                    zone.get("name", ""),
                    zone.get("status", ""),
                    zone.get("plan", {}).get("name", ""),
                )

        yield table

    def _hosting_content(self) -> ComposeResult:
        hosting = load_hosting()
        vercel = [p for p in hosting if p.provider == "Vercel"]
        flyio = [p for p in hosting if p.provider == "Fly.io"]

        yield Label(f"Vercel Projects ({len(vercel)})", classes="section-title")
        if vercel:
            v_table = DataTable()
            v_table.add_columns("Project", "URL")
            for p in vercel:
                v_table.add_row(p.name, p.url or "-")
            yield v_table
        else:
            yield Label("  No projects", classes="muted")

        yield Label(f"Fly.io Apps ({len(flyio)})", classes="section-title")
        if flyio:
            f_table = DataTable()
            f_table.add_columns("App", "Status", "URL")
            for p in flyio:
                f_table.add_row(p.name, p.status, p.url or "-")
            yield f_table
        else:
            yield Label("  No apps", classes="muted")

    def _spend_content(self) -> ComposeResult:
        costs = load_ai_costs()
        usage = load_ai_usage()
        workspaces = load_ai_workspaces()

        yield Label("Cost Summary", classes="section-title")
        yield Label(f"  Total: ${costs['total']:.2f} this month")
        yield Label(f"  OpenAI: ${costs['openai']:.2f} (prepaid)")
        yield Label(f"  Anthropic: ${costs['anthropic']:.2f} (pay-as-you-go)")

        yield Label("Anthropic Usage (7 days)", classes="section-title")
        if usage["anthropic"]:
            a_table = DataTable()
            a_table.add_columns("Model", "Input", "Output", "Total")
            for model, tokens in sorted(usage["anthropic"].items()):
                total = tokens["input"] + tokens["output"]
                a_table.add_row(model, f"{tokens['input']:,}", f"{tokens['output']:,}", f"{total:,}")
            yield a_table
        else:
            yield Label("  No usage", classes="muted")

        yield Label("OpenAI Usage (this month)", classes="section-title")
        if usage["openai"]:
            o_table = DataTable()
            o_table.add_columns("Model", "Input", "Output", "Total")
            for model, tokens in sorted(usage["openai"].items()):
                total = tokens["input"] + tokens["output"]
                o_table.add_row(model, f"{tokens['input']:,}", f"{tokens['output']:,}", f"{total:,}")
            yield o_table
        else:
            yield Label("  No usage this month", classes="muted")

        yield Label("Workspaces & Projects", classes="section-title")
        w_table = DataTable()
        w_table.add_columns("Provider", "Name")
        for w in workspaces:
            w_table.add_row(w.provider, w.name)
        yield w_table

    def on_mount(self) -> None:
        if self._first_run:
            self.notify("Fetching data from providers...")
            self.run_worker(self._do_refresh, exclusive=True, thread=True)

    def action_refresh(self) -> None:
        self.notify("Refreshing data...")
        self.run_worker(self._do_refresh, exclusive=True, thread=True)

    def _do_refresh(self) -> None:
        try:
            from infralens.fetch import fetch_all
            fetch_all()
            self.call_from_thread(self._on_refresh_done)
        except Exception as e:
            self.call_from_thread(lambda: self.notify(f"Refresh failed: {e}", severity="error"))

    def _on_refresh_done(self) -> None:
        self.notify("Data refreshed!", severity="information")
        self.refresh(recompose=True)

    def action_switch_tab(self, tab_id: str) -> None:
        self._panel_active = False
        tabs = self.query_one(TabbedContent)
        tabs.active = tab_id
        tabs.focus()
        self.sub_title = ""

    def action_next_tab(self) -> None:
        if self._panel_active:
            self.screen.focus_next()
        else:
            tabs = self.query_one(TabbedContent)
            current = tabs.active
            if current in self._tab_order:
                idx = self._tab_order.index(current)
                next_idx = (idx + 1) % len(self._tab_order)
                tabs.active = self._tab_order[next_idx]

    def action_prev_tab(self) -> None:
        if self._panel_active:
            self.screen.focus_previous()
        else:
            tabs = self.query_one(TabbedContent)
            current = tabs.active
            if current in self._tab_order:
                idx = self._tab_order.index(current)
                prev_idx = (idx - 1) % len(self._tab_order)
                tabs.active = self._tab_order[prev_idx]

    def action_activate_panel(self) -> None:
        if not self._panel_active:
            self._panel_active = True
            self.sub_title = "[Panel Mode - Tab to navigate, Esc to exit]"
            # Get active tab pane and focus its first table
            tabs = self.query_one(TabbedContent)
            active_pane = tabs.query_one(f"#{tabs.active}", TabPane)
            if active_pane:
                tables = active_pane.query(DataTable)
                if tables:
                    tables.first().focus()

    def action_deactivate_panel(self) -> None:
        if self._panel_active:
            self._panel_active = False
            self.sub_title = ""
            self.set_focus(None)


def main():
    app = InfralensApp()
    app.run()


if __name__ == "__main__":
    main()

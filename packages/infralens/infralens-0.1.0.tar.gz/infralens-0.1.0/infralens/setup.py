"""Interactive setup wizard for Infralens."""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, Horizontal, VerticalScroll, Center
from textual.widgets import (
    Button,
    Checkbox,
    Footer,
    Header,
    Input,
    Label,
)
from textual.screen import Screen

from infralens.config import PROVIDERS, get_configured_providers, save_env


class WelcomeScreen(Screen):
    """Welcome screen with provider selection."""

    CSS = """
    WelcomeScreen {
        background: #1e1e1e;
        align: center middle;
    }

    .main-container {
        width: 60;
        height: auto;
        max-height: 90%;
        background: #2d2d2d;
        border: solid #3d3d3d;
        padding: 1 2;
    }

    .welcome-title {
        text-align: center;
        color: #cc7755;
        text-style: bold;
        margin-bottom: 1;
    }

    .welcome-subtitle {
        text-align: center;
        color: #808080;
        margin-bottom: 1;
    }

    .provider-item {
        height: 3;
    }

    .provider-status {
        color: #6a9955;
        margin: 0 0 0 2;
    }

    .provider-missing {
        color: #808080;
        margin: 0 0 0 2;
    }

    .button-row {
        margin-top: 1;
        height: 3;
        align: center middle;
    }

    Button {
        margin: 0 1;
    }

    .primary-button {
        background: #a65d40;
    }
    """

    BINDINGS = [
        Binding("enter", "continue", "Continue"),
        Binding("escape", "quit", "Quit"),
        Binding("tab", "focus_next", "Tab", show=False),
        Binding("up", "focus_previous", "Up", show=False),
        Binding("down", "focus_next", "Down", show=False),
    ]

    def __init__(self):
        super().__init__()
        self.selected_providers: set[str] = set()

    def compose(self) -> ComposeResult:
        yield Header()
        configured = get_configured_providers()

        with Vertical(classes="main-container"):
            yield Label("Infralens Setup", classes="welcome-title")
            yield Label("Select providers to configure", classes="welcome-subtitle")

            for provider_id, provider in PROVIDERS.items():
                is_configured = configured.get(provider_id, False)
                with Horizontal(classes="provider-item"):
                    checkbox = Checkbox(provider.name, id=f"check-{provider_id}")
                    if is_configured:
                        checkbox.value = True
                        self.selected_providers.add(provider_id)
                    yield checkbox
                    if is_configured:
                        yield Label("[ok]", classes="provider-status")
                    elif not provider.env_vars:
                        yield Label("[CLI]", classes="provider-missing")

            with Horizontal(classes="button-row"):
                yield Button("Continue", variant="primary", id="continue", classes="primary-button")
                yield Button("Skip", id="skip")
        yield Footer()

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        provider_id = event.checkbox.id.replace("check-", "")
        if event.value:
            self.selected_providers.add(provider_id)
        else:
            self.selected_providers.discard(provider_id)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "continue":
            self.action_continue()
        elif event.button.id == "skip":
            self.app.exit()

    def action_continue(self) -> None:
        to_configure = list(self.selected_providers)
        if to_configure:
            self.app.push_screen(ProviderSetupScreen(to_configure))
        else:
            self.app.push_screen(CompleteScreen(False))

    def action_quit(self) -> None:
        self.app.exit()

    def action_focus_next(self) -> None:
        self.screen.focus_next()

    def action_focus_previous(self) -> None:
        self.screen.focus_previous()


class ProviderSetupScreen(Screen):
    """Screen for configuring a single provider."""

    CSS = """
    ProviderSetupScreen {
        background: #1e1e1e;
        align: center middle;
    }

    .setup-container {
        width: 70;
        height: auto;
        padding: 2;
        background: #2d2d2d;
        border: solid #3d3d3d;
    }

    .progress {
        color: #808080;
        text-align: right;
        margin-bottom: 1;
    }

    .provider-title {
        color: #cc7755;
        text-style: bold;
        margin-bottom: 1;
    }

    .security-note {
        color: #6a9955;
        margin-bottom: 1;
    }

    .step-label {
        color: #d4d4d4;
        margin: 0 0 0 2;
    }

    .guide-url {
        color: #cc7755;
        margin: 1 0;
    }

    .input-label {
        color: #808080;
        margin-top: 1;
    }

    .skip-hint {
        color: #808080;
        margin-top: 1;
    }

    Input {
        margin: 0 0 1 0;
        border: tall transparent;
    }

    Input:focus {
        border: tall #a65d40;
    }

    .button-row {
        margin-top: 1;
        height: 3;
        align: center middle;
    }

    Button {
        margin: 0 1;
        border: tall transparent;
    }

    Button:focus {
        border: tall #a65d40;
    }

    Button.-primary {
        background: #a65d40;
    }
    """

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("enter", "next", "Next"),
        Binding("tab", "focus_next", "Tab", show=False),
        Binding("up", "focus_previous", "Up", show=False),
        Binding("down", "focus_next", "Down", show=False),
    ]

    def __init__(self, providers: list[str]):
        super().__init__()
        self.providers = providers
        self.current_index = 0
        self.collected_values: dict[str, str] = {}

    @property
    def current_provider(self):
        return PROVIDERS[self.providers[self.current_index]]

    @property
    def current_provider_id(self):
        return self.providers[self.current_index]

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="setup-container"):
            yield Label(
                f"{self.current_index + 1} / {len(self.providers)}",
                classes="progress",
                id="progress"
            )
            yield from self._provider_content()

            with Horizontal(classes="button-row"):
                yield Button("Back", id="back")
                yield Button("Skip", id="skip")
                yield Button("Next", variant="primary", id="next")
        yield Footer()

    def _provider_content(self) -> ComposeResult:
        provider = self.current_provider
        yield Label(f"Configure {provider.name}", classes="provider-title", id="title")

        if provider.env_vars:
            yield Label("Saved locally in ~/.infralens/.env", classes="security-note", id="security")
            yield Label("How to get your key:", classes="input-label", id="steps-label")
        else:
            yield Label("Uses CLI authentication (no API key needed)", classes="security-note", id="security")
            yield Label("Setup steps:", classes="input-label", id="steps-label")

        for i, step in enumerate(provider.guide_steps, 1):
            yield Label(f"  {i}. {step}", classes="step-label", id=f"step-{i}")

        if provider.guide_url:
            yield Label(f"{provider.guide_url}", classes="guide-url", id="url")

        for var in provider.env_vars:
            yield Label(var, classes="input-label", id=f"label-{var}")
            yield Input(
                placeholder=f"Paste {var} here (or leave empty to skip)",
                password="SECRET" in var or "KEY" in var,
                id=f"input-{var}",
            )

        if provider.env_vars:
            yield Label("Leave empty to configure later manually", classes="skip-hint", id="skip-hint")
        else:
            yield Label("Press Next when CLI is installed", classes="skip-hint", id="skip-hint")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self._save_current()
        self._next_provider()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "next":
            self._save_current()
            self._next_provider()
        elif event.button.id == "skip":
            self._next_provider()
        elif event.button.id == "back":
            self.action_back()

    def action_next(self) -> None:
        self._save_current()
        self._next_provider()

    def _save_current(self) -> None:
        provider = self.current_provider
        for var in provider.env_vars:
            try:
                input_widget = self.query_one(f"#input-{var}", Input)
                if input_widget.value:
                    self.collected_values[var] = input_widget.value
            except:
                pass

    def _next_provider(self) -> None:
        self.current_index += 1
        if self.current_index >= len(self.providers):
            if self.collected_values:
                save_env(self.collected_values)
            self.app.push_screen(CompleteScreen(bool(self.collected_values)))
        else:
            self.refresh(recompose=True)

    def action_back(self) -> None:
        if self.current_index > 0:
            self.current_index -= 1
            self.refresh(recompose=True)
        else:
            self.app.pop_screen()

    def action_focus_next(self) -> None:
        self.screen.focus_next()

    def action_focus_previous(self) -> None:
        self.screen.focus_previous()


class CompleteScreen(Screen):
    """Setup complete screen."""

    CSS = """
    CompleteScreen {
        background: #1e1e1e;
        align: center middle;
    }

    .complete-box {
        width: 50;
        height: auto;
        padding: 2;
        background: #2d2d2d;
        border: solid #3d3d3d;
    }

    .complete-title {
        color: #6a9955;
        text-style: bold;
        text-align: center;
        margin-bottom: 1;
    }

    .complete-message {
        color: #d4d4d4;
        text-align: center;
        margin-bottom: 1;
    }

    .complete-path {
        color: #cc7755;
        text-align: center;
        margin-bottom: 1;
    }

    .complete-hint {
        color: #808080;
        text-align: center;
        margin-bottom: 2;
    }

    Button {
        width: 100%;
        border: tall transparent;
    }

    Button:focus {
        border: tall #a65d40;
    }

    Button.-primary {
        background: #a65d40;
    }
    """

    BINDINGS = [
        Binding("enter", "launch", "Launch"),
        Binding("escape", "quit", "Quit"),
    ]

    def __init__(self, has_credentials: bool = True):
        super().__init__()
        self.has_credentials = has_credentials

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="complete-box"):
            yield Label("Setup Complete!", classes="complete-title")
            if self.has_credentials:
                yield Label("Credentials saved to:", classes="complete-message")
                yield Label("~/.infralens/.env", classes="complete-path")
            else:
                yield Label("No credentials were added.", classes="complete-message")
                yield Label("Add them manually to ~/.infralens/.env", classes="complete-path")
            yield Label("Run 'infralens fetch' to pull data.", classes="complete-hint")
            yield Button("Launch Infralens", variant="primary", id="launch")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "launch":
            self.action_launch()

    def action_launch(self) -> None:
        self.app.exit(result="launch")

    def action_quit(self) -> None:
        self.app.exit()


class SetupApp(App):
    """Setup wizard application."""

    CSS = """
    * {
        scrollbar-color: #a65d40;
        scrollbar-background: #2d2d2d;
    }

    Button {
        border: tall transparent;
    }

    Button:focus {
        border: tall #a65d40;
    }

    Button.-primary {
        background: #a65d40;
    }

    Button.-primary:hover {
        background: #cc7755;
    }

    Checkbox {
        border: tall transparent;
    }

    Checkbox:focus {
        border: tall #a65d40;
    }

    Checkbox > .toggle--button {
        background: #3d3d3d;
        color: #808080;
    }

    Checkbox.-on > .toggle--button {
        background: #a65d40;
        color: #1e1e1e;
    }

    Checkbox > .toggle--label {
        text-style: none;
    }

    Checkbox:focus > .toggle--label {
        text-style: bold;
        background: #3d3d3d;
        color: #ffffff;
    }

    Input {
        border: tall transparent;
    }

    Input:focus {
        border: tall #a65d40;
    }
    """

    TITLE = "Infralens Setup"

    def on_mount(self) -> None:
        self.push_screen(WelcomeScreen())

    def on_exit(self, result=None) -> None:
        if result == "launch":
            from infralens.app import InfralensApp
            app = InfralensApp(first_run=True)
            app.run()

"""HTMLReporter - Generate HTML reports from conversation events."""

import json
import webbrowser
from pathlib import Path
from typing import Any

from voiceground.events import VoicegroundEvent
from voiceground.reporters.base import BaseReporter


def _get_version() -> str:
    """Get the package version, avoiding circular imports."""
    try:
        from importlib.metadata import PackageNotFoundError, version

        return version("voiceground")
    except (PackageNotFoundError, Exception):
        return "0.0.0+dev"


class HTMLReporter(BaseReporter):
    """Reporter that records events and generates self-contained HTML reports.

    Collects all events during pipeline execution and generates an interactive
    HTML report when the pipeline ends. The report is named
    "voiceground_report_{conversation_id}.html".

    Args:
        output_dir: Directory to write output files. Defaults to "./reports".
        auto_open: Whether to open the HTML report in browser after generation.
    """

    def __init__(
        self,
        output_dir: str | Path = "./reports",
        auto_open: bool = False,
    ):
        self._output_dir = Path(output_dir)
        self._auto_open = auto_open
        self._events: list[VoicegroundEvent] = []
        self._finalized = False
        self._conversation_id: str | None = None

    async def on_start(self, conversation_id: str) -> None:
        """Set the conversation ID when the pipeline starts."""
        self._conversation_id = conversation_id

    async def on_event(self, event: VoicegroundEvent) -> None:
        """Record an event."""
        self._events.append(event)

    async def on_end(self) -> None:
        """Generate HTML report."""
        # Guard against multiple calls
        if self._finalized:
            return
        self._finalized = True

        self._output_dir.mkdir(parents=True, exist_ok=True)

        # Generate HTML report
        events_data = [event.to_dict() for event in self._events]
        html_path = self._generate_html_report(events_data)

        if self._auto_open and html_path:
            # Convert path to file:// URL format (works cross-platform)
            file_url = html_path.absolute().as_uri()
            webbrowser.open(file_url)

        # Reset events for potential reuse
        self._events = []

    def _generate_html_report(self, events_data: list[dict[str, Any]]) -> Path | None:
        """Generate an HTML report with embedded events data.

        Returns the path to the generated HTML file, or None if the
        bundled client is not available.
        """
        # Try to load bundled client template
        template_path = Path(__file__).parent.parent / "_static" / "index.html"

        if template_path.exists():
            with open(template_path) as f:
                template = f.read()

            # Inject events data, conversation_id, and version into the template
            events_json = json.dumps(events_data)
            conversation_id_json = (
                json.dumps(self._conversation_id) if self._conversation_id else "null"
            )
            version_json = json.dumps(_get_version())
            script_content = f"""<script>
window.__VOICEGROUND_EVENTS__ = {events_json};
window.__VOICEGROUND_CONVERSATION_ID__ = {conversation_id_json};
window.__VOICEGROUND_VERSION__ = {version_json};
</script>"""
            html_content = template.replace(
                "<!-- VOICEGROUND_EVENTS_PLACEHOLDER -->",
                script_content,
            )
        else:
            # Fallback: generate a simple HTML page
            events_json = json.dumps(events_data, indent=2)
            html_content = self._generate_fallback_html(events_json)

        # Generate filename with conversation_id
        if self._conversation_id:
            filename = f"voiceground_report_{self._conversation_id}.html"
        else:
            filename = "voiceground_report.html"

        html_path = self._output_dir / filename
        with open(html_path, "w") as f:
            f.write(html_content)

        return html_path

    def _generate_fallback_html(self, events_json: str) -> str:
        """Generate a simple fallback HTML report."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Voiceground Report</title>
    <style>
        :root {{
            --bg: #0a0a0a;
            --surface: #141414;
            --border: #262626;
            --text: #fafafa;
            --text-muted: #a1a1aa;
            --accent: #22c55e;
        }}
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
            background: var(--bg);
            color: var(--text);
            padding: 2rem;
            line-height: 1.6;
        }}
        h1 {{
            color: var(--accent);
            margin-bottom: 1rem;
            font-size: 1.5rem;
        }}
        .info {{
            color: var(--text-muted);
            margin-bottom: 2rem;
            font-size: 0.875rem;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: var(--surface);
            border-radius: 8px;
            overflow: hidden;
        }}
        th, td {{
            padding: 0.75rem 1rem;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }}
        th {{
            background: var(--border);
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.05em;
        }}
        tr:hover {{
            background: rgba(34, 197, 94, 0.05);
        }}
        .category {{
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
        }}
        .user_speak {{ background: #3b82f620; color: #60a5fa; }}
        .bot_speak {{ background: #22c55e20; color: #4ade80; }}
        .stt {{ background: #f59e0b20; color: #fbbf24; }}
        .llm {{ background: #a855f720; color: #c084fc; }}
        .tts {{ background: #ec489920; color: #f472b6; }}
        .type {{
            color: var(--text-muted);
            font-size: 0.875rem;
        }}
        .data {{
            font-size: 0.75rem;
            color: var(--text-muted);
            max-width: 300px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
    </style>
</head>
<body>
    <h1>Voiceground Report</h1>
    <p class="info">Conversation events captured by Voiceground observer</p>
    <table>
        <thead>
            <tr>
                <th>Timestamp</th>
                <th>Category</th>
                <th>Type</th>
                <th>Data</th>
            </tr>
        </thead>
        <tbody id="events-body">
        </tbody>
    </table>
    <script>
        const events = {events_json};
        const tbody = document.getElementById('events-body');
        events.forEach(event => {{
            const row = document.createElement('tr');
            const timestamp = new Date(event.timestamp * 1000).toISOString();
            row.innerHTML = `
                <td>${{timestamp}}</td>
                <td><span class="category ${{event.category}}">${{event.category}}</span></td>
                <td class="type">${{event.type}}</td>
                <td class="data">${{JSON.stringify(event.data)}}</td>
            `;
            tbody.appendChild(row);
        }});
    </script>
</body>
</html>
"""

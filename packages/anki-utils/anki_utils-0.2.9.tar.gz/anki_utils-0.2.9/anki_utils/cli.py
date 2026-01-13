"""Command-line interface for anki-utils."""

from __future__ import annotations

import argparse
import importlib.resources
import json
import sys
from pathlib import Path

ASSET_MAP = {
    "preview-template": "assets/bundled/preview-template.jsx",
    "theme-designer": "assets/bundled/theme-designer.jsx",
}

DOC_MAP = {
    "roadmap": "ROADMAP.md",
    "changelog": "CHANGELOG.md",
    "migrations": "MIGRATIONS.md",
    "skill-update-protocol": "SKILL_UPDATE_PROTOCOL.md",
}


def _load_asset(asset_name: str) -> str:
    asset_path = ASSET_MAP[asset_name]
    return importlib.resources.files("anki_utils").joinpath(asset_path).read_text(
        encoding="utf-8"
    )


def _load_doc(doc_name: str) -> str:
    doc_path = DOC_MAP[doc_name]
    return importlib.resources.files("anki_utils").joinpath(doc_path).read_text(
        encoding="utf-8"
    )


def _write_asset(asset_name: str, target: Path) -> None:
    content = _load_asset(asset_name)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def _export_apkg_command(args: argparse.Namespace) -> int:
    from . import exporter

    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        print(f"Error parsing JSON: {exc}", file=sys.stderr)
        return 1

    result = exporter.create_package(data, args.output, base_path=args.base_path)
    print(json.dumps(result, indent=2))
    return 0


def _themes_command(args: argparse.Namespace) -> int:
    from . import themes

    if args.list:
        print("\n".join(themes.THEMES))
        return 0

    if args.all_json:
        theme_payload = {
            name: themes.get_theme_sections(name) for name in themes.THEMES
        }
        print(json.dumps(theme_payload))
        return 0

    if args.get not in themes.THEMES:
        print(f"Unknown theme: {args.get}", file=sys.stderr)
        return 1

    print(themes.get_front_back_css(args.get))
    return 0


def _asset_command(args: argparse.Namespace) -> int:
    if args.output:
        _write_asset(args.asset_name, Path(args.output))
        print(args.output)
        return 0

    print(_load_asset(args.asset_name))
    return 0


def _occlusion_command(args: argparse.Namespace) -> int:
    from . import occlusion

    argv = [args.image_path]
    if args.grid:
        argv.append("--grid")
    if args.json:
        argv.append("--json")
    if args.output:
        argv.extend(["--output", args.output])
    if args.min_conf is not None:
        argv.extend(["--min-conf", str(args.min_conf)])
    if args.preview:
        argv.append("--preview")
    if args.grid_size is not None:
        argv.extend(["--grid-size", str(args.grid_size)])
    return occlusion.main(argv)


def _preprocess_test_data_command(args: argparse.Namespace) -> int:
    from . import dev_tools

    argv = [args.json_path]
    if args.assets_dir:
        argv.append(args.assets_dir)
    return dev_tools.main(argv)


def _markdown_to_html_roadmap(markdown: str) -> str:
    """Convert roadmap markdown to styled HTML for Claude web preview."""
    import html
    import re

    lines = markdown.split("\n")
    html_parts = []
    in_table = False
    table_rows = []

    def process_table():
        if len(table_rows) < 2:
            return ""
        headers = [c.strip() for c in table_rows[0].split("|")[1:-1]]
        rows_html = []
        for row in table_rows[2:]:  # Skip header and separator
            cells = [c.strip() for c in row.split("|")[1:-1]]
            cells_html = "".join(f"<td>{html.escape(c)}</td>" for c in cells)
            rows_html.append(f"<tr>{cells_html}</tr>")
        headers_html = "".join(f"<th>{html.escape(h)}</th>" for h in headers)
        return f"<table><thead><tr>{headers_html}</tr></thead><tbody>{''.join(rows_html)}</tbody></table>"

    for line in lines:
        # Table handling
        if line.startswith("|"):
            if not in_table:
                in_table = True
                table_rows = []
            table_rows.append(line)
            continue
        elif in_table:
            html_parts.append(process_table())
            table_rows = []
            in_table = False

        # Headers
        if line.startswith("# "):
            html_parts.append(f"<h1>{html.escape(line[2:])}</h1>")
        elif line.startswith("## "):
            html_parts.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.startswith("### "):
            html_parts.append(f"<h3>{html.escape(line[4:])}</h3>")
        elif line.startswith("> "):
            html_parts.append(f"<blockquote>{html.escape(line[2:])}</blockquote>")
        elif line.startswith("---"):
            html_parts.append("<hr>")
        elif line.startswith("- **"):
            # List item with bold
            match = re.match(r"- \*\*(.+?)\*\*: (.+)", line)
            if match:
                html_parts.append(f"<li><strong>{html.escape(match.group(1))}</strong>: {html.escape(match.group(2))}</li>")
            else:
                html_parts.append(f"<li>{html.escape(line[2:])}</li>")
        elif line.strip():
            html_parts.append(f"<p>{html.escape(line)}</p>")

    if in_table:
        html_parts.append(process_table())

    body = "\n".join(html_parts)
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>anki-utils Roadmap</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
h1 {{ color: #1a1a1a; border-bottom: 2px solid #3b82f6; padding-bottom: 10px; }}
h2 {{ color: #374151; margin-top: 30px; }}
h3 {{ color: #4b5563; margin-top: 20px; }}
table {{ width: 100%; border-collapse: collapse; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin: 15px 0; }}
th {{ background: #3b82f6; color: white; padding: 12px; text-align: left; }}
td {{ padding: 10px 12px; border-bottom: 1px solid #e5e7eb; }}
tr:hover {{ background: #f9fafb; }}
blockquote {{ background: #dbeafe; border-left: 4px solid #3b82f6; margin: 10px 0; padding: 10px 15px; }}
hr {{ border: none; border-top: 1px solid #d1d5db; margin: 30px 0; }}
li {{ margin: 5px 0; }}
</style>
</head>
<body>
{body}
</body>
</html>"""


def _roadmap_command(args: argparse.Namespace) -> int:
    # Print deprecation notice
    print("=" * 60)
    print("NOTICE: The roadmap command is deprecated.")
    print("All tasks are now tracked in GitHub Issues:")
    print("  https://github.com/Gilbetrar/anki-package/issues")
    print()
    print("Quick links:")
    print("  Ready tasks:     ...issues?q=label:ready")
    print("  Good first task: ...issues?q=label:good-first-task")
    print("  Phase 2:         ...issues?q=label:phase-2")
    print("=" * 60)
    print()

    content = _load_doc("roadmap")

    # Filter to section first if specified
    if args.section:
        lines = content.split("\n")
        in_section = False
        section_lines = []
        section_header = f"## {args.section}"
        for line in lines:
            if line.startswith("## "):
                if in_section:
                    break
                if line.lower().startswith(section_header.lower()):
                    in_section = True
            if in_section:
                section_lines.append(line)
        if section_lines:
            content = "\n".join(section_lines)
        else:
            print(f"Section '{args.section}' not found.", file=sys.stderr)
            return 1

    # Output as HTML or markdown
    if args.html:
        print(_markdown_to_html_roadmap(content))
    else:
        print(content)
    return 0


def _changelog_command(args: argparse.Namespace) -> int:
    content = _load_doc("changelog")
    if args.latest:
        # Print only the most recent version
        lines = content.split("\n")
        in_version = False
        version_lines = []
        for line in lines:
            if line.startswith("## ["):
                if in_version:
                    break
                in_version = True
            if in_version:
                version_lines.append(line)
        print("\n".join(version_lines))
    else:
        print(content)
    return 0


def _parse_migrations(content: str) -> list[dict]:
    """Parse MIGRATIONS.md into structured entries."""
    import re

    entries = []
    lines = content.split("\n")
    current_entry = None
    current_section = None
    section_lines = []

    def save_section():
        if current_entry and current_section and section_lines:
            text = "\n".join(section_lines).strip()
            if current_section == "what_changed":
                current_entry["changes"] = [
                    line[2:].strip() for line in section_lines if line.startswith("- ")
                ]
            elif current_section == "schema_changes":
                current_entry["schema_changes"] = text
            elif current_section == "skill_instructions":
                current_entry["skill_instructions"] = text

    for line in lines:
        # Version header: ## [0.2.1] - 2025-01-01
        version_match = re.match(r"^## \[(\d+\.\d+\.\d+)\] - (\d{4}-\d{2}-\d{2})", line)
        if version_match:
            save_section()
            if current_entry:
                entries.append(current_entry)
            current_entry = {
                "version": version_match.group(1),
                "date": version_match.group(2),
                "changes": [],
                "schema_changes": "",
                "skill_instructions": "",
            }
            current_section = None
            section_lines = []
            continue

        # Section headers
        if line.startswith("### What Changed"):
            save_section()
            current_section = "what_changed"
            section_lines = []
        elif line.startswith("### Schema Changes"):
            save_section()
            current_section = "schema_changes"
            section_lines = []
        elif line.startswith("### Skill Instructions"):
            save_section()
            current_section = "skill_instructions"
            section_lines = []
        elif line.startswith("## ") or line.startswith("# "):
            # New major section, stop parsing current entry
            save_section()
            if current_entry:
                entries.append(current_entry)
            current_entry = None
            current_section = None
        elif current_section:
            section_lines.append(line)

    save_section()
    if current_entry:
        entries.append(current_entry)

    return entries


def _compare_versions(v1: str, v2: str) -> int:
    """Compare semantic versions. Returns -1 if v1 < v2, 0 if equal, 1 if v1 > v2."""
    parts1 = [int(x) for x in v1.split(".")]
    parts2 = [int(x) for x in v2.split(".")]
    for p1, p2 in zip(parts1, parts2):
        if p1 < p2:
            return -1
        if p1 > p2:
            return 1
    return 0


def _migrations_command(args: argparse.Namespace) -> int:
    content = _load_doc("migrations")
    entries = _parse_migrations(content)

    # Filter by --since if provided
    if args.since:
        entries = [e for e in entries if _compare_versions(e["version"], args.since) > 0]

    # Output format
    if args.json:
        from . import __version__

        output = {
            "current_version": __version__,
            "since": args.since,
            "has_updates": len(entries) > 0,
            "entries": entries,
        }
        print(json.dumps(output, indent=2))
    else:
        if not entries:
            if args.since:
                print(f"No migrations since version {args.since}")
            else:
                print(content)
        else:
            for entry in entries:
                print(f"\n## [{entry['version']}] - {entry['date']}")
                if entry["changes"]:
                    print("\n### What Changed")
                    for change in entry["changes"]:
                        print(f"- {change}")
                if entry["skill_instructions"]:
                    print("\n### Skill Instructions")
                    print(entry["skill_instructions"])
    return 0


def _version_command(args: argparse.Namespace) -> int:
    from . import __version__

    if args.json:
        print(json.dumps({"version": __version__}))
    else:
        print(__version__)
    return 0


def _skill_update_protocol_command(args: argparse.Namespace) -> int:
    content = _load_doc("skill-update-protocol")
    print(content)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="anki-utils")
    subparsers = parser.add_subparsers(dest="command", required=True)

    export_parser = subparsers.add_parser(
        "export-apkg",
        help="Create an Anki .apkg file from JSON input.",
    )
    export_parser.add_argument(
        "--output",
        required=True,
        help="Path to write the .apkg file.",
    )
    export_parser.add_argument(
        "--base-path",
        help="Base directory to resolve relative media paths.",
    )
    export_parser.set_defaults(func=_export_apkg_command)

    themes_parser = subparsers.add_parser(
        "themes",
        help="List or fetch theme CSS definitions.",
    )
    themes_group = themes_parser.add_mutually_exclusive_group(required=True)
    themes_group.add_argument(
        "--list",
        action="store_true",
        help="List available themes.",
    )
    themes_group.add_argument(
        "--all-json",
        action="store_true",
        help="Print JSON containing all theme CSS sections.",
    )
    themes_group.add_argument(
        "--get",
        metavar="NAME",
        help="Print CSS for a theme.",
    )
    themes_parser.set_defaults(func=_themes_command)

    asset_parser = subparsers.add_parser(
        "asset",
        help="Print or copy bundled JSX assets.",
    )
    asset_parser.add_argument(
        "asset_name",
        choices=sorted(ASSET_MAP.keys()),
        help="Asset name to output.",
    )
    asset_parser.add_argument(
        "--output",
        help="Optional path to copy the asset into.",
    )
    asset_parser.set_defaults(func=_asset_command)

    occlusion_parser = subparsers.add_parser(
        "occlusion-detect",
        help="Detect occlusion regions in an image.",
    )
    occlusion_parser.add_argument("image_path", help="Path to the input image.")
    occlusion_parser.add_argument("--json", action="store_true", help="Output JSON only.")
    occlusion_parser.add_argument("--grid", action="store_true", help="Generate a grid overlay.")
    occlusion_parser.add_argument(
        "--output",
        "-o",
        help="Output directory (default: same as input).",
    )
    occlusion_parser.add_argument(
        "--min-conf",
        type=int,
        default=60,
        help="Minimum OCR confidence threshold 0-100.",
    )
    occlusion_parser.add_argument(
        "--preview",
        action="store_true",
        help="Generate preview image with detected regions highlighted.",
    )
    occlusion_parser.add_argument(
        "--grid-size",
        type=int,
        default=10,
        help="Grid size NxN.",
    )
    occlusion_parser.set_defaults(func=_occlusion_command)

    preprocess_parser = subparsers.add_parser(
        "preprocess-test-data",
        help="Convert image paths in JSON into base64 data URLs.",
    )
    preprocess_parser.add_argument("json_path", help="Path to the JSON file.")
    preprocess_parser.add_argument(
        "assets_dir",
        nargs="?",
        help="Base directory for resolving relative image paths.",
    )
    preprocess_parser.set_defaults(func=_preprocess_test_data_command)

    roadmap_parser = subparsers.add_parser(
        "roadmap",
        help="View the development roadmap.",
    )
    roadmap_parser.add_argument(
        "--section",
        help="Show only a specific section (e.g., 'Current Focus', 'Phase 1').",
    )
    roadmap_parser.add_argument(
        "--html",
        action="store_true",
        help="Output as styled HTML instead of markdown.",
    )
    roadmap_parser.set_defaults(func=_roadmap_command)

    changelog_parser = subparsers.add_parser(
        "changelog",
        help="View the version changelog.",
    )
    changelog_parser.add_argument(
        "--latest",
        action="store_true",
        help="Show only the most recent version.",
    )
    changelog_parser.set_defaults(func=_changelog_command)

    migrations_parser = subparsers.add_parser(
        "migrations",
        help="View migration instructions for consuming agents.",
    )
    migrations_parser.add_argument(
        "--since",
        metavar="VERSION",
        help="Show only migrations since this version (e.g., '0.2.0').",
    )
    migrations_parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON for programmatic parsing.",
    )
    migrations_parser.set_defaults(func=_migrations_command)

    version_parser = subparsers.add_parser(
        "version",
        help="Show the current package version.",
    )
    version_parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON.",
    )
    version_parser.set_defaults(func=_version_command)

    skill_protocol_parser = subparsers.add_parser(
        "skill-update-protocol",
        help="Show the skill update protocol with validation tests.",
    )
    skill_protocol_parser.set_defaults(func=_skill_update_protocol_command)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

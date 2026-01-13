"""CLI entry point for imc-prospector."""

import sys
from datetime import datetime
from importlib import metadata
from pathlib import Path
from typing import Annotated, Optional

from typer import Argument, Option, Typer

from imcprospector.checker import ProsperityChecker, Severity
from imcprospector.submit import submit

app = Typer(context_settings={"help_option_names": ["--help", "-h"]}, name="imc-prospector")


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        try:
            version = metadata.version("imc-prospector")
        except metadata.PackageNotFoundError:
            version = "dev"
        print(f"imc-prospector {version}")
        sys.exit(0)


@app.command()
def check(
    algorithm: Annotated[
        Path,
        Argument(
            help="Path to the Python file containing the algorithm to check.",
            show_default=False,
            exists=True,
            file_okay=True,
            dir_okay=False,
            resolve_path=True,
        ),
    ],
    config: Annotated[
        Optional[str],
        Option("--config", "-c", help="Path to YAML config file"),
    ] = None,
    strict: Annotated[
        bool,
        Option("--strict", help="Treat warnings as errors"),
    ] = False,
    json_output: Annotated[
        bool,
        Option("--json", help="Output JSON (no prompt)"),
    ] = False,
    no_info: Annotated[
        bool,
        Option("--no-info", help="Hide info messages"),
    ] = False,
    no_prompt: Annotated[
        bool,
        Option("--no-prompt", "-y", help="Don't prompt, just exit with code"),
    ] = False,
    dump_config: Annotated[
        bool,
        Option("--dump-config", help="Dump effective config and exit"),
    ] = False,
) -> None:
    """Check an IMC Prosperity algorithm for compliance."""
    import json

    from imcprospector.checker import load_config

    config_dict = load_config(config)

    if dump_config:
        try:
            import yaml as yaml_lib

            print(yaml_lib.dump(config_dict, default_flow_style=False))
        except ImportError:
            print(json.dumps(config_dict, indent=2))
        sys.exit(0)

    checker = ProsperityChecker(config=config_dict, strict=strict)
    result = checker.check_file(str(algorithm))

    if no_info:
        result.issues = [i for i in result.issues if i.severity != Severity.INFO]

    error_count = sum(1 for i in result.issues if i.severity == Severity.ERROR)
    warning_count = sum(1 for i in result.issues if i.severity == Severity.WARNING)

    if json_output:
        output = result.to_dict()
        output["error_count"] = error_count
        output["warning_count"] = warning_count
        print(json.dumps(output, indent=2))
        sys.exit(0 if result.valid else 1)

    # Pretty print output
    print(f"\n{'='*60}")
    print(f"  IMC Prosperity Checker: {algorithm.name}")
    print(f"{'='*60}\n")

    if not result.issues:
        print("✅ No issues found!\n")
    else:
        for severity in [Severity.ERROR, Severity.WARNING, Severity.INFO]:
            issues = [i for i in result.issues if i.severity == severity]
            if issues:
                print(f"\n{severity.value.upper()}S ({len(issues)}):")
                print("-" * 40)
                for issue in issues:
                    print(f"  {issue}\n")

    if config_dict.get("output", {}).get("show_requirements", True):
        print(f"{'='*60}")
        print("Official requirements:")
        print("  • Imports: pandas, numpy, statistics, math, typing, jsonpickle")
        print("  • Return: (result, conversions, traderData)")
        print(f"  • Timeout: <{config_dict.get('limits', {}).get('timeout_ms', 900)}ms")
        print(f"{'='*60}")

    if not result.issues:
        print("✅ PASSED")
        print(f"{'='*60}\n")
        sys.exit(0)

    if error_count > 0:
        print(f"❌ FAILED ({error_count} errors, {warning_count} warnings)")
    else:
        print(f"⚠️  WARNINGS ({warning_count} warnings)")
    print(f"{'='*60}\n")

    if no_prompt or not sys.stdin.isatty():
        sys.exit(1 if error_count > 0 else 0)

    response = input("Continue anyway? [y/N]: ").strip().lower()
    if response in ('y', 'yes'):
        print("Continuing...\n")
        sys.exit(0)
    else:
        print("Aborted.\n")
        sys.exit(1)


@app.command()
def submit_cmd(
    algorithm: Annotated[
        Path,
        Argument(
            help="Path to the Python file containing the algorithm to submit.",
            show_default=False,
            exists=True,
            file_okay=True,
            dir_okay=False,
            resolve_path=True,
        ),
    ],
    out: Annotated[
        Optional[str],
        Option("--out", "-o", help="File to save submission logs to (defaults to submissions/<timestamp>.log)."),
    ] = None,
    no_out: Annotated[
        bool,
        Option("--no-out", help="Don't download logs when done."),
    ] = False,
    no_check: Annotated[
        bool,
        Option("--no-check", help="Skip running the checker before submission."),
    ] = False,
    strict: Annotated[
        bool,
        Option("--strict", help="Treat checker warnings as errors."),
    ] = False,
    config: Annotated[
        Optional[str],
        Option("--config", "-c", help="Path to YAML config file for checker."),
    ] = None,
    force: Annotated[
        bool,
        Option("--force", help="Force submission even if checker finds errors (not recommended)."),
    ] = False,
    version: Annotated[
        bool,
        Option("--version", "-v", help="Show the program's version number and exit.", is_eager=True, callback=version_callback),
    ] = False,
) -> None:
    """Submit an IMC Prosperity algorithm."""
    if out is not None and no_out:
        print("--out and --no-out are mutually exclusive")
        sys.exit(1)

    if out is not None:
        output_file = Path(out).expanduser().resolve()
    elif no_out:
        output_file = None
    else:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_file = Path.cwd() / "submissions" / f"{timestamp}.log"

    submit(
        algorithm,
        output_file,
        run_checker=not no_check,
        checker_strict=strict,
        checker_config=config,
        force=force,
    )


def main() -> None:
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()


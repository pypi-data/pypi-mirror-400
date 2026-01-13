# python
from __future__ import annotations
import json
import pathlib
from typing import Optional

import typer

app = typer.Typer(name="payx-cli", help="CLI to automate engineer onboarding tasks")


@app.command("processor-setup")
def processor_setup(
        provider: str = typer.Option(..., help="Processor provider name, e.g. stripe"),
        env: str = typer.Option("staging", help="Target environment"),
        dry_run: bool = typer.Option(False, help="Show actions without applying"),
) -> None:
    """
    Setup a payment processor for an environment.
    This is a lightweight stub that should be replaced with real API calls.
    """
    typer.echo(f"Setting up processor '{provider}' in environment '{env}'")
    if dry_run:
        typer.echo("Dry run enabled — no changes will be made")
        raise typer.Exit()
    # TODO: integrate with provider SDKs / internal APIs
    typer.echo("Processor setup completed (stub)")


@app.command("transaction-test")
def transaction_test(
        merchant_id: str = typer.Option(..., help="Merchant identifier"),
        amount: float = typer.Option(..., help="Amount for test transaction"),
        currency: str = typer.Option("USD", help="Currency code"),
        capture: bool = typer.Option(True, help="Whether to capture the payment"),
) -> None:
    """
    Run a test transaction for a merchant (stub).
    """
    typer.echo(
        f"Running test transaction: merchant={merchant_id}, amount={amount} {currency}, capture={capture}"
    )
    # TODO: call payment gateway / sandbox endpoints
    typer.echo("Test transaction processed (stub)")


@app.command("merchant-migrate")
def merchant_migrate(
        merchant_id: str = typer.Option(..., help="Merchant identifier to migrate"),
        source: str = typer.Option(..., help="Source environment"),
        target: str = typer.Option(..., help="Target environment"),
        skip_validation: bool = typer.Option(False, help="Skip config validation step"),
) -> None:
    """
    Migrate merchant configuration from source to target environment.
    """
    typer.echo(f"Migrating merchant '{merchant_id}' from {source} -> {target}")
    if not skip_validation:
        typer.echo("Validating source configuration (stub)")
        # TODO: validate actual configurations
    # TODO: perform migration steps, handle secrets securely
    typer.echo("Migration completed (stub)")


def _load_config_file(path: pathlib.Path) -> Optional[dict]:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    suffix = path.suffix.lower()
    text = path.read_text()
    if suffix in {".json"}:
        return json.loads(text)
    if suffix in {".yaml", ".yml"}:
        try:
            import yaml  # type: ignore
        except Exception:
            raise RuntimeError(
                "PyYAML is required to parse YAML files. Install with 'pip install pyyaml'"
            )
        return yaml.safe_load(text)
    raise RuntimeError("Unsupported config file format; use .json, .yaml, or .yml")


@app.command("config-validate")
def config_validate(file: str = typer.Argument(..., help="Path to config file")) -> None:
    """
    Validate a configuration file (JSON or YAML).
    """
    path = pathlib.Path(file)
    try:
        cfg = _load_config_file(path)
    except Exception as exc:
        typer.secho(f"Validation failed: {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=2)
    typer.secho("Configuration parsed successfully", fg=typer.colors.GREEN)
    typer.echo(f"Top-level keys: {list(cfg.keys()) if isinstance(cfg, dict) else 'non-dict'}")


@app.command("config-sync")
def config_sync(
        source: str = typer.Argument(..., help="Source config file"),
        target: str = typer.Argument(..., help="Target config file"),
        overwrite: bool = typer.Option(False, help="Overwrite target if exists"),
) -> None:
    """
    Sync source config to target path. This is a simple file copy with basic checks.
    """
    src = pathlib.Path(source)
    tgt = pathlib.Path(target)
    if not src.exists():
        typer.secho(f"Source not found: {src}", fg=typer.colors.RED)
        raise typer.Exit(code=2)
    if tgt.exists() and not overwrite:
        typer.secho(f"Target exists: {tgt} (use --overwrite to replace)", fg=typer.colors.YELLOW)
        raise typer.Exit(code=3)
    tgt.parent.mkdir(parents=True, exist_ok=True)
    tgt.write_bytes(src.read_bytes())
    typer.secho(f"Synchronized {src} -> {tgt}", fg=typer.colors.GREEN)


def main() -> None:
    app()


if __name__ == "__main__":
    main()

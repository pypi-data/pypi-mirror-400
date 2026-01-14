import sys
import click
from .validators import VALIDATORS


def read_sa_json() -> str:
    """
    Read a GCP service-account JSON blob from stdin until **and including**
    the line whose *only* non-whitespace character is the closing brace '}'.

    • One ⏎ after the final '}' is sufficient.
    • EOF (Ctrl-D / Ctrl-Z⏎) still works too.
    """
    click.echo(
        "\nPaste the service-account JSON now."
        "\nFinish with a single Enter after the final '}', or press ⌃-D.\n"
    )
    lines: list[str] = []
    while True:
        try:
            line = sys.stdin.readline()
        except KeyboardInterrupt:
            click.echo("\nAborted.")
            sys.exit(1)

        if line == "":          # EOF  (Ctrl-D)
            break
        lines.append(line.rstrip("\n"))
        if line.strip() == "}":  # got the closing brace → stop
            break

    click.secho("✅ JSON captured — validating…\n", fg="cyan")
    return "\n".join(lines).strip()


@click.command()
def main() -> None:
    apps = sorted(VALIDATORS.keys())
    click.echo("Select a secret type to validate:")
    for i, a in enumerate(apps, 1):
        click.echo(f"  {i}. {a}")
    idx = click.prompt("Enter number", type=int)
    if not 1 <= idx <= len(apps):
        click.secho("Invalid selection.", fg="red")
        sys.exit(1)

    app = apps[idx - 1]
    validator = VALIDATORS[app]

    params: dict[str, str] = {}
    for p in validator.params:
        if p == "sa_json":
            params[p] = read_sa_json()
            continue
        hide = any(token in p for token in ("token", "key", "secret"))
        params[p] = click.prompt(p.replace("_", " "), hide_input=hide)

    rotated, msg = validator(**params)
    click.echo(msg)
    if rotated:
        click.secho("✅ Secret appears to be rotated / disabled.", fg="green")
    else:
        click.secho("⚠️  Secret is still live — rotate immediately!", fg="red")


if __name__ == "__main__":
    main()

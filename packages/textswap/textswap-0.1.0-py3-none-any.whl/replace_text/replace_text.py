"""Replace text in files based on dictionary mappings."""

import json
import os
from pathlib import Path

import click


@click.command(name="textswap")
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    default="config.json",
    help="Path to config file (default: config.json in current directory)",
)
@click.option(
    "--direction",
    "-d",
    type=click.IntRange(1, 2),
    prompt="Direction (1 for keys-to-values, 2 for values-to-keys)",
    help="1 for keys-to-values, 2 for values-to-keys",
)
@click.option(
    "--folder",
    "-f",
    type=click.Path(exists=True),
    prompt="Folder path",
    help="Path to folder containing files to process",
)
@click.option(
    "--dict-name",
    "-n",
    default=None,
    help="Dictionary name from config (auto-selects if only one)",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be replaced without making changes",
)
def replace_text(
    config: str, direction: int, folder: str, dict_name: str | None, dry_run: bool
) -> None:
    """Replace text in files based on dictionary mappings.

    Define replacement dictionaries in a JSON config file, then run this tool
    to bulk replace text across all files in a folder.
    """
    config_path = Path(config)
    if not config_path.exists():
        click.echo(f"Error: Config file not found: {config}", err=True)
        raise SystemExit(1)

    with open(config_path) as f:
        cfg = json.load(f)

    dictionaries = cfg.get("dictionaries", {})
    ignore_extensions = cfg.get("ignore_extensions", [])
    ignore_directories = cfg.get("ignore_directories", [])
    ignore_file_prefixes = cfg.get("ignore_file_prefixes", [])

    if not dictionaries:
        click.echo("Error: No dictionaries found in config", err=True)
        raise SystemExit(1)

    if dict_name is None:
        if len(dictionaries) == 1:
            dict_name = next(iter(dictionaries))
            click.echo(f"Using dictionary: {dict_name}")
        else:
            dict_name = click.prompt(
                "Dictionary name", type=click.Choice(list(dictionaries.keys()))
            )

    if dict_name not in dictionaries:
        click.echo(f"Error: Dictionary '{dict_name}' not found", err=True)
        raise SystemExit(1)

    replacement_dict: dict[str, str] = dictionaries[dict_name]

    if direction == 2:
        replacement_dict = {v: k for k, v in replacement_dict.items()}

    if dry_run:
        click.echo("Dry run mode - no files will be modified")

    files_processed = 0
    replacements_made = 0

    for root, dirs, files in os.walk(folder):
        dirs[:] = [d for d in dirs if d not in ignore_directories]

        for file in files:
            file_path = os.path.join(root, file)

            if any(file.endswith(ext) for ext in ignore_extensions):
                continue

            if any(file.startswith(prefix) for prefix in ignore_file_prefixes):
                continue

            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                new_content = content
                for key, value in replacement_dict.items():
                    new_content = new_content.replace(key, value)

                if new_content != content:
                    replacements_made += 1
                    if dry_run:
                        click.echo(f"Would modify: {file_path}")
                    else:
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(new_content)
                        click.echo(f"Modified: {file_path}")

                files_processed += 1

            except (UnicodeDecodeError, PermissionError):
                continue

    click.echo(f"\nProcessed {files_processed} files, {replacements_made} modified")


def main():
    """Entry point."""
    replace_text()


if __name__ == "__main__":
    main()

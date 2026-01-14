import shlex
import logging
import click
import shutil
import subprocess
import tempfile
from importlib import resources
from pathlib import Path

from cde_submit_migration.migration import get_logger


logger = get_logger(name="MigrationSubmitLogger", level=logging.WARNING)


def make_zip(destination: Path, source: Path) -> None:
    archive_name = shutil.make_archive(destination, "zip", source)
    logger.info(f"Created '{archive_name}' in local file system.")

    return Path(archive_name)


def format_bash_command(cmd: str) -> str:
    if len(cmd) < 60:
        return cmd

    tokens = shlex.split(cmd)
    if not tokens:
        return ""

    first_line = []
    i = 0

    while not tokens[i].startswith("-"):
        first_line.append(tokens[i])
        i += 1

    lines = [" ".join(first_line)]
    indent = "  "

    while i < len(tokens):
        current_token = tokens[i]

        if (
            current_token.startswith("-")
            and current_token != "--"
            and ((i + 1) < len(tokens))
            and not tokens[i + 1].startswith("-")
        ):
            # argument + value in the same line
            lines.append(f"{indent}{current_token} {tokens[i + 1]}")
            i += 2
        else:
            lines.append(f"{indent}{current_token}")
            i += 1

        if current_token == "--":
            indent = f"{indent}  "

    formatted = " \\\n".join(lines)

    return formatted


def run_cde_spark_submit(
    path: Path,
    db: str,
    verbose: bool,
    format_cmd: bool = False,
    profile: str | None = None,
) -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir_path = Path(tmp_dir)

        # find migration.py script path
        runner_script_path = str(
            resources.files("cde_submit_migration").joinpath("migration.py")
        )

        if path.is_file():
            migration_file_path = path
        elif path.is_dir():
            migration_file_path = make_zip(tmp_dir_path / path.name, path)
        else:
            raise ValueError("Path does not exist, or is not a file or directory")

        cmd = [
            "cde",
            "spark",
            "submit",
            "--files",
            str(migration_file_path),
        ]

        if profile:
            cmd.extend(["--config-profile", profile])

        cmd.extend(
            [
                runner_script_path,
                "--",
                "--path",
                migration_file_path.name,
                "--db",
                db,
            ]
        )
        logger.info("Running 'cde spark submit' in a subprocess.")

        if verbose:
            cmd_str = " ".join(cmd)
            if format_cmd:
                cmd_str = format_bash_command(cmd_str)

            click.secho("[Command]: ", fg="red", bold=True)
            click.secho(f"{cmd_str}\n", bold=True)

            if not click.confirm(
                "Do you want to proceed with running this command?", default=False
            ):
                logger.info("Command execution cancelled by user.")
                return

        subprocess.run(cmd, check=True)


@click.command(help="Submit SQL migration(s)")
@click.option(
    "--path",
    "path_",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to SQL migration file or folder containing multiple SQL migration files",
)
@click.option(
    "--db",
    required=True,
    help="Target database name where migration should take place",
)
@click.option(
    "--profile",
    default=None,
    help="CDE configuration profile name",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Shows 'cde spark submit' command and prompts for confirmation",
)
@click.option(
    "-f",
    "--format",
    "format_cmd",
    is_flag=True,
    help="Format 'cde spark submit' command if --verbose flag is used",
)
def main(
    path_: Path, db: str, profile: str | None, verbose: bool, format_cmd: bool
) -> None:
    run_cde_spark_submit(
        path=path_, db=db, verbose=verbose, format_cmd=format_cmd, profile=profile
    )


if __name__ == "__main__":
    main()

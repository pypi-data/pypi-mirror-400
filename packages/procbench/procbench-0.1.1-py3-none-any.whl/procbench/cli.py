# procmon/cli.py

import json
import time
from pathlib import Path
from typing import List

import click

from .testcase import TestCase
from .runner import ProcessRunner
from .monitor import ProcessMonitor
from .summary import summarize_samples
from .output import OutputWriter
from .errors import ProcMonError

try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli():
    """ProcBench - Process benchmarking and monitoring tool."""
    pass


@cli.command(name="run")
@click.argument(
    "testcases",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    nargs=-1,
    required=True,
)
@click.option(
    "-o",
    "--output",
    "output_path",
    type=click.Path(dir_okay=False, path_type=Path),
    required=True,
    help="Output JSON file",
)
@click.option(
    "--continue-on-error/--stop-on-error",
    default=True,
    help="Continue running remaining test cases if one fails",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Verbose logging to stdout",
)
def run_command(
    testcases: List[Path],
    output_path: Path,
    continue_on_error: bool,
    verbose: bool,
):
    """
    Run process monitoring test cases and write a single JSON output.
    """

    session_start = time.time()
    results = []

    writer = OutputWriter(schema_version="1.0")

    for tc_path in testcases:
        if verbose:
            click.echo(f"[+] Loading test case: {tc_path}")

        try:
            tc = TestCase.load_from_file(tc_path)

            if verbose:
                click.echo(f"[+] Running test case: {tc.id}")

            runner = ProcessRunner(
                command=tc.command,
                cwd=tc.cwd,
                env=tc.env,
            )
            runner.start()

            assert runner.pid is not None

            monitor = ProcessMonitor(
                pid=runner.pid,
                sampling_interval_ms=tc.sampling_interval_ms,
                timeout_sec=tc.timeout_sec,
                include_children=tc.include_children,
            )

            monitor.run()

            # If monitor timed out, ensure process is terminated
            if monitor.status == "timeout":
                if verbose:
                    click.echo(f"[!] Timeout reached, terminating pid {runner.pid}")
                runner.terminate()
            else:
                runner.wait(timeout=1)

            process_info = runner.info()

            summary = summarize_samples(
                samples=monitor.samples,
                start_time=monitor.start_time,
                end_time=monitor.end_time,
                exit_code=process_info.get("exit_code"),
                status=monitor.status,
            )

            result = writer.build_testcase_result(
                testcase_meta=tc.to_dict(),
                process_info=process_info,
                samples=monitor.samples,
                summary=summary,
            )

            results.append(result)

            if verbose:
                click.echo(f"[+] Test case {tc.id} completed with status={monitor.status}")

        except ProcMonError as e:
            click.echo(f"[ERROR] {e}", err=True)

            if not continue_on_error:
                break

        except Exception as e:
            click.echo(f"[FATAL] Unexpected error: {e}", err=True)
            if not continue_on_error:
                break

    session_end = time.time()

    writer.write(
        output_path=output_path,
        session_start=session_start,
        session_end=session_end,
        results=results,
    )

    if verbose:
        click.echo(f"[+] Results written to {output_path}")


@cli.group(name="export")
def export_group():
    """Export benchmark results to various formats."""
    pass


@export_group.command(name="html")
@click.argument(
    "input_json",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
@click.argument(
    "output_html",
    type=click.Path(dir_okay=False, path_type=Path),
)
def export_html(input_json: Path, output_html: Path):
    """
    Export benchmark results JSON to an HTML report.
    
    INPUT_JSON: Path to the benchmark results JSON file
    OUTPUT_HTML: Path to write the HTML report
    """
    try:
        # Read the JSON file
        with open(input_json, 'r') as f:
            json_content = f.read()
        
        # Validate that it's valid JSON
        json.loads(json_content)
        
        # Load the HTML template using importlib.resources
        template_package = files('procbench').joinpath('templates')
        template_file = template_package.joinpath('html_template.html')
        
        if hasattr(template_file, 'read_text'):
            # Python 3.9+
            template_content = template_file.read_text(encoding='utf-8')
        else:
            # Python 3.7-3.8
            with template_file.open('r', encoding='utf-8') as f:
                template_content = f.read()
        
        # Replace the placeholder with JSON content
        html_output = template_content.replace(
            '[[TEST_CASES_DATA_PLACEHOLDER]]',
            json_content
        )
        
        # Write the output HTML file
        with open(output_html, 'w', encoding='utf-8') as f:
            f.write(html_output)
        
        click.echo(f"[+] HTML report written to {output_html}")
        
    except json.JSONDecodeError as e:
        click.echo(f"[ERROR] Invalid JSON in input file: {e}", err=True)
        raise click.Abort()
    except FileNotFoundError as e:
        click.echo(f"[ERROR] File not found: {e}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"[ERROR] Failed to generate HTML report: {e}", err=True)
        raise click.Abort()


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()

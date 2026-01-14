import os
import argparse
import sys
from .logger import get_logger
from .runner import run_maestro_command
from .parser import parse_xml_report
from .sender import send_report_to_lark
from dotenv import load_dotenv


load_dotenv()
log = get_logger("main")


# helper utilities and extract it into private function
# by having this, it will removes duplicated os.path.exists
# and also isolate the core maestro logic instead of pile up together
# removed all the unnecessary logging when error, and replace with exception
def _resolve_report_path(command: str, report_path: str, no_run: bool) -> str:
    if no_run:
        log.info("--no-run flag is set, skipping Maestro tests")
        if not os.path.exists(report_path):
            raise FileNotFoundError(
                f"Maestro report file does not exists: {report_path}"
            )
        return report_path

    if not command:
        raise ValueError("No Maestro command provided, use `--command` or `--no-run`")

    log.info(f"Running Maestro command: {command}")
    generated_report = run_maestro_command(command=command)

    if not generated_report:
        raise RuntimeError("Failed to generate Maestro report")

    report_path = str(generated_report)
    if not os.path.exists(report_path):
        raise FileNotFoundError(f"Maestro report file does not exist: {report_path}")

    return report_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run Maestro tests with a custom reporter, parse the report and send it to Lark"
    )

    parser.add_argument("--command", "-c", type=str, help="Maestro command to run")
    parser.add_argument(
        "--report",
        "-r",
        type=str,
        default="report.xml",
        help="Path to Maestro report, by default it's `report.xml`",
    )
    parser.add_argument(
        "--webhook",
        "-w",
        type=str,
        help="Specify a webhook URL to send the report to Lark",
    )
    parser.add_argument(
        "--no-run",
        "-n",
        action="store_true",
        help="No need to run Maestro tests, just parse the report",
    )
    parser.add_argument(
        "--title",
        "-t",
        type=str,
        help="Set a custom title for the interactive card Lark message",
    )
    parser.add_argument(
        "--color",
        "-ct",
        type=str,
        help="Set a custom color template for the interactive card Lark message",
    )

    args = parser.parse_args()
    report_path = args.report

    if not args.color:
        log.warning(
            "No color template provided, using default color template or you can set it with `--color` flag"
        )

    if not args.title:
        log.warning(
            "No title provided, using default title or you can set it with `--title` flag"
        )

    try:
        report_path = _resolve_report_path(
            command=args.command, report_path=args.report, no_run=args.no_run
        )
    except Exception as e:
        log.error(f"Caught exception error: {e}")
        sys.exit(1)

    log.info(f"Parsing Maestro report file: {report_path}")
    parsed_report = parse_xml_report(report_path)
    if parsed_report is None:
        log.error("Failed to parse Maestro report")
        sys.exit(1)

    webhook_url = args.webhook or os.getenv("LARK_URL")
    if not webhook_url:
        log.error(
            "No webhook URL provided, use `--webhook` or set LARK_URL environment variable"
        )
        sys.exit(1)

    log.info("Sending Maestro report to Lark...")
    send_report_to_lark(
        parsed_report,
        title=args.title or "Maestro Testing Report",
        color_template=args.color or "Green",
        webhook_url=webhook_url,
    )
    log.info("Maestro report sent successfully")


if __name__ == "__main__":
    main()

import argparse
import json
import subprocess
from pathlib import Path

CONFIG_DIR = Path.home() / ".redirect-compute"
CONFIG_PATH = CONFIG_DIR / "config.json"
DEFAULT_CONFIG = {
    "provider": None,
    "remoteScratchDir": "~/redirect-compute/scratch",
    "transport": "ssh",
}

JOBS = {
    "demucs-vocals": {
        "description": "Separate vocals using Demucs htdemucs_ft",
        "command": "source ~/demucs-env/bin/activate && export PYTORCH_ENABLE_MPS_FALLBACK=1 && caffeinate -i demucs --two-stems=vocals -d mps -n htdemucs_ft {input} -o {output}",
    }
}


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return DEFAULT_CONFIG.copy()
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return {**DEFAULT_CONFIG, **data}


def save_config(config: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
        f.write("\n")


def cmd_config(args: argparse.Namespace) -> int:
    config = load_config()

    if args.config_command == "set-provider":
        config["provider"] = args.ssh_host_alias
        save_config(config)
        print(f"Provider set to: {args.ssh_host_alias}")
        return 0

    if args.config_command == "get-provider":
        provider = config.get("provider")
        if not provider:
            print("No provider configured")
            return 1
        print(provider)
        return 0

    raise ValueError(f"Unknown config command: {args.config_command}")


def cmd_provider(args: argparse.Namespace) -> int:
    config = load_config()
    provider = config.get("provider")

    if args.provider_command == "status":
        if not provider:
            print("No provider configured")
            print("Run: redirect-compute config set-provider <ssh-host-alias>")
            return 1

        command = ["ssh", provider, "echo redirect-compute-ok"]
        result = subprocess.run(command, text=True, capture_output=True)
        if result.returncode == 0 and "redirect-compute-ok" in result.stdout:
            print(f"Provider reachable: {provider}")
            return 0

        print(f"Provider unreachable: {provider}")
        print(f"Command failed: {' '.join(command)}")
        if result.stderr:
            print(result.stderr.strip())
        return result.returncode or 1

    raise ValueError(f"Unknown provider command: {args.provider_command}")


def cmd_worker(args: argparse.Namespace) -> int:
    if args.worker_command == "list":
        for name, job in JOBS.items():
            print(f"{name}: {job['description']}")
        return 0

    if args.worker_command == "run":
        job = JOBS.get(args.job_name)
        if not job:
            print(f"Unknown job: {args.job_name}")
            print("Available jobs:")
            for name in JOBS:
                print(f"  {name}")
            return 1

        input_path = Path(args.input_path).expanduser()
        output_dir = Path(args.output_dir).expanduser()
        if not input_path.exists():
            print(f"Input not found: {input_path}")
            return 1
        output_dir.mkdir(parents=True, exist_ok=True)

        command = job["command"].format(input=str(input_path), output=str(output_dir))
        print(f"Running job: {args.job_name}")
        result = subprocess.run(["bash", "-lc", command])
        return result.returncode

    raise ValueError(f"Unknown worker command: {args.worker_command}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="redirect-compute")
    subparsers = parser.add_subparsers(dest="command", required=True)

    config_parser = subparsers.add_parser("config", help="Manage local config")
    config_subparsers = config_parser.add_subparsers(dest="config_command", required=True)

    set_provider = config_subparsers.add_parser("set-provider", help="Set SSH provider alias")
    set_provider.add_argument("ssh_host_alias")

    config_subparsers.add_parser("get-provider", help="Print configured SSH provider alias")

    provider_parser = subparsers.add_parser("provider", help="Check provider connectivity")
    provider_subparsers = provider_parser.add_subparsers(dest="provider_command", required=True)
    provider_subparsers.add_parser("status", help="Check configured provider over SSH")

    worker_parser = subparsers.add_parser("worker", help="Run local worker jobs")
    worker_subparsers = worker_parser.add_subparsers(dest="worker_command", required=True)
    worker_subparsers.add_parser("list", help="List available worker jobs")

    worker_run = worker_subparsers.add_parser("run", help="Run a worker job locally")
    worker_run.add_argument("job_name")
    worker_run.add_argument("input_path")
    worker_run.add_argument("output_dir")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "config":
        return cmd_config(args)
    if args.command == "provider":
        return cmd_provider(args)
    if args.command == "worker":
        return cmd_worker(args)

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

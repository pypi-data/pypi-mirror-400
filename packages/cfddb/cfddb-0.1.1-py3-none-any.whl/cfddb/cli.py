import argparse
from pathlib import Path

from rich.console import Console
from rich.prompt import Confirm

from cfddb.dynamodb.client import DynamoClient
from cfddb.engine.executor import Executor
from cfddb.engine.plan_output import write_json_plan
from cfddb.engine.planner import Planner
from cfddb.engine.state import LocalState

console = Console()


def parse_parameters(param_list):
    """
    Parses ['Key=Value', 'Env=prod'] into {'Key': 'Value', 'Env': 'prod'}
    """
    if not param_list:
        return {}
    params = {}
    for item in param_list:
        if "=" not in item:
            raise ValueError(f"Invalid parameter format '{item}'. Use Key=Value.")
        key, value = item.split("=", 1)
        params[key.strip()] = value.strip()
    return params


def main():
    parser = argparse.ArgumentParser("cfddb")

    parser.add_argument("--template", required=True)
    parser.add_argument(
        "--parameters",
        action="append",
        help="CloudFormation parameter overrides in Key=Value format",
        default=[],
    )

    parser.add_argument("--endpoint", default="http://localhost:8000")
    parser.add_argument("--region", default="eu-central-1")
    parser.add_argument("--aws_access_key_id", default="local")
    parser.add_argument("--aws_secret_access_key", default="local")

    parser.add_argument("--plan", action="store_true")
    parser.add_argument("--plan-json", nargs="?", const=True)
    parser.add_argument("--force-unlock", action="store_true")
    parser.add_argument(
        "--prune",
        action="store_true",
        help="Delete GSIs found in DB but missing from template",
    )

    args = parser.parse_args()
    parameter_overrides = parse_parameters(args.parameters)

    state = LocalState()
    if args.force_unlock:
        state.release_lock()
    state.acquire_lock()

    try:
        dynamodb = DynamoClient(
            endpoint=args.endpoint,
            region=args.region,
            aws_access_key_id=args.aws_access_key_id,
            aws_secret_access_key=args.aws_secret_access_key,
        )
        planner = Planner(
            template=Path(args.template),
            parameter_overrides=parameter_overrides,
            dynamodb_client=dynamodb,
            prune=args.prune,
        )

        plan = planner.create_plan()
        plan.print_plan()
        if args.plan_json:
            write_json_plan(
                plan,
                None if args.plan_json is True else args.plan_json,
            )
            return

        if args.plan:
            return

        if not plan.actions:
            return

        console.print()
        if not Confirm.ask("[bold]Do you want to apply these changes?[/bold]"):
            console.print("[red]Aborted.[/red]")
            return

        executor = Executor(dynamodb)
        executor.apply(plan)

        state.save_metadata(
            {
                "last_apply_env": args.parameters,
                "template": str(args.template),
            }
        )

    except Exception:
        console.print("[red]ERROR[/red]")
        raise
    finally:
        state.release_lock()


if __name__ == "__main__":
    main()

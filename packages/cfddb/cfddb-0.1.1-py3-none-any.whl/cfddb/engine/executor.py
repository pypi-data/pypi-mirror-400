from botocore.exceptions import ClientError
from rich.console import Console
from rich.progress import Progress

from cfddb.cfn.constants import ActionType

console = Console()


class Executor:
    def __init__(self, dynamodb_client):
        self.ddb = dynamodb_client

    def apply(self, plan):
        if not plan.actions:
            console.print("[green]No changes to apply[/green]")
            return

        with Progress() as progress:
            task = progress.add_task("[cyan]Applying DynamoDB changes.", total=len(plan.actions))

            for action in plan.actions:
                progress.advance(task)

                try:
                    if action.type == ActionType.CREATE:
                        self._create_table(action)

                    elif action.type == ActionType.ADD_GSI:
                        self._add_gsi(action)

                    elif action.type == ActionType.DELETE_GSI:
                        self._delete_gsi(action)

                    elif action.type == ActionType.UPDATE_TTL:
                        self._update_ttl(action)

                    elif action.type == ActionType.UPDATE_PITR:
                        self._update_pitr(action)

                    elif action.type == ActionType.WARN_GSI_REMOVAL:
                        console.print(
                            f"[yellow]Warning:[/yellow] GSI removal detected on {action.spec.TableName}: {action.payload}"
                        )

                    elif action.type == ActionType.ERROR_GSI_MODIFIED:
                        raise RuntimeError(
                            f"GSI '{action.payload['index']}' modified on table {action.spec.TableName}. "
                            "DynamoDB does not support GSI modification."
                        )
                    else:
                        raise RuntimeError(f"Unknown action type: {action.type}")

                except ClientError:
                    console.print(f"[red]Failed to execute action on {action.spec.TableName}[/red]")
                    raise

    def _create_table(self, action):
        spec = action.spec
        console.print(f"[green]+ Creating table[/green] {spec.TableName}")

        try:
            self.ddb.create(spec)
        except ClientError as e:
            if "Key Schema too big" in str(e):
                console.print(
                    "[yellow]! Detected 'Key Schema too big'. Filtering multi-attribute GSIs.[/yellow]"
                )

                valid_gsis = []
                filtered = False

                for gsi in spec.GlobalSecondaryIndexes:
                    if len(gsi.KeySchema) > 2:
                        console.print(f"[red]  - Dropping GSI '{gsi.IndexName}'[/red]")
                        filtered = True
                    else:
                        valid_gsis.append(gsi)

                if filtered:
                    # Update the GSIs list
                    spec.GlobalSecondaryIndexes = valid_gsis

                    # Clean up AttributeDefinitions (remove unused keys)
                    used_attrs = set()
                    for k in spec.KeySchema:
                        used_attrs.add(k.AttributeName)
                    for gsi in valid_gsis:
                        for k in gsi.KeySchema:
                            used_attrs.add(k.AttributeName)

                    spec.AttributeDefinitions = [
                        attr
                        for attr in spec.AttributeDefinitions
                        if attr.AttributeName in used_attrs
                    ]

                    # Handle an empty GSI list case implicitly handled by create_payload()
                    # if the list becomes empty.
                    console.print("[cyan]! Retrying table creation.[/cyan]")
                    self.ddb.create(spec)
                else:
                    raise
            else:
                raise

        console.print("[dim]  ... waiting for table to become ACTIVE[/dim]")
        waiter = self.ddb.ddb.get_waiter("table_exists")
        waiter.wait(TableName=spec.TableName, WaiterConfig={"Delay": 1, "MaxAttempts": 20})

    def _add_gsi(self, action):
        spec = action.spec
        gsi = action.payload
        console.print(f"[cyan]+ Adding GSI[/cyan] {gsi.IndexName} on {spec.TableName}")
        target_definitions = spec.gsi_attribute_definitions(gsi)
        required_keys = {k.AttributeName for k in gsi.KeySchema}
        found_keys = {a["AttributeName"] for a in target_definitions}
        if not required_keys.issubset(found_keys):
            console.print(
                f"[red]! Skipping GSI {gsi.IndexName}: Missing AttributeDefinitions[/red]"
            )
            return
        try:
            self.ddb.add_gsis(
                table_name=spec.TableName,
                attrs=target_definitions,
                updates=[spec.create_gsi_update(gsi)],
            )
            console.print(f"[dim]  ... waiting for GSI '{gsi.IndexName}' to become ACTIVE[/dim]")
            self.ddb.wait_for_gsi_active(spec.TableName, gsi.IndexName)
        except ClientError as e:
            if "Key Schema too big" in str(e):
                console.print(
                    f"[yellow]Skipping GSI {gsi.IndexName} (Multi-attribute key)[/yellow]"
                )
            else:
                raise

    def _delete_gsi(self, action):
        spec = action.spec
        gsi_name = action.payload
        console.print(f"[red]- Pruning GSI[/red] {gsi_name} from {spec.TableName}")
        self.ddb.add_gsis(
            table_name=spec.TableName,
            attrs=[],
            updates=[spec.delete_gsi_update(gsi_name)],
        )
        console.print("[dim]  ... waiting for GSI deletion to finish[/dim]")
        waiter = self.ddb.ddb.get_waiter("table_exists")
        waiter.wait(TableName=spec.TableName, WaiterConfig={"Delay": 2, "MaxAttempts": 60})

    def _update_ttl(self, action):
        spec = action.spec
        ttl = action.payload

        console.print(f"[cyan]~ Updating TTL[/cyan] on {spec.TableName}")

        self.ddb.update_ttl(
            table_name=spec.TableName,
            enabled=ttl.Enabled,
            attr=ttl.AttributeName,
        )

    def _update_pitr(self, action):
        spec = action.spec
        enabled = action.payload

        state_str = "Enabling" if enabled else "Disabling"
        console.print(f"[cyan]~ {state_str} PITR[/cyan] on {spec.TableName}")

        self.ddb.update_pitr(spec.TableName, enabled)

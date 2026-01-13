from cfddb.cfn.constants import ActionType
from cfddb.cfn.parser import CFNParser
from cfddb.dynamodb.tables import DynamoTableSpec
from cfddb.engine.diff import symbol


class PlanAction:
    def __init__(self, type_, spec, payload=None):
        self.type = type_
        self.spec = spec
        self.payload = payload


class Plan:
    def __init__(self):
        self.actions = []

    def serialize(self):
        return [
            {"type": action.type, "table": action.spec.TableName, "payload": action.payload}
            for action in self.actions
        ]

    def print_plan(self):
        from rich.console import Console
        from rich.table import Table

        table = Table(title="Plan")
        table.add_column("Diff")
        table.add_column("Action")
        table.add_column("Table")
        table.add_column("Details")

        for action in self.actions:
            table.add_row(
                symbol(action.type),
                action.type,
                action.spec.TableName,
                str(action.payload) if action.payload else "",
            )

        Console().print(table)


class Planner:
    def __init__(self, template, parameter_overrides, dynamodb_client, prune=False):
        self.parser = CFNParser(template, parameter_overrides)
        self.client = dynamodb_client
        self.prune = prune

    def create_plan(self):
        resources = self.parser.parse()
        existing = self.client.list_tables()
        plan = Plan()

        for r in resources.values():
            if r["Type"] != "AWS::DynamoDB::Table":
                continue

            spec = DynamoTableSpec.from_cfn(r["Properties"])
            actual = existing.get(spec.TableName)

            if not actual:
                plan.actions.append(PlanAction(ActionType.CREATE, spec))
                # Schedule TTL update for new tables immediately
                # because CreateTable API doesn't support setting TTL.
                if spec.TimeToLiveSpecification:
                    plan.actions.append(
                        PlanAction(ActionType.UPDATE_TTL, spec, spec.TimeToLiveSpecification)
                    )
                continue

            actual_gsis = {g["IndexName"] for g in actual.get("GlobalSecondaryIndexes", [])}

            desired_gsis = {g.IndexName for g in spec.GlobalSecondaryIndexes}

            for g in spec.GlobalSecondaryIndexes:
                if g.IndexName not in actual_gsis:
                    plan.actions.append(PlanAction(ActionType.ADD_GSI, spec, g))

            removed = actual_gsis - desired_gsis
            if removed:
                plan.actions.append(PlanAction(ActionType.WARN_GSI_REMOVAL, spec, list(removed)))

            if spec.TimeToLiveSpecification:
                ttl_resp = self.client.describe_ttl(spec.TableName)
                ttl_desc = ttl_resp.get("TimeToLiveDescription", {})
                is_enabled = ttl_desc.get("TimeToLiveStatus") in ["ENABLED", "ENABLING"]
                current_attr = ttl_desc.get("AttributeName")

                desired_enabled = spec.TimeToLiveSpecification.Enabled
                desired_attr = spec.TimeToLiveSpecification.AttributeName

                if (is_enabled != desired_enabled) or (is_enabled and current_attr != desired_attr):
                    plan.actions.append(
                        PlanAction(ActionType.UPDATE_TTL, spec, spec.TimeToLiveSpecification)
                    )

            removed_names = actual_gsis - desired_gsis
            if removed_names:
                if self.prune:
                    for gsi_name in removed_names:
                        plan.actions.append(PlanAction(ActionType.DELETE_GSI, spec, gsi_name))
                else:
                    plan.actions.append(
                        PlanAction(ActionType.WARN_GSI_REMOVAL, spec, list(removed_names))
                    )
            desired_pitr = getattr(spec, "PointInTimeRecoverySpecification", None)

            if desired_pitr:
                pitr_resp = self.client.describe_pitr(spec.TableName)
                if pitr_resp:
                    current_desc = pitr_resp.get("ContinuousBackupsDescription", {}).get(
                        "PointInTimeRecoveryDescription", {}
                    )

                    current_status = current_desc.get("PointInTimeRecoveryStatus", "DISABLED")

                    is_enabled = current_status == "ENABLED"
                    desired_enabled = desired_pitr.PointInTimeRecoveryEnabled

                    if is_enabled != desired_enabled:
                        plan.actions.append(
                            PlanAction(ActionType.UPDATE_PITR, spec, desired_enabled)
                        )
        return plan

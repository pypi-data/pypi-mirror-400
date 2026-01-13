import re

from cfddb.cfn.constants import CloudFormationToken


def resolve(value, parameters, conditions=None):
    """Recursively resolve CloudFormation intrinsics."""
    if conditions is None:
        conditions = {}

    if isinstance(value, dict):
        if CloudFormationToken.REF in value:
            return parameters.get(value[CloudFormationToken.REF], value[CloudFormationToken.REF])

        if CloudFormationToken.SUB in value:
            # Handle both !Sub "String" and !Sub ["String", {Vars}]
            val = value[CloudFormationToken.SUB]
            if isinstance(val, list):
                template = val[0]
                local_vars = resolve(val[1], parameters, conditions)
                merged_params = parameters.copy()
                merged_params.update(local_vars)
                return _sub(template, merged_params)
            return _sub(val, parameters)

        if CloudFormationToken.IF in value:
            cond_name, true_val, false_val = value[CloudFormationToken.IF]
            # Look up the condition result
            is_true = conditions.get(cond_name, False)
            selected = true_val if is_true else false_val
            return resolve(selected, parameters, conditions)

        if CloudFormationToken.JOIN in value:
            delimiter, values = value[CloudFormationToken.JOIN]
            resolved_list = resolve(values, parameters, conditions)
            return delimiter.join(str(v) for v in resolved_list)

        if CloudFormationToken.SPLIT in value:
            delimiter, string_val = value[CloudFormationToken.SPLIT]
            resolved_str = resolve(string_val, parameters, conditions)
            return resolved_str.split(delimiter)

        if CloudFormationToken.SELECT in value:
            index, list_val = value[CloudFormationToken.SELECT]
            resolved_list = resolve(list_val, parameters, conditions)
            try:
                return resolved_list[int(index)]
            except (IndexError, ValueError):
                return ""

        if CloudFormationToken.GET_ATT in value:
            resource, attr = value[CloudFormationToken.GET_ATT]
            # Since we are planning before creating, we can't get real ARNs.
            # We return a deterministic mock to satisfy string requirements (e.g. for SSM).
            if attr == "StreamArn":
                return f"arn:aws:dynamodb:local:000000000000:table/{resource}/stream/2026-01-01T00:00:00.000"
            return f"MOCK_ATTR_{resource}_{attr}"

        # Recursively resolve dictionary values
        return {k: resolve(v, parameters, conditions) for k, v in value.items()}

    if isinstance(value, list):
        return [resolve(v, parameters, conditions) for v in value]

    return value


def _sub(template: str, parameters: dict) -> str:
    """Interpolate ${Variable} in strings."""
    if not isinstance(template, str):
        return template

    return re.sub(
        r"\$\{([^}]+)}",
        lambda m: str(parameters.get(m.group(1), m.group(0))),
        template,
    )

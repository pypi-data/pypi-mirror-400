from typing import Any

from cfddb.cfn.constants import CloudFormationToken


def evaluate(conditions, parameters):
    """Evaluate all CFN conditions based on parameters."""
    return {name: _eval(expr, parameters) for name, expr in conditions.items()}


def _eval(expr: Any, parameters: dict[str, Any]) -> Any:
    """Recursively evaluate a CFN condition expression."""
    if isinstance(expr, dict):
        if CloudFormationToken.EQUALS in expr:
            first, second = expr[CloudFormationToken.EQUALS]
            return _eval(first, parameters) == _eval(second, parameters)

        if CloudFormationToken.OR in expr:
            return any(_eval(e, parameters) for e in expr[CloudFormationToken.OR])

        if CloudFormationToken.AND in expr:
            return all(_eval(e, parameters) for e in expr[CloudFormationToken.AND])

        if CloudFormationToken.NOT in expr:
            # Fn::Not expects a list with a single element
            [e] = expr[CloudFormationToken.NOT]
            return not _eval(e, parameters)

        if CloudFormationToken.REF in expr:
            return parameters.get(expr[CloudFormationToken.REF])
    return expr

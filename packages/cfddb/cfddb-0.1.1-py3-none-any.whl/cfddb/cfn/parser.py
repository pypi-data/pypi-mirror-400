import yaml

from cfddb.cfn.conditions import evaluate
from cfddb.cfn.constants import CloudFormationToken
from cfddb.cfn.intrinsics import resolve
from cfddb.cfn.ssm import SSM


class CFNYAMLLoader(yaml.SafeLoader):
    pass


def ref_constructor(loader, node):
    return {CloudFormationToken.REF: loader.construct_scalar(node)}


def equals_constructor(loader, node):
    return {CloudFormationToken.EQUALS: loader.construct_sequence(node)}


def or_constructor(loader, node):
    return {CloudFormationToken.OR: loader.construct_sequence(node)}


def and_constructor(loader, node):
    return {CloudFormationToken.AND: loader.construct_sequence(node)}


def if_constructor(loader, node):
    return {CloudFormationToken.IF: loader.construct_sequence(node)}


def sub_constructor(loader, node):
    if isinstance(node, yaml.ScalarNode):
        return {CloudFormationToken.SUB: loader.construct_scalar(node)}
    elif isinstance(node, yaml.SequenceNode):
        return {CloudFormationToken.SUB: loader.construct_sequence(node)}
    return None


def join_constructor(loader, node):
    return {CloudFormationToken.JOIN: loader.construct_sequence(node)}


def split_constructor(loader, node):
    return {CloudFormationToken.SPLIT: loader.construct_sequence(node)}


def getatt_constructor(loader, node):
    if isinstance(node, yaml.ScalarNode):
        return {CloudFormationToken.GET_ATT: node.value.split(".")}
    elif isinstance(node, yaml.SequenceNode):
        return {CloudFormationToken.GET_ATT: loader.construct_sequence(node)}
    return None


def select_constructor(loader, node):
    return {CloudFormationToken.SELECT: loader.construct_sequence(node)}


yaml.add_constructor("!Ref", ref_constructor, Loader=CFNYAMLLoader)
yaml.add_constructor("!Equals", equals_constructor, Loader=CFNYAMLLoader)
yaml.add_constructor("!Or", or_constructor, Loader=CFNYAMLLoader)
yaml.add_constructor("!And", and_constructor, Loader=CFNYAMLLoader)
yaml.add_constructor("!If", if_constructor, Loader=CFNYAMLLoader)
yaml.add_constructor("!Sub", sub_constructor, Loader=CFNYAMLLoader)
yaml.add_constructor("!Join", join_constructor, Loader=CFNYAMLLoader)
yaml.add_constructor("!Split", split_constructor, Loader=CFNYAMLLoader)
yaml.add_constructor("!GetAtt", getatt_constructor, Loader=CFNYAMLLoader)
yaml.add_constructor("!Select", select_constructor, Loader=CFNYAMLLoader)


class CFNParser:
    def __init__(self, template_path, parameter_overrides=None):
        self.template = yaml.load(template_path.read_text(), Loader=CFNYAMLLoader)
        self.parameter_overrides = parameter_overrides or {}

    def parse(self) -> dict:
        parameters = self._parameters()
        conditions = evaluate(self.template.get("Conditions", {}), parameters)

        resources = {}
        for name, resource in self.template.get("Resources", {}).items():
            # Pass conditions to resolve() so !If works inside properties
            resolved_props = resolve(resource, parameters, conditions)

            if resource["Type"] == "AWS::SSM::Parameter":
                SSM.put(
                    resolved_props["Properties"]["Name"],
                    resolved_props["Properties"]["Value"],
                )
                continue

            # Check if the resource is enabled via Conditions
            if conditions.get(name, True):
                resources[name] = resolved_props

        return resources

    def _parameters(self):
        params = {
            param_name: values.get("Default")
            for param_name, values in self.template.get("Parameters", {}).items()
        }
        params.update(self.parameter_overrides)
        params["AWS::AccountId"] = "000000000000"
        params["AWS::Region"] = "local"
        params["AWS::Partition"] = "aws"
        params["AWS::StackName"] = "local-stack"

        return params

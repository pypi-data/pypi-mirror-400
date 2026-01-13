import yaml

from cfddb.cfn.parser import CFNYAMLLoader, CloudFormationToken


def test_yaml_loader_ref():
    content = "Value: !Ref MyParam"
    data = yaml.load(content, Loader=CFNYAMLLoader)
    assert data["Value"] == {CloudFormationToken.REF: "MyParam"}


def test_yaml_loader_sub():
    content = "Value: !Sub '${A}-table'"
    data = yaml.load(content, Loader=CFNYAMLLoader)
    assert data["Value"] == {CloudFormationToken.SUB: "${A}-table"}


def test_yaml_loader_getatt_shorthand():
    content = "Value: !GetAtt Table.StreamArn"
    data = yaml.load(content, Loader=CFNYAMLLoader)
    assert data["Value"] == {CloudFormationToken.GET_ATT: ["Table", "StreamArn"]}

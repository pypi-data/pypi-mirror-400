from cfddb.cfn.constants import CloudFormationToken as Token
from cfddb.cfn.intrinsics import resolve


def test_resolve_ref():
    params = {"AppEnv": "sandbox"}
    obj = {Token.REF: "AppEnv"}
    assert resolve(obj, params) == "sandbox"


def test_resolve_sub_string():
    params = {"AppEnv": "prod"}
    obj = {Token.SUB: "table-${AppEnv}-v1"}
    assert resolve(obj, params) == "table-prod-v1"


def test_resolve_sub_list_vars():
    # !Sub ["Hello ${Name}", {Name: World}]
    obj = {Token.SUB: ["Hello ${Name}", {"Name": "World"}]}
    assert resolve(obj, {}) == "Hello World"


def test_resolve_if_true():
    conditions = {"IsProd": True}
    # !If [IsProd, "yes", "no"]
    obj = {Token.IF: ["IsProd", "yes", "no"]}
    assert resolve(obj, {}, conditions) == "yes"


def test_resolve_if_false():
    conditions = {"IsProd": False}
    obj = {Token.IF: ["IsProd", "yes", "no"]}
    assert resolve(obj, {}, conditions) == "no"


def test_resolve_split_select():
    # !Select [0, !Split ["-", "a-b-c"]]
    split_obj = {Token.SPLIT: ["-", "a-b-c"]}
    select_obj = {Token.SELECT: [0, split_obj]}

    assert resolve(select_obj, {}) == "a"


def test_resolve_getatt_stream_arn():
    # !GetAtt Table.StreamArn
    obj = {Token.GET_ATT: ["MyTable", "StreamArn"]}
    result = resolve(obj, {})
    assert "arn:aws:dynamodb:local" in result
    assert "/stream/" in result

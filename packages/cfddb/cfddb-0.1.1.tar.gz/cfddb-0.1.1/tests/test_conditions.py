from cfddb.cfn.conditions import evaluate


def test_condition_equals():
    conds = {"IsProd": {"Fn::Equals": [{"Ref": "Env"}, "prod"]}}
    assert evaluate(conds, {"Env": "prod"})["IsProd"] is True
    assert evaluate(conds, {"Env": "dev"})["IsProd"] is False


def test_condition_not():
    conds = {"IsNotProd": {"Fn::Not": [{"Fn::Equals": [{"Ref": "Env"}, "prod"]}]}}
    assert evaluate(conds, {"Env": "dev"})["IsNotProd"] is True


def test_condition_and_or():
    # (Env == prod) OR (Env == stage)
    conds = {
        "IsUpperEnv": {
            "Fn::Or": [
                {"Fn::Equals": [{"Ref": "Env"}, "prod"]},
                {"Fn::Equals": [{"Ref": "Env"}, "stage"]},
            ]
        }
    }
    assert evaluate(conds, {"Env": "prod"})["IsUpperEnv"] is True
    assert evaluate(conds, {"Env": "stage"})["IsUpperEnv"] is True
    assert evaluate(conds, {"Env": "dev"})["IsUpperEnv"] is False

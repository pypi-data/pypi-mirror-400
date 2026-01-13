from cfddb.cfn.parser import CFNParser
from cfddb.cfn.ssm import SSM

# A dummy CloudFormation template
SAMPLE_TEMPLATE = """
Parameters:
  Env:
    Type: String
    Default: local

Conditions:
  IsLocal: !Equals [!Ref Env, "local"]

Resources:
  # Should be included
  MyTable:
    Type: AWS::DynamoDB::Table
    Condition: IsLocal
    Properties:
      TableName: !Sub "app-${Env}-MyTable"

  # Should be filtered out
  ProdTable:
    Type: AWS::DynamoDB::Table
    Condition: IsProd  # Defined implicitly as False if missing?
                       # Actually, we need to define it or logic defaults to True/False depending on impl.
                       # Let's rely on the IsLocal condition for negative test.
  MyCompanyTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub "app-${Env}-MyCompanyTable"
      AttributeDefinitions:
        - AttributeName: PK
          AttributeType: S
        - AttributeName: SK
          AttributeType: S
        - AttributeName: GSI1PK
          AttributeType: S
        - AttributeName: GSI1SK
          AttributeType: S
      KeySchema:
        - AttributeName: PK
          KeyType: HASH
        - AttributeName: SK
          KeyType: RANGE
      GlobalSecondaryIndexes:
        - IndexName: GSI1
          KeySchema:
            - AttributeName: GSI1PK
              KeyType: HASH
            - AttributeName: GSI1SK
              KeyType: RANGE
          Projection:
            ProjectionType: INCLUDE
            NonKeyAttributes:
              - name
              - street
              - city
      DeletionProtectionEnabled: true
      PointInTimeRecoverySpecification:
        PointInTimeRecoveryEnabled: !If [EnablePITRCondition, true, false]

  # SSM Parameter logic check
  MyParam:
    Type: AWS::SSM::Parameter
    Properties:
      Name: /app/config
      Value: !Ref AWS::AccountId
"""


def test_parser_full_flow(tmp_path):
    t_file = tmp_path / "template.yaml"
    t_file.write_text(SAMPLE_TEMPLATE)

    parser = CFNParser(t_file, parameter_overrides={"AppEnv": "local"})
    resources = parser.parse()
    assert "MyTable" in resources
    # !Sub "app-${Env}-table" -> "app-local-Table"
    assert resources["MyTable"]["Properties"]["TableName"] == "app-local-MyTable"
    assert resources["MyCompanyTable"]["Properties"]["TableName"] == "app-local-MyCompanyTable"
    # We used !Ref AWS::AccountId in the SSM parameter
    # SSM parameters are stored in the SSM class, not returned as generic resources
    assert SSM.get("/app/config") == "000000000000"

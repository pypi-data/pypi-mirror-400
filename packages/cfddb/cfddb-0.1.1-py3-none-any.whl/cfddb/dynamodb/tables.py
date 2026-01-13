from pydantic import BaseModel, ConfigDict, Field


class AttributeDefinition(BaseModel):
    AttributeName: str
    AttributeType: str


class KeySchemaElement(BaseModel):
    AttributeName: str
    KeyType: str


class Projection(BaseModel):
    ProjectionType: str
    NonKeyAttributes: list[str] | None = None


class GlobalSecondaryIndex(BaseModel):
    IndexName: str
    KeySchema: list[KeySchemaElement]
    Projection: Projection


class StreamSpecModel(BaseModel):
    StreamViewType: str


class TTLSpecModel(BaseModel):
    AttributeName: str
    Enabled: bool


class DynamoTableSpec(BaseModel):
    # Ignore extra fields like 'Tags' or 'DeletionProtection'
    model_config = ConfigDict(extra="ignore")

    TableName: str
    AttributeDefinitions: list[AttributeDefinition]
    KeySchema: list[KeySchemaElement]
    GlobalSecondaryIndexes: list[GlobalSecondaryIndex] = Field(default_factory=list)

    TimeToLiveSpecification: TTLSpecModel | None = None
    StreamSpecification: StreamSpecModel | None = None

    BillingMode: str = "PAY_PER_REQUEST"

    @classmethod
    def from_cfn(cls, props):
        return cls(**props)

    def create_payload(self):
        # Start with a dict based on the model's data
        # exclude_none=True prevents sending nulls, but keeps empty lists
        base = self.model_dump(exclude_none=True, exclude={"TimeToLiveSpecification"})

        if "GlobalSecondaryIndexes" in base and not base["GlobalSecondaryIndexes"]:
            del base["GlobalSecondaryIndexes"]

        # Boto3 structure for StreamSpecification requires "StreamEnabled": True
        if self.StreamSpecification:
            base["StreamSpecification"] = {
                "StreamEnabled": True,
                "StreamViewType": self.StreamSpecification.StreamViewType,
            }

        return base

    def create_gsi_update(self, gsi: GlobalSecondaryIndex):
        gsi_dict = gsi.model_dump(exclude_none=True)
        return {"Create": gsi_dict}

    def delete_gsi_update(self, index_name):
        return {"Delete": {"IndexName": index_name}}

    def gsi_attribute_definitions(self, gsi: GlobalSecondaryIndex):
        target_attrs = {key.AttributeName for key in gsi.KeySchema}

        return [
            attr.model_dump()
            for attr in self.AttributeDefinitions
            if attr.AttributeName in target_attrs
        ]

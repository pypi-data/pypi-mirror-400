from enum import Enum


class CloudFormationToken(str, Enum):
    REF = "Ref"
    IF = "Fn::If"
    EQUALS = "Fn::Equals"
    OR = "Fn::Or"
    AND = "Fn::And"
    NOT = "Fn::Not"
    SUB = "Fn::Sub"
    JOIN = "Fn::Join"
    SPLIT = "Fn::Split"
    SELECT = "Fn::Select"
    GET_ATT = "Fn::GetAtt"


class ActionType(str, Enum):
    CREATE = "Create"
    ADD_GSI = "Add_GSI"
    DELETE_GSI = "Delete_GSI"
    UPDATE_TTL = "Update_TTL"
    UPDATE_PITR = "Update_PITR"
    WARN_GSI_REMOVAL = "Warn_GSI_Removal"
    ERROR_GSI_MODIFIED = "Error_GSI_Modified"

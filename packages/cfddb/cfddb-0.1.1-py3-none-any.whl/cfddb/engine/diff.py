from cfddb.cfn.constants import ActionType


def symbol(action):
    return {
        ActionType.CREATE: "+",
        ActionType.ADD_GSI: "~",
        ActionType.UPDATE_TTL: "~",
        ActionType.WARN_GSI_REMOVAL: "!",
    }.get(action, "?")

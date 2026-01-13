from enum import Enum


# Sorted by A..Z of Entity Type
class EntityName(Enum):
    AUTH_LOGIN = "auth"
    EVENT = "event"
    GENDER_DETECTION = "gender-detection"
    GROUP = "group"
    GROUP_PROFILE = "group-profile"
    LOGGER = "logger"
    MARKETPLACE_GOODS = "marketplace-goods"
    STORAGE = "storage"
    STORAGE_GRAPHQL = "storage-graphql"
    TIMELINE = "timeline"
    USER_REGISTRATION = "user-registration"
    SMARTLINK = "smartlink"
    DIALOG_WORKFLOW = "dialogWorkflow"

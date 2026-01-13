from enum import Enum


# Order by a..z of component name
# Should in in sync with https://github.com/circles-zone/url-remote-typescript-package/blob/dev/src/component-name.enum.ts
class ComponentName(Enum):
    AUTHENTICATION = "auth"  # Used by User Context both for login and validateJwt
    EVENT = "event"
    GENDER_DETECTION = "gender-detection"
    GROUP = "group"
    GROUP_PROFILE = "group-profile"
    LOGGER = "logger"
    MARKETPLACE_GOODS = "marketplace-goods"
    STORAGE = "storage"
    TIMELINE = "timeline"
    USER_REGISTRATION = "user-registration"
    SMARTLINK = "smartlink"
    DIALOG_WORKFLOW = "dialogWorkflow"

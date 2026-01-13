from enum import Enum


# TODO Based on https://restfulapi.net/resource-naming/ we should change all APIs to xxx-yy gradually


# Rename to HttpUrlActionName
class ActionName(Enum):
    # Authentication
    LOGIN = (
        "login"  # No need to authenticate before, we should add API KEY and impersonate
    )
    VALIDATE_USER_JWT = "validate-user-jwt"  # No need to authenticate before, we should add API KEY and impersonate

    # Event
    GET_EVENT_BY_ID = "getEventById"
    CREATE_EVENT = "createEvent"
    UPDATE_EVENT_BY_ID = "updateEventById"
    DELETE_EVENT_BY_ID = "deleteEventById"

    # Gender-detection
    ANALYZE_FACIAL_IMAGE = "analyzeFacialImage"
    # TODO Repace it with GENDER_DETECTION_API_VERSION_DICT[environment_name][ANALYZE_FACIAL_IMAGE]
    GENDER_DETECTION_API_VERSION = 1

    # Group
    GET_ALL_GROUPS = "getAllGroups"
    GET_GROUP_BY_NAME = "getGroupByName"
    GET_GROUP_BY_ID = "getGroupById"
    GET_GROUPS_BY_PROFILE_ID = "getGroupsByProfileId"
    CREATE_GROUP = "createGroup"
    UPDATE_GROUP = "updateGroup"
    DELETE_GROUP = "deleteGroupById"

    # Logger
    ADD_LOG = "add"

    # Storage
    PUT = "put"
    DOWNLOAD = "download"
    GRAPHQL = "graphql"

    # Timeline
    TIMELINE = "timeline"

    # User
    CREATE_USER = "createUser"  # No need to authenticate before, we should add API KEY and impersonate
    UPDATE_USER = "updateUser"

    # Group-profile
    CREATE_GROUP_PROFILE = "createGroupProfile"
    DELETE_GROUP_PROFILE = "deleteGroupProfile"
    GET_GROUP_PROFILE = "getGroupProfileByGroupIdProfileId"

    # SmartLink
    EXECUTE_SMARTLINK_BY_IDENTIFIER = "executeSmartlinkByIdentifier"  # Used when not logged-in user press on a SmartLink
    GET_SMARTLINK_DATA_BY_IDENTIFIER = (
        "getSmartlinkDataByIdentifier"  # Who is using it?
    )

    # Dialog-Workflow
    DIALOG_SEND_MESSAGE = "sendMessage"

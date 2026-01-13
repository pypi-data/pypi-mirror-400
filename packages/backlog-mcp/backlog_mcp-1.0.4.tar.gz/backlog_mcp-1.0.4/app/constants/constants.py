from enum import Enum

class BacklogApiError(Enum):
    InternalError = (1, "An error occurs in the API Server.")
    LicenceError = (2, "You call an API that is not available in your licence.")
    LicenceExpiredError = (3, "Space licence has expired.")
    AccessDeniedError = (4, "You access from an IP Address that is not allowed.")
    UnauthorizedOperationError = (5, "Your operation is denied.")
    NoResourceError = (6, "You access a resource that does not exist.")
    InvalidRequestError = (7, "You post a request with invalid parameters.")
    SpaceOverCapacityError = (8, "It exceeds the capacity of your space.")
    ResourceOverflowError = (9, "You call an API to add a resource when it exceeds a limit provided in the resource.")
    TooLargeFileError = (10, "The uploaded attachment is too large.")
    AuthenticationError = (11, "You are not registered on a target space.")
    RequiredMFAError = (12, "You are disabled Two-Factor Authentication in the space requiring 2-step verification.")
    TooManyRequestsError = (13, "Your API access exceeded the rate limit.")

    def __init__(self, code, description):
        self.code = code
        self.description = description

    @classmethod
    def get_description_by_code(cls, code, error_message=None, error_more_info=None):
        for error in cls:
            if error.code == code:
                description = error.description
                if error_message:
                    description += f" - {error_message}"
                if error_more_info:
                    description += f" ({error_more_info})"
                return description
        return "Unknown error code"

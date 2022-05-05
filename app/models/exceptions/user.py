class UserDoesNotExist(Exception):
    """Raised when the user id to share to does not exist"""

    code = 11
    http_code = 404

    def __init__(self, user_id: str) -> None:
        self.message = f"User: {user_id} is not found in user-management"
        super().__init__(self.message)


class UserAlreadyExists(Exception):
    """Raised when the user id to share to does not exist"""

    code = 11
    http_code = 409

    def __init__(self, user_id: str) -> None:
        self.message = f"User: {user_id} is already there"
        super().__init__(self.message)


class UserHasNoAccess(Exception):
    """Raised when the user does not have access to this endpoint"""

    code = 12
    http_code = 403

    def __init__(self, user_id: str, resource_id: str, action: str) -> None:
        self.message = (
            f"User: {user_id} has no access to {resource_id} with action {action}"
        )
        super().__init__(self.message)


class CannotConnectToUserManagement(Exception):
    """Raised when the user id to share to does not exist"""

    code = 13
    http_code = 404

    def __init__(self, url: str) -> None:
        self.message = f"User-management cannot be connected via {url}"
        super().__init__(self.message)

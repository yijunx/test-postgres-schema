from app.models.schemas.user import UserInJWT


class CasbinRuleDoesNotExist(Exception):
    """Raised when xxx happens, some more desc here"""

    code = 21
    http_code = 404

    def __init__(self, user_id: str, resource_id: str) -> None:
        self.message = f"User {user_id} does not have access for resource {resource_id}"
        super().__init__(self.message)


class CasbinRuleAlreadyExists(Exception):
    """Raised when xxx happens, some more desc here"""

    code = 21
    http_code = 409

    def __init__(self, user_id: str, resource_id: str) -> None:
        self.message = (
            f"User {user_id} already has access for resource or role {resource_id}"
        )
        super().__init__(self.message)


class CasbinNotAuthorised(Exception):
    """raised when an action is not authorised"""

    code = 21
    http_code = 403

    def __init__(self, actor: UserInJWT, resource_id: str, action: str) -> None:
        self.message = (
            f"user {actor.id} "
            f"in tenant {actor.tenant_id} "
            f"has no right to {action} "
            f" on resource {resource_id}"
        )

        super().__init__(self.message)
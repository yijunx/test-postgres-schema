class ItemDoesNotExist(Exception):
    """Raised when xxx happens, some more desc here. This will be shown in the openapi page as well!"""

    code = 1
    # http code will be reflected in the open api page also
    http_code = 404

    def __init__(self, item_id: str) -> None:
        self.message = f"Item {item_id} does not exist"
        super().__init__(self.message)


class ItemAlreadyExists(Exception):
    """Raised when xxx happens, some more desc here"""

    code = 2
    http_code = 409

    def __init__(self, item_name: str) -> None:
        self.message = f"Item {item_name} already exists"
        super().__init__(self.message)

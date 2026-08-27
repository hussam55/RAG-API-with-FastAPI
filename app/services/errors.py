class DocumentNotFoundError(Exception):
    pass


class DocumentNotReadyError(Exception):
    def __init__(self, status: str) -> None:
        super().__init__(f"Document is {status}")
        self.status = status


class ModelUnavailableError(Exception):
    pass


class DocumentDeletionError(Exception):
    pass

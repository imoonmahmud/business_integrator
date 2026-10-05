class UserNotFoundError(Exception):
    pass

class APIError(Exception):
    pass

class ResourceNotFoundError(APIError):
    pass

class InvalidJSONError(APIError):
    pass

class InvalidDataFormatError(APIError):
    pass 
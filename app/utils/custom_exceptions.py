class CreatePaymentException(Exception):
    pass


class UserNotFoundException(Exception):
    pass


class UserIsInActiveException(Exception):
    pass


class ImageTooSmallException(Exception):
    pass


class DataError(Exception):
    pass


class SendSmsError(Exception):
    pass


class SendEmailError(Exception):
    pass

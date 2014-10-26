class MajorDomoError(Exception):
    pass


class MaxRetryError(MajorDomoError):
    pass


class InvalidMessage(MajorDomoError):
    pass


class UnknownMagic(InvalidMessage):
    pass
class Len8Error(Exception):
    pass


class BadLines(Len8Error):
    pass

class InvalidFile(Len8Error):
    def __init__(self, arg):
        self.arg = arg

    def __str__(self):
        return "InvalidFile: '%s' is not a file, or is an invalid type." % self.arg

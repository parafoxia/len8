class Len8Error(Exception):
    pass


class BadLines(Len8Error):
    pass

class MissingArgument(Len8Error):
    def __init__(self, arg):
        self.arg = arg

    def __str__(self):
        return "%s option is missing a required argument." % self.arg

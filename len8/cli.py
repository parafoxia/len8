from .errors import BadLines
from .errors import MissingArgument

from len8 import check


HELP_MESSAGE = """USAGE: len8 [OPTIONS] path

OPTIONS:
    -f, --file:     Parse only a single file.
    -l, --length:   Increase acceptable line length to 99.
    -x, --exclude:  Exclude the following file(s) or dir(s).
"""


def cli(args):
    if not args or "-h" in args or "--help" in args:
        return print(HELP_MESSAGE)

    f_flag = ("-f", "--file")
    l_flag = ("-l", "--length")
    x_flag = ("-x", "--exclude")

    exclude = []
    excluding = False
    extend = False
    file = None
    filing = False
    path = None

    if args[0] not in (x_flag + l_flag + f_flag):
        path = args.pop(0)

        for arg in args:
            if arg in x_flag:
                excluding = True

            elif excluding and arg not in (l_flag + f_flag):
                exclude.append(arg)

            elif filing and arg not in (x_flag + l_flag):
                file = arg
                filing = False

            elif arg in l_flag:
                if excluding:
                    excluding = False

                extend = True

            elif arg in f_flag:
                if excluding:
                    excluding = False

                filing = True

        if filing:
            raise MissingArgument("file")


    elif args[0] in l_flag:
        args.pop(0)
        extend = True

        for arg in args:
            if arg in f_flag:
                pass

        # TODO continue this maze of logic.
        # jax is cute

    # if file:
    #     check(file, extend=extend)

    try:
        check(path, exclude=exclude, extend=extend)
    except BadLines as e:
        print(e)

import random
from random import randint as rint


def windows() -> str:
    etc = ["WOW64", "Win64; x64"]
    ver = ["10.0", f"6.{rint(0, 3)}"]
    main = "Windows NT "

    version = random.choice(ver)

    if version == "10.0" or rint(0, 1):
        version += f"; {random.choice(etc)}"

    return main + version


def macos() -> str:
    main = "Macintosh; Intel Mac OS X 10_"
    sub = str(rint(10, 14))
    sub += "_" + str(rint(1, (6 if sub != "14" else 2)))

    return main + sub


def linux() -> str:
    ver = ["x86_64", "i686", "i686 on x86_64"]
    main = "X11; Linux "

    return main + random.choice(ver)


def random_os() -> str:
    os_functions = [windows, macos, linux]
    return random.choice(os_functions)()

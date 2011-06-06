# -*- coding: utf-8 -*-


def setConsoleTitle ():
    try:
        sys.stdout.write("\x1b]2;Tyrs\x07")
    except:
        pass


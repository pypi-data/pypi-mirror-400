from sys import platform


def _get_text_font_unsafe():
    """ Returns None which should cause Pygame to fall to default """
    return None

def _get_symbolic_font_unsafe():
    """ Returns expected system font """
    match platform:
        case "linux":
            return "Noto Color Emojis" # TODO test
        case "darwin":
            return None #Apple Color Emoji" # TODO test
        case "win32":
            return "segoeuiemoji" 
        case _:
            return None

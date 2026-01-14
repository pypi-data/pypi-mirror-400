###########################################################
# Colorprint- Python module that lets you print colorfully#
# With CSS-like chaining in terminal                      #
# MIT license CoolGuy158-Git                              #
###########################################################

class Colors:
    # Text colors
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    
    # Background colors
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"
    
    # Styles
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    ITALIC = "\033[3m"
    STRIKETHROUGH = "\033[9m"

def cprint(text, cstyle="RESET"):
    style_codes = cstyle.upper().split("+")
    codes = ""
    for style in style_codes:
        codes += getattr(Colors, style, "")
    print(f"{codes}{text}{Colors.RESET}")

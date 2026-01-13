from colorama import Fore

LOG_COLORS = {
    "DEBUG": 0x95A5A6,
    "INFO": 0x5865F2,
    "WARNING": 0xF1C40F,
    "ERROR": 0xE74C3C,
    "CRITICAL": 0x9B59B6
}

COLORAMA_COLORS = {
    "DEBUG": Fore.LIGHTBLACK_EX,
    "INFO": Fore.BLUE,
    "WARNING": Fore.YELLOW,
    "ERROR": Fore.RED,
    "CRITICAL": Fore.MAGENTA
}

STATUS_ICONS = {
    "DEBUG": "•",
    "INFO": "✓",
    "WARNING": "!",
    "ERROR": "✗",
    "CRITICAL": "⚠",
}

LOG_LEVELS = list(LOG_COLORS.keys())

BASE_URL = "https://discord.com/api/v10"
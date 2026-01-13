import logging
import traceback
from datetime import datetime
from colorama import init, Fore, Style

init(autoreset=True)


def write_traceback_to_file():
    """
    Writes the current exception traceback to a DD-MM-YYYY.err file.
    Must be called from inside an except block.
    """
    date_str = datetime.now().strftime("%d-%m-%Y")
    filename = f"{date_str}.err"

    tb = traceback.format_exc()

    with open(filename, "a", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write(datetime.now().strftime("%H:%M:%S") + "\n")
        f.write(tb + "\n")


class ColorFormatter(logging.Formatter):
    LEVEL_COLORS = {
        "INFO": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": Fore.MAGENTA,
    }

    def format(self, record):
        time_str = f"{Fore.BLUE}{self.formatTime(record, '%d.%m.%Y %H:%M:%S')}{Style.RESET_ALL}"
        level_color = self.LEVEL_COLORS.get(record.levelname, "")
        level_str = f"{level_color}[{record.levelname}]{Style.RESET_ALL}"

        return f"{time_str} {level_str} {record.getMessage()}"


def get_logger(name: str):
    logger = logging.getLogger(name)

    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setFormatter(ColorFormatter())
        logger.addHandler(handler)

    return logger


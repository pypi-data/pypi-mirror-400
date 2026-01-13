from colorama import Fore, Back, Style, init

init(autoreset=True)

class Log:
    """
    日志
    """
    def __init__(self):
        self.is_debug = False

    def info(self, message):
        """
        信息
        """
        print(
            f"{Back.GREEN}[INFO]{Style.RESET_ALL} {Fore.LIGHTGREEN_EX} {message} {Style.RESET_ALL}"
        )

    def debug(self, message):
        """
        调试
        """
        if self.is_debug:
            print(
                f"{Back.YELLOW}[DEBUG]{Style.RESET_ALL} {Fore.LIGHTYELLOW_EX} {message} {Style.RESET_ALL}"
            )

    def error(self, message):
        """
        错误
        """
        print(
            f"{Back.RED}[ERROR]{Style.RESET_ALL} {Fore.LIGHTRED_EX} {message} {Style.RESET_ALL}"
        )

    def warning(self, message):
        """
        警告
        """
        print(
            f"{Back.YELLOW}[WARNING]{Style.RESET_ALL} {Fore.LIGHTYELLOW_EX} {message} {Style.RESET_ALL}"
        )


log = Log()
from plyer import notification
from rpa_quaestvm.logger import Logger


def print_log(title="", message="", timeout=0, app_name="", print_console=True, log_path="logs/rpa.log"):
    notification.notify( title=title, message=message, app_name=app_name, timeout=timeout)
    if print_console:
        logger = Logger.get_logger(log_path)
        logger.info(f"{title}: {message}")
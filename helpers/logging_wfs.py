import logging
import sys
from dataclasses import dataclass


@dataclass
class LoggerSetup:
    logger: logging.Logger
    handler: logging.Handler

class CustomFilter(logging.Filter):
    def __init__(self,pattern= None):
        super().__init__()
        self.pattern = pattern

    def filter(self, record):
        if self.pattern:
            if self.pattern in record.msg:
                return True
            return False
        return True

class CustomHandler(logging.Handler):
    def emit(self, record):
        print(f"customer Handler: {record.getMessage()}")


class ColorFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG:    "\033[34m",  # Blau
        logging.INFO:     "\033[32m",  # Grün
        logging.WARNING:  "\033[33m",  # Gelb
        logging.ERROR:    "\033[31m",  # Rot
        logging.CRITICAL: "\033[1;31m" # Rot fett
    }
    RESET = "\033[0m"

    def format(self, record):
        color = self.COLORS.get(record.levelno, self.RESET)
        message = super().format(record)
        return f"{color}{message}{self.RESET}"


class InitialLogging:


    @staticmethod
    def set_up_logger_std(log_level:str="INFO", formatter_str:str="%(message)s",
                          logger_name:str=__name__) -> LoggerSetup :
        """try:
            level_choice = logging._nameToLevel[log_level.upper()] #<-scheint ohne match case zu parsen
        except KeyError:
            raise ValueError(f"Unknown logging level: {log_level}")
    """
        level_choice = None
        match log_level.lower():
            case "info":
                level_choice = logging.INFO
            case "debug":
                level_choice = logging.DEBUG
            case "warning":
                level_choice = logging.WARNING
            case "error":
                level_choice = logging.ERROR
            case "critical":
                level_choice = logging.CRITICAL
            case _:
                raise ValueError (f"Unknown logging level: {log_level}")

        logger = logging.getLogger(logger_name)
        logger.propagate = False #<-
        logger.handlers.clear() #<-
        logger.setLevel(level=level_choice)

        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(ColorFormatter(formatter_str))
        logger.addHandler(handler)
        return LoggerSetup( logger, handler)
    """wenn 
    logger = set_up_logger_std()
    einen neuen Handler den alten ersetzen soll muss der alte entfern werden.
    
    logger = set_up_logger_std(log_level="DEBUG")
    
    logger.handlers.clear()        # alten Handler entfernen
    logger.addHandler(neuer_handler)
    
    
    import logging 
    
    # logging.disable(logging.DEBUG)#<- debug messages off, 
"""


def main():
    # logger = set_up_logger_std()
    # logger.info("Irgendwas")
    ...
if __name__ == '__main__':
    main()

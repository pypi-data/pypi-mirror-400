import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
import types


def log_newline(self, how_many_lines=1):
    """Temporariamente altera o formatter para um formatter em branco,
    insere linhas em branco no log, e restaura o formatter original.
    Útil para separar seções no log.

    Args:
        how_many_lines (int): Número de linhas em branco a inserir.
    """

    def set_handlers_formatter(formatter):
        handlers = (self.console_handler, self.file_handler)
        for handler in handlers:
            self.removeHandler(handler)
        for handler in handlers:
            handler.setFormatter(formatter)
            self.addHandler(handler)

    set_handlers_formatter(self.blank_formatter)
    for _ in range(how_many_lines):
        self.info("")
    set_handlers_formatter(self.default_formatter)


class LoggerInstance(logging.Logger):
    def newLine(self, how_many_lines=1):
        """Inserte uma linha em branco no log. Útil para separar logs de execuções diferentes
        Args:
            how_many_lines (int): Número de linhas em branco a inserir. Default: 1
        """
        # Reaproveita a função utilitária definida acima
        try:
            log_newline(self, how_many_lines)
        except Exception:
            # Não falhar em caso de erro ao inserir nova linha
            self.info("")


class Logger:
    _instances: dict[str, LoggerInstance] = {}

    def __init__(self, logs_path: str, name: str = None, level: str = "INFO"):
        self.logs_path = logs_path
        self.name = (
            name
            if name is not None
            else logs_path.replace(os.sep, "_").replace("/", "_")
        )
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(level=level)

        # Formato padrão
        formatter = logging.Formatter(
            "%(module)s [%(levelname)s] [%(asctime)s]: %(message)s"
        )
        self.logger.default_formatter = formatter

        # File Handler com rotação
        log_file = Path(logs_path)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)

        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)

        # Adiciona handlers
        # associa handlers ao logger e desabilita propagação para evitar mensagens duplicadas
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        self.logger.file_handler = file_handler
        self.logger.console_handler = console_handler
        self.logger.propagate = False
        self.logger.blank_formatter = logging.Formatter(fmt="")

        # adiciona método para criar uma linha em branco no log
        self.logger.newLine = types.MethodType(log_newline, self.logger)

        # Garante que `level` possa ser passado como string (ex: 'INFO') ou inteiro
        try:
            self.logger.setLevel(logging.getLevelName(level))
        except Exception:
            # fallback para valor passado diretamente
            self.logger.setLevel(level)

    @classmethod
    def get_logger(
        cls, logs_path: str, name: str = None, level: str = "INFO"
    ) -> LoggerInstance:
        _instance = cls._instances.get(logs_path, None)
        if not _instance:
            cls._instances[logs_path] = cls(logs_path, name, level)

        return cls._instances.get(logs_path).logger

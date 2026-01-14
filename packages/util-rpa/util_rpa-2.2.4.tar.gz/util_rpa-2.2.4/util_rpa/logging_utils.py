"""Utilidades de logging para RPA."""
import datetime
import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
import time
from functools import wraps

FMT = "%(asctime)-5s [%(levelname)s] %(name)s %(filename)s:%(lineno)d - %(message)s"
DATE_FMT = "%Y-%m-%d %H:%M:%S"

log = logging.getLogger(__name__)


def init_logging():
    """Logging centralizado.

    VARIABLES DE ENTORNO SOPORTADAS:
        LOG_LEVEL=DEBUG|INFO|WARNING|ERROR
        LOG_OUTPUT=CONSOLE|CONSOLE_FILE
    """
    root = logging.getLogger()

    if root.handlers:
        print("[LOG INIT] Logging ya inicializado, omitiendo configuración duplicada")
        return root

    # Nivel de log
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    print(f"[LOG INIT] level={level_name}")
    level = getattr(logging, level_name, logging.INFO)
    root.setLevel(level)

    formatter = logging.Formatter(FMT, DATE_FMT)

    # Consola siempre
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    root.addHandler(ch)

    # Archivo si LOG_OUTPUT = CONSOLE_FILE
    if os.getenv("LOG_OUTPUT", "CONSOLE").upper() == "CONSOLE_FILE":
        logs_dir = Path("./logs")
        logs_dir.mkdir(parents=True, exist_ok=True)

        # Sufijo horario → YYYYMMDDHH
        suffix = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        file_path = logs_dir / f"app_{suffix}.log"

        fh = RotatingFileHandler(
            str(file_path),
            maxBytes=10_000_000,
            backupCount=5
        )
        fh.setFormatter(formatter)
        root.addHandler(fh)

    root.info(f"[LOG INIT] Configuración completada. Nivel: {level_name}")
    return root


def timed(func):
    """Decorador para loggear el tiempo de ejecución de una función.

    - Usa el root logger directamente para evitar duplicación
    - No captura excepciones
    - No altera el resultado
    """
    func_name = func.__qualname__

    # Usar root logger directamente
    logger = logging.getLogger()

    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(
            "############### Inicio: %s ###############",
            func_name,
        )

        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start

        logger.info(
            "## Tiempo transcurrido (%s): %.2f s",
            func_name,
            duration,
        )
        logger.info(
            "############### Fin: %s ###############",
            func_name,
        )

        return result

    return wrapper

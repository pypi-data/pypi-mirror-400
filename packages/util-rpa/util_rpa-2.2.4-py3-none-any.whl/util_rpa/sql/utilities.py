"""Utilidades comunes para operaciones SQL."""
from pathlib import Path
import logging

log = logging.getLogger(__name__)


def validate_sql_error_log(error_log: Path) -> bool:
    """Valida si un archivo de log contiene errores reales de SQL Server.

    Args:
        error_log: Ruta al archivo de log de errores

    Returns:
        True si se detectaron errores, False en caso contrario

    Raises:
        RuntimeError: Si se detectan errores de SQL Server
    """
    if not error_log.exists():
        return False

    error_content = error_log.read_text(errors="ignore")

    # Buscar patrones específicos de error de SQL Server/BCP
    sql_error_patterns = [
        "Error =",
        "SQLState =",
        "Msg ",
        "[Microsoft][ODBC",
        "Login timeout expired",
        "Connection timeout",
    ]

    if any(pattern in error_content for pattern in sql_error_patterns):
        log.info(error_content)
        raise RuntimeError(f"Error detectado en log: {error_log}")

    return False

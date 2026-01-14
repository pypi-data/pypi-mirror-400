"""Pruebas de integración SQLCMD para util-rpa."""
from pathlib import Path
import logging

from util_rpa.sql.sqlcmd import SQLCmd
from util_rpa.sql.bcp import BCP
from util_rpa.sql.sql_credentials import SQLCredentials
import tempfile

from util_rpa.logging_utils import init_logging
init_logging()
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------
# CONFIGURACIÓN BASE (NO TOCAR)
# ---------------------------------------------------------------------
creds = SQLCredentials(
    hostname="127.0.0.1",
    database="db_test",
    username="user_1",
    password="pass_1"
)

# ---------------------------------------------------------------------
# 1. CASO FELIZ - SQLCMD
# ---------------------------------------------------------------------


def test_sqlcmd():
    """Prueba de lectura de tabla exitosa."""
    # Crear archivo temporal y escribir "SELECT * FROM TEST"
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(b"SELECT * FROM test_1")
        tmp_file_path = tmp_file.name
        log.info(f"Archivo SQL temporal creado: {tmp_file_path}")

    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file_log_path = tmp_file.name
        log.info(f"Archivo SQL temporal creado: {tmp_file_log_path}")

    sqlcmd = SQLCmd(creds)

    sqlcmd.run(
        sql_file=Path(tmp_file_path),
        output_log=Path(tmp_file_log_path)
    )

    # Leer archivo temporal
    with open(tmp_file_log_path, "r") as f:
        sql_query = f.read()
        log.info(sql_query)
    log.info("TEST 1 OK - Lectura exitosa")

# ---------------------------------------------------------------------
# 2. CASO FELIZ - BCP
# ---------------------------------------------------------------------


def test_bcp():
    """Prueba de lectura de tabla exitosa."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file_out_path = tmp_file.name
        log.info(f"Archivo SQL temporal creado: {tmp_file_out_path}")

    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file_log_path = tmp_file.name
        log.info(f"Archivo SQL temporal creado: {tmp_file_log_path}")

    bcp = BCP(creds)

    bcp.run(
        table="dbo.test_1",
        file=Path(tmp_file_out_path),
        operation="OUT",
        error_log=Path(tmp_file_log_path)
    )

    # Leer archivo temporal
    with open(tmp_file_out_path, "r") as f:
        sql_query = f.read()
        log.info(sql_query)

    log.info("TEST 2 OK - Lectura exitosa")

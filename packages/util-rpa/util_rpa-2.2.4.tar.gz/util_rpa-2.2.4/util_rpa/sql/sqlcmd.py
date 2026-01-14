"""SQLCMD client for executing SQL scripts against SQL Server."""
import subprocess
import shutil
from pathlib import Path
import os
import logging
from typing import Optional

from util_rpa.sql.sql_credentials import SQLCredentials
from util_rpa.sql.utilities import validate_sql_error_log

log = logging.getLogger(__name__)


class SQLCmd:
    """SQLCMD client for executing SQL scripts against SQL Server."""

    def __init__(self, credentials: SQLCredentials, encoding="65001"):
        self.credentials = credentials
        self.encoding = encoding
        self.bin = "sqlcmd" if os.name == "nt" else "/opt/mssql-tools/bin/sqlcmd"

    def run(
        self,
        sql_file: Path,
        output_log: Path,
        variables: Optional[dict] = None,
        validate_error: bool = True
    ):
        """Run a SQL script using sqlcmd."""
        if not sql_file.exists():
            raise FileNotFoundError(sql_file)

        tmp = sql_file.with_suffix(".tmp.sql")

        if variables:
            self._replace_vars(sql_file, tmp, variables)
        else:
            shutil.copy(sql_file, tmp)

        cmd = [
            self.bin,
            "-e", "-y", "0",
            "-i", str(tmp),
            "-o", str(output_log),
            "-S", self.credentials.hostname,
            "-d", self.credentials.database,
            "-U", self.credentials.username,
            "-P", self.credentials.password,
            "-f", self.encoding,
        ]

        # Crear comando censurado para el log
        cmd_censored = cmd.copy()
        password_index = cmd.index("-P") + 1
        cmd_censored[password_index] = "****"

        log.info("SQLCMD: %s", " ".join(cmd_censored))

        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        log.debug(proc.stdout)

        tmp.unlink(missing_ok=True)

        if validate_error and output_log.exists():
            validate_sql_error_log(output_log)

    def _replace_vars(self, src: Path, dst: Path, variables: dict):
        content = src.read_text()
        for k, v in variables.items():
            content = content.replace(k, v)
        dst.write_text(content)

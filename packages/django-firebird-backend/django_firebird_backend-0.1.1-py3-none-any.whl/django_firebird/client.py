"""
Firebird database client for Django.

Provides command-line client interface (isql-fb).
"""

import signal
import subprocess

from django.db.backends.base.client import BaseDatabaseClient


class DatabaseClient(BaseDatabaseClient):
    """Firebird command-line client wrapper."""

    executable_name = "isql-fb"

    @classmethod
    def settings_to_cmd_args_env(cls, settings_dict, parameters):
        """
        Return command-line arguments and environment for isql-fb.
        """
        args = [cls.executable_name]
        env = None

        # Build connection string
        host = settings_dict.get("HOST")
        port = settings_dict.get("PORT")
        database = settings_dict.get("NAME", "")

        if host:
            if port:
                connection_string = f"{host}/{port}:{database}"
            else:
                connection_string = f"{host}:{database}"
        else:
            connection_string = database

        args.append(connection_string)

        # Add user
        user = settings_dict.get("USER")
        if user:
            args.extend(["-user", user])

        # Add password
        password = settings_dict.get("PASSWORD")
        if password:
            args.extend(["-password", password])

        # Add charset
        options = settings_dict.get("OPTIONS", {})
        charset = options.get("charset", "UTF8")
        args.extend(["-charset", charset])

        # Add any additional parameters
        args.extend(parameters)

        return args, env

    def runshell(self, parameters):
        """Run the database shell."""
        sigint_handler = signal.getsignal(signal.SIGINT)
        try:
            # Allow SIGINT to pass to isql-fb to abort queries
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            args, env = self.settings_to_cmd_args_env(
                self.connection.settings_dict, parameters
            )
            subprocess.run(args, env=env, check=True)
        finally:
            # Restore the original SIGINT handler
            signal.signal(signal.SIGINT, sigint_handler)

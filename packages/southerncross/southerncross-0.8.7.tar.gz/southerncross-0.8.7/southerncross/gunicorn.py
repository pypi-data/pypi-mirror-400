import abc
import os
import sys
import logging
import time
from contextlib import suppress

from gunicorn.app.base import Application as _Application, Config
from gunicorn.glogging import Logger, loggers
from gunicorn.config import Setting
import gunicorn.util


def _set_owner_process(uid, gid, initgroups=False):
    """ set user and group of workers processes """

    if gid:
        if uid:
            try:
                username = gunicorn.util.get_username(uid)
            except KeyError:
                initgroups = False

        if initgroups:
            os.initgroups(username, gid)

        # This is the patched part (https://github.com/benoitc/gunicorn/issues/2770).
        if gid != os.getgid():
            os.setgid(gid)

    if uid and uid != os.getuid():
        os.setuid(uid)


gunicorn.util.set_owner_process = _set_owner_process


def _unix_socket_bind(self, sock):
    # This patch is for not adding "x" permissions.
    # Using umask configuration may affect other part including workertmp.
    sock.bind(self.cfg_addr)
    gunicorn.util.chown(self.cfg_addr, self.conf.uid, self.conf.gid)
    os.chmod(self.cfg_addr, 0o666)


gunicorn.sock.UnixSocket.bind = _unix_socket_bind


class LogDatetimeFormat(Setting):
    name = "log_datetime_format"
    section = "Logging"
    cli = ["--log-datetime-format"]
    meta = "STRING"
    default = r"[%Y-%m-%d %H:%M:%S %z]"
    desc = "The format of datetime logged in log file."

    def validator(val):
        return val.strip()


class PatchedLogger(Logger):
    def reopen_files(self):
        # This patch is reuqired because permission of reopened one is not change to
        # that of worker's one.
        # Related to https://github.com/benoitc/gunicorn/issues/1116
        super().reopen_files()

        def _chown(filename):
            os.chown(filename, self.cfg.user, self.cfg.group)

        if self.cfg.capture_output and self.cfg.errorlog != "-":
            with suppress(OSError):
                _chown(self.logfile.name)

        for log in loggers():
            for handler in log.handlers:
                if isinstance(handler, logging.FileHandler):
                    _chown(handler.stream.name)

    def setup(self, cfg):
        self.datefmt = cfg.log_datetime_format
        if self.datefmt == LogDatetimeFormat.default:
            # Default is apache common log format.
            self._access_log_datetime = "[%d/%b/%Y:%H:%M:%S %z]"
        else:
            self._access_log_datetime = cfg.log_datetime_format
        super().setup(cfg)

    def _set_handler(self, log, output, fmt, stream=None):
        super()._set_handler(log, output, CustomFormatter(
            fmt._fmt, fmt.datefmt), stream)

    def now(self):
        datefmt = self._access_log_datetime
        if "%f" in datefmt:
            datefmt = datefmt.replace("%f", str(time.time()).split(".")[1][:6])
        return time.strftime(datefmt)


class CustomFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            if "%f" in datefmt:
                datefmt = datefmt.replace("%f", str(record.created).split(".")[1][:6])
            s = time.strftime(datefmt, ct)
        else:
            s = time.strftime(self.default_time_format, ct)
            if self.default_msec_format:
                s = self.default_msec_format % (s, record.msecs)
        return s


class Application(_Application, metaclass=abc.ABCMeta):
    def __init__(self, app, **kwargs):
        self.usage = self.callable = self.prog = None
        self.app = app
        self.options = kwargs
        self.cfg = Config()
        self.current_config = {"app": {}, "gunicorn": {}}
        self.secret_key = os.urandom(24)

    @abc.abstractmethod
    def get_configuration(self):
        """This function is called to get configuration for this application.
        Return configuration of gunicorn and flask application with tuple of dictionary as
        follows.
        return (gunicorn_configuration, application_configuration)
        """
        raise NotImplementedError

    def pre_configure(self):
        """Implement this function to do something before configuration."""
        pass

    def post_configure(self):
        """Implement this function to do something after configuration."""
        pass

    def _setup(self, gunicorn_conf, app_conf):
        self.pre_configure()

        # Setup gunicorn configuration.
        gunicorn_conf.setdefault("limit_request_line", 0)
        gunicorn_conf.setdefault("capture_output", True)

        if gunicorn_conf.get("worker_class") == "gthread":
            gunicorn_conf.setdefault("threads", 8)

        gunicorn_conf.setdefault("logger_class", PatchedLogger)
        [self.cfg.set(k, v) for k, v in gunicorn_conf.items()]

        # Setup application configuration.
        self.app.config.update({k.upper(): v for k, v in app_conf.items()})

        # Setup logging configurations.
        self._setup_logging()

        self.post_configure()

    def _setup_logging(self):
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(CustomFormatter(Logger.error_fmt, self.cfg.log_datetime_format))
        handler._gal = True

        # Set log level.
        try:
            loglevel = getattr(logging, self.cfg.loglevel.upper())
            handler.setLevel(loglevel)
            self.app.logger.setLevel(loglevel)
        except AttributeError:
            raise ValueError("Invalid loglevel has been specified.")

        # Remove old log handler if exists
        while self.app.logger.handlers:
            self.app.logger.removeHandler(self.app.logger.handlers[0])
        self.app.logger.addHandler(handler)

    def _configure(self):
        gunicorn_conf, app_conf = self.get_configuration()

        self._setup(gunicorn_conf, app_conf)

        # If all the configuration has been completed, set to current_config.
        self.current_config.update(app=app_conf, gunicorn=gunicorn_conf)

    def run(self):
        try:
            self._configure()
        except Exception as e:
            print(e)
            sys.exit(-1)
        return super().run()

    def load(self):
        return self.app

    def load_config(self):
        try:
            self._configure()
        except Exception:
            self.app.logger.exception("Failed to load configuration.")
            self._setup(self.current_config["gunicorn"], self.current_config["app"])

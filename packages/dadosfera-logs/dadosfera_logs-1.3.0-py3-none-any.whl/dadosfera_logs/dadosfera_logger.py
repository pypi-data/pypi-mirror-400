import logging
import os
from distutils.util import strtobool
from logging import StreamHandler, FileHandler
from aws_logging_handlers.S3 import S3Handler
from pygelf import GelfTcpHandler, gelf
from loguru import logger
from typing import Callable, Optional, Dict
import sys


def dict_from_env(var_env_name):
    if os.environ.get(var_env_name) is not None:
        key_pairs = os.environ[var_env_name].split(",")
        env_variables = {}
        for key_pair in key_pairs:
            key, value = key_pair.split("=")
            env_variables[key] = value
        return env_variables


class DadosferaFormatter(logging.Formatter):
    def __init__(self, handler_type, fmt=None, style="%"):
        self.logger_elastic_apm_correlation = strtobool(os.environ.get('LOGGER_ELASTIC_APM_CORRELATION', 'true'))
        logger_console_extra = strtobool(os.environ.get('LOGGER_CONSOLE_EXTRA', 'false'))

        if fmt is None:
            fmt = "%(message)s"
        if handler_type == "console" and logger_console_extra:
            fmt = (fmt + "  EXTRA[%(extra)s]")
        super(DadosferaFormatter, self).__init__(fmt=fmt, style=style)

    def format(self, record):
        if self.logger_elastic_apm_correlation:
            if not hasattr(record, 'elasticapm_transaction_id'):
                record.elasticapm_transaction_id = None
                record.elasticapm_trace_id = None
                record.elasticapm_span_id = None

            record.__dict__["extra"].update({
                'transaction': {'id': record.elasticapm_transaction_id},
                'trace': {'id': record.elasticapm_trace_id},
                'span': {'id': record.elasticapm_span_id}
            })

        return super(DadosferaFormatter, self).format(record=record)


class DadosferaLoggingInterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        extras = {}
        dummy_record = logging.LogRecord("", 1, "", 1, None, {}, None)
        for key, value in record.__dict__.items():
            if key not in dummy_record.__dict__:

                # Ignore elasticapm extras as they are optionally added in DadosferaFormatter
                if not key.startswith("elasticapm"):
                    extras.update({key: value})

        message = record.getMessage().replace("{", "{{").replace("}", "}}")
        logger.opt(depth=depth, exception=record.exc_info).log(level, message, **extras)


class DadosferaLogger:
    @staticmethod
    def setup_logger_third_party_libraries_log_level():
        logger_third_party_libraries_log_level = dict_from_env('LOGGER_THIRD_PARTY_LIBRARIES_LOG_LEVEL')
        if logger_third_party_libraries_log_level is not None:
            for logger_third_party_library, log_level in logger_third_party_libraries_log_level.items():
                logging.getLogger(logger_third_party_library).setLevel(log_level)

    @classmethod
    def setup_logger(
            cls, 
            service_name: str, 
            service_environment: str, 
            file_log_path: str = None,
            s3_bucket: str = None,
            s3_key: str = None,
            filter_function = None,
            **kwargs
        ) -> logger:
        def log_uncaught_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            logging.exception("Uncaught exception: " + str(exc_value), exc_info=(exc_type, exc_value, exc_traceback))

        sys.excepthook = log_uncaught_exception

        logger_console_formatter = DadosferaFormatter(handler_type="console")
        logger_gelf_formatter = DadosferaFormatter(handler_type="gelf")
        logger_file_formatter = DadosferaFormatter(handler_type="file")
        logger_console_format = (
            '<level><green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green></level>  '
            '<level>{level: <10}</level>  '
            '<level><cyan>{name: <30}</cyan></level>  '
            '<level>{message}</level>'
        )
        logger_gelf_format = '{message}'
        logger_level = os.environ.get('LOGGER_LEVEL', 'INFO')
        logger_console_colorize = strtobool(os.environ.get('LOGGER_CONSOLE_COLORIZE', 'true'))

        # This should be set to False in StreamHandler (IN PRODUCTION) to avoid leaking sensitive data
        logger_console_diagnose = strtobool(os.environ.get('LOGGER_CONSOLE_DIAGNOSE', 'false'))

        logger_gelf_host = os.environ.get('LOGGER_GELF_HOST')
        logger_gelf_port = os.environ.get('LOGGER_GELF_PORT')

        if logger_gelf_port:
            logger_gelf_port = int(logger_gelf_port)

        logger.remove()

        root = logging.getLogger()
        if root.handlers:
            for handler in root.handlers:
                root.removeHandler(handler)
        logging.basicConfig(handlers=[DadosferaLoggingInterceptHandler()], level=logging.ERROR)
        DadosferaLogger.setup_logger_third_party_libraries_log_level()

        logger_config = {
            'handlers': [],
            'extra': {'service': {'name': service_name, 'environment': service_environment}, **kwargs}
        }

        logger_console_handler = StreamHandler()
        logger_console_handler.setFormatter(logger_console_formatter)
        logger_config['handlers'].append(
            {
                'sink': logger_console_handler,
                'level': logger_level,
                'format': logger_console_format,
                'diagnose': logger_console_diagnose,
                'colorize': logger_console_colorize,
                'serialize': False,
                'filter': filter_function
            }
        )

        if logger_gelf_host is not None and logger_gelf_port is not None:
            # Adding loguru SUCCESS level.no into gelf levels
            gelf.LEVELS.update({logger.level("SUCCESS").no: logger.level("SUCCESS").no})

            logger_gelf_handler = GelfTcpHandler(host=logger_gelf_host, port=logger_gelf_port)
            logger_gelf_handler.setFormatter(logger_gelf_formatter)
            logger_config['handlers'].append(
                {
                    'sink': logger_gelf_handler,
                    'level': logger_level,
                    'format': logger_gelf_format,
                    'diagnose': False,  # This should be set to False in GELFUDPHandler to avoid leaking sensitive data
                    'serialize': True,
                    'filter': filter_function
                }
            )

        if file_log_path:
            logger_file_handler = FileHandler(filename=file_log_path, mode='a')
            logger_file_handler.setFormatter(logger_file_formatter)
            logger_config['handlers'].append(
                {
                    'sink': logger_file_handler,
                    'level': 'INFO',
                    'format': logger_console_format,
                    'diagnose': False,
                    'colorize': False,
                    'serialize': False,
                    'filter': filter_function
                }
            )

        if s3_bucket is not None and s3_key is not None:
            s3_handler = S3Handler(s3_key, s3_bucket, workers=1, chunk_size=5120, encryption_options={})
            s3_handler.stream._current_object = s3_handler.stream._get_stream_object(s3_key)
            s3_handler.setFormatter(logger_file_formatter)
            logger_config['handlers'].append(
                {
                    'sink': s3_handler,
                    'level': 'INFO',
                    'format': logger_console_format,
                    'diagnose': False,
                    'colorize': False,
                    'serialize': False,
                    'filter': filter_function
                }
            )

        logger.configure(**logger_config)
        return logger

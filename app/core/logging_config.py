import logging
import sys
import structlog

def setup_logging():
    """
    Configures structured logging for the application.
    """
    # A list of processors that will be applied to all log records.
    shared_processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
    ]

    structlog.configure(
        processors=[
            # This processor is first to filter logs based on level.
            structlog.stdlib.filter_by_level,
            # Add context variables to the log record.
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        # The 'context_class' allows for thread-local context storage.
        context_class=dict,
        # The 'logger_factory' creates standard Python loggers.
        logger_factory=structlog.stdlib.LoggerFactory(),
        # 'wrapper_class' is the main entry point for logging.
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure the 'stdlib' formatter which will render the logs.
    formatter = structlog.stdlib.ProcessorFormatter(
        # The final processor renders the log record as a JSON string.
        processor=structlog.processors.JSONRenderer(),
        # These processors are applied before rendering.
        foreign_pre_chain=shared_processors,
    )

    # Use a standard library handler to output logs to the console.
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # Get the root logger and add our configured handler.
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)

    print("Structured logging configured.")
import logging

def configure_logging():
    # Suppress all SQLAlchemy logs
    for logger_name in [
        'sqlalchemy',
        'sqlalchemy.engine',
        'sqlalchemy.orm',
        'sqlalchemy.pool',
        'sqlalchemy.dialects',
        'sqlalchemy.dialects.postgresql',
    ]:
        logging.getLogger(logger_name).setLevel(logging.WARNING)
        logging.getLogger(logger_name).propagate = False
    
    # Configure root logger for API logs
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s: %(message)s',
        force=True  # Override existing handlers
    )
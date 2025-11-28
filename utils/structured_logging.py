import logging, json, os, datetime

_logger = None

def _init_logger():
    global _logger
    if _logger is not None:
        return _logger
    logger = logging.getLogger('structured')
    if not logger.handlers:
        level = os.getenv('APP_LOG_LEVEL', 'INFO').upper()
        logger.setLevel(getattr(logging, level, logging.INFO))
        stream_handler = logging.StreamHandler()
        # Simple formatter outputs message only; we already build JSON string
        formatter = logging.Formatter('%(message)s')
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
        # Optional file handler when APP_LOG_FILE is set
        log_file = os.getenv('APP_LOG_FILE')
        if log_file:
            try:
                # Ensure directory exists
                os.makedirs(os.path.dirname(log_file), exist_ok=True)
            except Exception:
                pass
            try:
                file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
            except Exception:
                # If file handler fails, continue with stream only
                pass
        logger.propagate = False
    _logger = logger
    return _logger

def log_event(event_type: str, **fields):
    """Log a structured JSON line with an event_type and arbitrary key/values.

    Adds timestamp automatically. Values must be JSON serializable.
    Silently ignores serialization errors by coercing to string.
    """
    logger = _init_logger()
    payload = {
        'ts': datetime.datetime.utcnow().isoformat() + 'Z',
        'event': event_type,
    }
    for k, v in fields.items():
        try:
            json.dumps(v)  # test serializable
            payload[k] = v
        except Exception:
            payload[k] = str(v)
    try:
        line = json.dumps(payload, ensure_ascii=False)
    except Exception:
        # Fallback: stringify payload
        line = '{"event":"serialization_error","original_event":"%s"}' % event_type
    logger.info(line)

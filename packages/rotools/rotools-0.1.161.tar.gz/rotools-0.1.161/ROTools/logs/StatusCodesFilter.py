import logging


class StatusCodesFilter(logging.Filter):
    def __init__(self, status_codes=(304,), logger_prefix="access."):
        super().__init__()
        self.status_codes = set(status_codes)
        self.logger_prefix = logger_prefix

    def filter(self, record: logging.LogRecord) -> bool:
        if not record.name.startswith(self.logger_prefix):
            return True
        sc = getattr(record, "status_code", None)
        return sc not in self.status_codes
"""
Queue handler class queue_handler_t.

SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import logging as l
from logging.handlers import QueueHandler as base_t

from logger_36.constant.record import SHOW_W_RULE_ATTR


class queue_handler_t(base_t):
    """
    Custom QueueHandler for multiprocess logging.

    Extends the standard QueueHandler to ensure log records are properly
    formatted before being sent through the queue. This is necessary because
    some log record attributes may not be serializable or may need special
    handling in a multiprocess context.
    """

    def prepare(self, record: l.LogRecord, /) -> l.LogRecord:
        """
        Prepare a log record for queue transmission.

        Ensures the record's message is a string (or special rule marker) before
        sending through the multiprocessing queue. Non-string messages are
        converted to strings to avoid serialization issues.

        Args:
            record (l.LogRecord): The log record to prepare.

        Returns:
            l.LogRecord: The prepared record, potentially with modified msg attribute.

        Note:
            Records marked with SHOW_W_RULE_ATTR (display rules) are exempt from
            string conversion as they have special handling.
        """
        if not (
            isinstance(record.msg, str) or getattr(record, SHOW_W_RULE_ATTR, False)
        ):
            record.msg = str(record.msg)

        return record

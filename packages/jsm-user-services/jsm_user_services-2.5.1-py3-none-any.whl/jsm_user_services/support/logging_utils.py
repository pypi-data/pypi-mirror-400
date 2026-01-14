import logging

from jsm_user_services.services.user import get_user_session_id


class UserSessionIDFilter(logging.Filter):
    EMPTY_FIELD = "-"

    def filter(self, record):
        record.session_id = get_user_session_id() or self.EMPTY_FIELD
        return True

import logging

from jsm_user_services.support.http_utils import request
from jsm_user_services.support.local_threading_utils import get_from_local_threading
from jsm_user_services.support.settings_utils import get_from_settings_or_raise_missing_config

logger = logging.getLogger(__name__)


def perform_recaptcha_validation(g_recaptcha_response: str) -> bool:
    """
    Performs a request to Google in order to validate the reCAPTCHA.
    For more details, check: https://developers.google.com/recaptcha/docs/verify
    """

    google_recaptcha_url = get_from_settings_or_raise_missing_config(
        "GOOGLE_RECAPTCHA_URL", "https://www.google.com/recaptcha/api/siteverify"
    )
    google_recaptcha_secret_key = get_from_settings_or_raise_missing_config("GOOGLE_RECAPTCHA_SECRET_KEY")

    min_score_threshold = float(get_from_settings_or_raise_missing_config("GOOGLE_RECAPTCHA_SCORE_THRESHOLD", "0.8"))

    google_recaptcha_bypass_ip_header_name = get_from_settings_or_raise_missing_config(
        "GOOGLE_RECAPTCHA_BYPASS_IP_HEADER_NAME", "true-client-ip"
    )

    user_ip = get_from_local_threading("user_ip")
    headers = {google_recaptcha_bypass_ip_header_name: user_ip}
    data = {"response": g_recaptcha_response, "secret": google_recaptcha_secret_key}

    if user_ip:
        data["remoteip"] = user_ip

    logger.debug("Performing request to Google to check if recaptcha is valid")

    with request() as r:
        resp = r.post(google_recaptcha_url, data=data, headers=headers)

    result_json = resp.json()

    if resp.status_code != 200:
        logger.warning(
            "[GoogleRecaptcha] Validation failed for response: %s | Status code: %s | Response body: %s",
            g_recaptcha_response,
            resp.status_code,
            result_json,
        )
        return False

    if result_json.get("success") is not True:
        logger.info("[GoogleRecaptcha] Recaptcha is not valid: %s", result_json)
        return False

    if result_json.get("score", 0) < min_score_threshold:
        logger.info("[GoogleRecaptcha] Score %s below threshold %s", result_json.get("score", 0), min_score_threshold)
        return False

    logger.info(
        "[GoogleRecaptcha] Validation succeeded. min_score_threshold: %s, response body: %s",
        min_score_threshold,
        result_json,
    )
    return True

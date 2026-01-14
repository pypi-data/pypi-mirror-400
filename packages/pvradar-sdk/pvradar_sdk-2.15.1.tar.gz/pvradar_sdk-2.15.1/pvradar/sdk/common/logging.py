import logging

from ..display.jupyter_helpers import maybe_display_alert
from .constants import SDK_VERSION
from ..common.common_utils import compare_versions
from ..common.exceptions import OutdatedSdkError
from ..modeling.basics import SerializedAlert

logger = logging.getLogger('pvradar.sdk')


def log_alert(alert: SerializedAlert):
    if not maybe_display_alert(alert):
        logger.info(f'Alert: {alert["text"]}')


def log_package_missing(package_name: str, feature: str):
    log_alert(
        {
            'type': 'warning',
            'text': f'Python package <b>{package_name}</b> is required for {feature}. Please install it to use this feature.',
            'html': (
                f'<p>The package "<strong>{package_name}</strong>" is required for {feature}.</p>'
                f'<p>Please install it using <code>pip install {package_name}</code></p>'
            ),
        }
    )


# here kwargs ensures that callers can pass arbitrary extra arguments without causing errors
# in case the signature of this function changes in the future
def require_sdk_version(min_version: str, **kwargs):
    current_version = SDK_VERSION
    if compare_versions(min_version, current_version) > 0:
        message = f'SDK version {min_version} or higher is required. You are using version {current_version}'
        log_alert(
            {
                'type': 'critical',
                'text': message,
                'html': (
                    f'PVRADAR SDK version <b>{min_version}</b> or higher is required. '
                    f'You are using version <b>{current_version}</b></br>'
                    'Usually upgrading is as simple as running <code>pip install --upgrade pvradar-sdk</code> '
                    'in the terminal within the virtual environment<br/>'
                    'Please refer to the '
                    '<a href="https://pvradar.com/product/python-package/docs">Documentation</a> '
                    'for more details'
                ),
            }
        )
        raise OutdatedSdkError(message)

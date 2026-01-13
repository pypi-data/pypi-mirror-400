""" Rally Notification Support

Most notifications destinations are configured with Notification Presets, typically from the UI.
You can send notifications to those recipients using this module.

Import example:

>>> from rally import notifications
"""
__all__ = [
    'send_notification'
]

from .context import context, JOB_UUID, ASSET_ID
from ._session import _getSession


def send_notification(destination, message, subject='No Subject: Notification from Decision Engine', attributes=None, attachments=None,
                      group_id=None, direct=False, reply_to=None, bcc=None):
    """ Send a notification or email.  The notification will be queued with Rally's Notification system and sent in the future by default,
    or sent immediately if direct is set true.

    :param destination: name of the notification preset, or email addresses. Multiple emails must be comma separated.
    :type destination: str
    :param message: notification contents, eventDetails for eventbridge, or event value for Kafka
    :type message: str
    :param subject: notification subject - defaults to 'No Subject: Notification from Decision Engine', eventbridge DetailType,
        or event key (defaults to None) for Kafka
    :type subject: str, optional
    :param attributes: key value pairs to include with the notification, not supported with all notification types,
        defaults to no attributes, for eventbridge can be used to override Source and Time attributes.
    :type attributes: dict, optional
    :param attachments: includes the labeled files as notification attachments, not supported with all notification
        types, defaults to no attachments
    :type attachments: list(str), optional
    :param group_id: the string value of the AWS Message Group Id to use in the notification request if applicable,
        defaults to no group
    :type group_id: str, optional
    :param direct: flag indicating if notification should be send directly or queued, defaults to false (queued)
    :type direct: bool, optional
    :param reply_to: repyTo header for emails
    :type reply_to: str, optional
    :param bcc: bcc for emails. Multiple emails must be comma separated.
    :type bcc: str, optional

    Usage:

    >>> notifications.send_notification('Notify Preset', 'Supply Chain is complete!', subject='Asset: Yak Incorporated')

    Sending Emails:

    >>> notifications.send_notification('rally@sdvi.com', 'Did you know Rally can send emails?', subject='Basic Email')
    >>> notifications.send_notification('rally@sdvi.com, rally2@sdvi.com', 'Did you know Rally can send emails?', subject='Multiple Receiver Email', bcc='rally3@sdvi.com')

    Sending EventBridge:

    >>> notifications.send_notification('EventBridge Preset', '{"key":"value"}', subject='DetailType', attributes={'Source':'CustomSource'})
    """
    _attachments = []
    if attachments:
        for file in attachments:
            if not isinstance(file, str):
                raise TypeError(f'invalid attachment \'{file}\' must be of type string')
            _attachments.append(file)

    if not isinstance(subject, str):
        raise TypeError(f'invalid subject \'{subject}\' must be of type string')

    s = _getSession()
    payload = {
        'destination': destination,
        'text': message,
        'subject': subject,
        'attributes': attributes,
        'attachments': _attachments if _attachments else None,
        'messageGroupId': group_id,
        'direct' : direct,
        'replyTo' : reply_to,
        'bcc': bcc
    }
    if direct:
        payload['assetId'] = context(ASSET_ID)
    else:
        payload['jobUuid'] = context(JOB_UUID)
        payload['format'] =  'raw'

    s.post('v1.0/notify/events/new', json=payload)


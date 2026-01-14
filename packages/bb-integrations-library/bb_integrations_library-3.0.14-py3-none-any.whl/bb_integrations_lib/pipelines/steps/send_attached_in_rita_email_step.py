from io import BytesIO

from bb_integrations_lib.gravitate.rita_api import GravitateRitaAPI
from bb_integrations_lib.models.rita.email import EmailData, EmailAttachment
from bb_integrations_lib.pipelines.steps.send_rita_email_step import SendRitaEmailStep
from bb_integrations_lib.shared.model import RawData


class SendAttachedInRitaEmailStep(SendRitaEmailStep):
    def __init__(self, rita_client: GravitateRitaAPI, to: str | list[str], html_content: str, subject: str,
                 timeout: float = 10.0, *args, **kwargs):
        """
        Send one or more RawData objects as an email attachment via RITA.

        :param rita_client: Instantiated RITA API client using an API key with email.send scope.
        :param to: Email address(es) to send the email to.
        :param html_content: HTML content (body) of the email.
        :param subject: Subject of the email.
        :param timeout: The maximum amount of time allowed to send the email. Large emails may take longer to send than
          the default.
        """
        super().__init__(rita_client=rita_client, timeout=timeout, *args, **kwargs)
        self.to = to
        self.html_content = html_content
        self.subject = subject

    def describe(self):
        return "Send email via RITA with RawData(s) from step input attached"

    async def execute(self, i: RawData | list[RawData]):
        if isinstance(i, RawData):
            i = [i]
        ed = EmailData(
            to=self.to,
            html_content=self.html_content,
            subject=self.subject,
            attachments=[
                EmailAttachment(
                    file_name=rd.file_name,
                    file_data=rd.data.getvalue() if type(rd.data) == BytesIO else rd.data,
                ) for rd in i
            ]
        )
        await super().execute(ed)

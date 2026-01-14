from bb_integrations_lib.gravitate.rita_api import GravitateRitaAPI
from bb_integrations_lib.models.rita.email import EmailData
from bb_integrations_lib.protocols.pipelines import Step


class SendRitaEmailStep(Step):
    def __init__(self, rita_client: GravitateRitaAPI, timeout: float = 10.0, raise_on_error: bool = True,
                 email_data_override: EmailData | None = None, *args, **kwargs):
        """
        Instantiate a pipeline step that sends an email via RITA.

        :param rita_client: Instantiated RITA API client using an API key with email.send scope.
        :param timeout: The maximum amount of time allowed to send the email. Large emails may take longer to send than
          the default.
        :param raise_on_error: Whether to raise an exception if the email send HTTP response indicates an error.
        :param email_data_override: Explicitly specified EmailData object to use instead of step input. This allows
          specifying a static email for either testing or notifications.
        """
        super().__init__(*args, **kwargs)
        self.rita_client = rita_client
        self.timeout = timeout
        self.raise_on_error = raise_on_error
        self.ed_override = email_data_override

    def describe(self) -> str:
        return "Send email via RITA"

    async def execute(self, i: EmailData):
        if self.ed_override:
            resp = await self.rita_client.send_email(self.ed_override, self.timeout)
        else:
            resp = await self.rita_client.send_email(i, self.timeout)
        if self.raise_on_error:
            resp.raise_for_status()

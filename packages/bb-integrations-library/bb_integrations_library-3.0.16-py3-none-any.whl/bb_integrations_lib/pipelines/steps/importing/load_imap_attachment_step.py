from time import sleep
from typing import Any, AsyncIterator

from loguru import logger

from bb_integrations_lib.gravitate.rita_api import GravitateRitaAPI
from bb_integrations_lib.models.pipeline_structs import NoPipelineData
from bb_integrations_lib.protocols.pipelines import GeneratorStep
from bb_integrations_lib.provider.imap.client import IMAPClient
from bb_integrations_lib.secrets import IMAPCredential
from bb_integrations_lib.secrets.credential_models import IMAPAuthSimple
from bb_integrations_lib.shared.model import RawData, FileConfigRawData


class LoadIMAPAttachmentStep(GeneratorStep):
    def __init__(
            self,
            rita_client: GravitateRitaAPI,
            imap_client: IMAPClient,
            attachment_extension: str,
            to_email_address: str | None = None,
            from_email_address: str | None = None,
            delivered_to_email_address: str | None = None,
            retries: int = 3,
            email_subject: str | None = None,
            bucket_name: str | None = None,
            config_names: list[str] | None = None,
            raise_on_no_data: bool = False,
            *args, **kwargs

    ):
        """
        Load attachments from an IMAP folder / mailbox. The search criteriae are reductive; more filters are ANDed and
        will result in fewer results. If no filters are provided, the default is to search for all emails in the inbox.

        :param rita_client: The RITA client to retrieve fileconfigs with.
        :param imap_client: The IMAP account which owns the mailbox.
        :param attachment_extension: Sets the extension on the returned RawData.
        :param to_email_address: Matches emails sent TO this address, if provided.
        :param from_email_address: Matches emails sent FROM this address, if provided.
        :param delivered_to_email_address: Matches emails "Delivered-To" this address, if provided. Differs from the
          ``to_email_address`` argument - this matches on the Delivered-To mail header, which some email services set if
          they are automatically forwarding from their mailbox to ours.
        :param retries: How many times to retry a mail query that fails.
        :param email_subject: The subject of the email to search for.
        :param bucket_name: The config bucket that holds the config_names configs.
        :param config_names: The names of FileConfigs to use to search for.
        :param raise_on_no_data: Whether to raise an error when there are no matching emails.
        """
        super().__init__(*args, **kwargs)
        self.rita_client = rita_client
        self.imap_client = imap_client

        self.to_email_address = to_email_address
        self.from_email_address = from_email_address
        self.delivered_to_email_address = delivered_to_email_address
        self.email_subject = email_subject
        self.attachment_extension = attachment_extension
        self.retries = retries
        criteria_parts = ['UNSEEN']

        if self.from_email_address:
            criteria_parts.append(f'FROM {self.from_email_address}')

        if self.delivered_to_email_address:
            criteria_parts.append(f'HEADER Delivered-To {self.delivered_to_email_address}')
        if self.to_email_address:
            criteria_parts.append(f'TO {self.to_email_address}')

        if self.email_subject:
            if ' ' in self.email_subject:
                criteria_parts.append(f'SUBJECT "{self.email_subject}"')
            else:
                criteria_parts.append(f'SUBJECT {self.email_subject}')
        self.criteria = '(' + ' '.join(criteria_parts) + ')'

        self.bucket_name = bucket_name
        self.config_names = config_names

        self.raise_on_no_data = raise_on_no_data

    def describe(self) -> str:
        return "Get attachments from IMAP folder"

    async def generator(self, i: Any) -> AsyncIterator[RawData]:
        for config_name in self.config_names:
            async for result in self.load_using_config(config_name):
                yield result

    async def load_using_config(self, config_name: str) -> AsyncIterator[RawData]:
        file_config = (
            await self.rita_client.get_fileconfig_by_name(self.bucket_name, config_name)
        )[config_name]
        logger.info(f"Searching with criteria {self.criteria}")
        message_indexes = self.imap_client.search(self.criteria)
        logger.info(f"Found {len(message_indexes)} new emails in inbox meeting search criteria")
        if self.raise_on_no_data and not message_indexes:
            raise NoPipelineData("No new emails found in inbox meeting search criteria")
        for idx in message_indexes:
            logger.info(f"Fetching mail {idx}")
            for retry in range(self.retries):
                try:
                    message = self.imap_client.fetch(idx)
                    attachment_rd = self.imap_client.get_attachment_from_message(
                        message,
                        extension=self.attachment_extension,
                        return_rawdata=True
                    )
                    if attachment_rd is not None:
                        logger.info(f"Fetched attachment from email id: {idx}")
                        if file_config:
                            attachment_rd = FileConfigRawData(
                                file_name=attachment_rd.file_name,
                                data=attachment_rd.data,
                                file_config=file_config
                            )
                            self.pipeline_context.file_config = file_config
                        yield attachment_rd
                        break
                    else:
                        raise Exception("Returned attachment was None")
                except Exception as e:
                    logger.error(f"Error reading data from mail: {e}")
                    sleep(3)
                    self.imap_client.mark_unseen(idx)

    @staticmethod
    def _unplus_email(email_str: str) -> str:
        """
        Remove plus-addressing from an email to get the 'base' email account. If there is no plus, the original email
        string is returned. Note that in either case, the email must have an @ symbol in it.
        """
        split_at = email_str.split("@")
        if len(split_at) != 2:
            raise ValueError(f"Email address '{email_str}' is not in the expected format")
        first_half = split_at[0]
        has_plus = "+" in first_half
        if has_plus:
            unplussed = first_half[:first_half.rfind("+")]
            return f"{unplussed}@{split_at[1]}"
        return email_str


if __name__ == "__main__":
    async def main():
        step = LoadIMAPAttachmentStep(
            rita_client=GravitateRitaAPI(
                base_url="",
                client_id="",
                client_secret=""
            ),
            imap_client=IMAPClient(
                credentials=IMAPCredential(
                    host="",
                    port=993,
                    email_address="",
                    auth=IMAPAuthSimple(
                        password="",
                    )
                )
            ),
            attachment_extension=".csv",
            bucket_name="/Inventory",
            config_names=["wawa"]
        )
        async for result in step.generator(None):
            print(result)


    import asyncio

    asyncio.run(main())

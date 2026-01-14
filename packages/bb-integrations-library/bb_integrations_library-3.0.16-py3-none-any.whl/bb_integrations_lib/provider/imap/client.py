import email
import imaplib
import time
from email.message import Message
from io import BytesIO
from typing import Iterable, Optional, List, Self

import requests
from charset_normalizer import detect
from loguru import logger

from bb_integrations_lib.secrets.credential_models import IMAPAuthOAuth, IMAPCredential
from bb_integrations_lib.shared.model import RawData
from bb_integrations_lib.util.utils import load_credentials


class ImapEmailIntegration:
    """Integration client to download attachments from an IMAP email server."""

    def __init__(
            self,
            credentials: IMAPCredential,
            criteria: str,
            retries: int = 3,
            type: str = 'sales',
            file_extension: str = '.csv',
    ):
        self.credentials = credentials
        self.criteria = criteria
        self.retries = retries
        self.type = type
        self.file_extension = file_extension

    def get_raw_data(self) -> Iterable[RawData]:
        mail = IMAPClient(self.credentials)

        mail.connect()
        unseen_message_idxs = mail.search(self.criteria)
        logger.info(f"📬 Found {len(unseen_message_idxs)} new emails in tank data inbox")

        for idx in unseen_message_idxs:
            retry_count = 0
            while retry_count < self.retries:
                try:
                    message = mail.fetch(idx)
                    attachment = mail.get_attachment_from_message(message, extension=self.file_extension)

                    if not attachment:
                        logger.error(f"⚠️ No valid attachment found in email id: {idx}")
                        break

                    if attachment is None:
                        logger.error(f"⚠️ Could not process file from email id: {idx}")
                        break  # No need to retry if processing failed

                    raw_data = RawData(
                        file_name=f"data_{idx}{self.file_extension}",
                        data=attachment,
                    )
                    yield raw_data
                    logger.info(f"✅ Successfully processed {self.file_extension} file from email id: {idx}")
                    break  # Exit retry loop on success

                except Exception as e:
                    retry_count += 1
                    logger.error(f"❌ Error reading data from email (Attempt {retry_count}/{self.retries}): {e}")
                    time.sleep(5)
                    if retry_count == self.retries:
                        mail.mark_unseen(idx)


class IMAPClient:
    def __init__(
            self,
            credentials: IMAPCredential,
            mailbox: str = "INBOX",
            dry_run: bool = False,
    ):
        self.credentials = credentials
        self.mailbox = mailbox
        self.mail = None
        self.dry_run = dry_run

    @classmethod
    def from_credential_file(cls, credential_file_name: str | None = None) -> Self:
        credential_file_name = credential_file_name or "ftp.credentials"
        credentials = load_credentials(credential_file_name)
        return cls(credentials)

    def test_imap(self, auth_string):
        """Authenticate with Gmail IMAP using XOAUTH2 in dry_run mode."""
        try:
            imap_conn = imaplib.IMAP4_SSL('imap.gmail.com')
            imap_conn.debug = 4
            imap_conn.authenticate('XOAUTH2', lambda x: auth_string)
            imap_conn.select('INBOX')
            logger.success("✅ IMAP Authentication Successful! (Dry Run Mode)")
            return True
        except imaplib.IMAP4.error as e:
            logger.error(f"❌ IMAP Authentication Failed (Dry Run Mode): {e}")
            return False

    def generate_oauth2_string(self, username, access_token):
        """Generates a properly formatted OAuth2 authentication string."""
        auth_string = f"user={username}\x01auth=Bearer {access_token}\x01\x01"
        return auth_string.encode("utf-8")  # MUST return UTF-8 encoded bytes

    def call_refresh_token(self, client_id, client_secret, refresh_token):
        """Fetch a new access token using the refresh token."""
        url = "https://oauth2.googleapis.com/token"
        payload = {
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }

        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        response = requests.post(url, data=payload, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            print("❌ Failed to refresh token:", response.text)
            raise Exception(f"Failed to refresh token: {response.text}")

    def refresh_authorization(self, client_id, client_secret, refresh_token):
        """Refresh OAuth access token."""
        response = self.call_refresh_token(client_id, client_secret, refresh_token)
        if "access_token" in response:
            return response["access_token"], response["expires_in"]
        else:
            raise Exception("❌ Failed to get access token: Invalid response")

    def connect(self):
        if self.mail:
            return self.mail
        self.mail = imaplib.IMAP4_SSL(self.credentials.host, self.credentials.port)
        self.mail.debug = 4
        auth = self.credentials.auth
        if isinstance(auth, IMAPAuthOAuth):
            try:
                access_token, expires_in = self.refresh_authorization(
                    client_id=auth.client_id,
                    client_secret=auth.client_secret,
                    refresh_token=auth.refresh_token
                )
                auth_string = self.generate_oauth2_string(self.credentials.email_address, access_token)
                if self.dry_run:
                    logger.info("Dry run mode: testing IMAP Authentication only.")
                    self.test_imap(auth_string)
                    return None
                self.mail.authenticate("XOAUTH2", lambda x: auth_string)
            except imaplib.IMAP4.error as e:
                logger.error(f"Gmail authentication failed: {e}")
                raise Exception("Invalid Gmail OAuth authentication. Check your credentials and refresh token.")
        else:
            self.mail.login(self.credentials.email_address, self.credentials.auth.password)
        self.mail.select(self.mailbox)
        return self.mail

    def change_mailbox(self, mailbox: str):
        """Change the mailbox (folder) in IMAP."""
        self.connect().select(mailbox)

    def search(self, criteria: str) -> List[int]:
        """Search for emails based on criteria (e.g., '(UNSEEN)')."""
        status, message_indexes = self.connect().search(None, criteria)
        message_indexes = [int(idx) for idx in next(iter(message_indexes), "").split()]
        return message_indexes

    def fetch(self, message_index: int) -> Optional[Message]:
        """Fetch an email by its index."""
        status, message = self.connect().fetch(str(message_index), "(RFC822)")
        try:
            if message and message[0]:
                raw_email_string = message[0][1].decode("utf-8")
                return email.message_from_string(raw_email_string)
        except (IndexError, AttributeError) as e:
            logger.error(f"Error fetching email {message_index}: {e}")
        return None

    def mark_unseen(self, message_index: int):
        """Mark an email as unseen (unread)."""
        try:
            self.connect().store(str(message_index), "-FLAGS", "\\Seen")
        except Exception as e:
            logger.error(f"Error marking email {message_index} as unseen: {e}")

    @staticmethod
    def get_attachment_from_message(message: Message, extension: str, return_rawdata: bool = False) -> Optional[bytes | str | RawData]:
        """Extracts an email attachment and handles unknown encoding.

        - Returns **decoded text** for text-based files (CSV, TXT, JSON, etc.).
        - Returns **raw binary data** for non-text files (PDF, XLSX, ZIP, etc.).
        """
        for part in message.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get("Content-Disposition") is None and part.get_filename() is None:
                continue
            if part.get_filename() and part.get_filename().lower().endswith(extension.lower()):
                try:
                    raw_bytes = part.get_payload(decode=True)
                    if extension.lower() in [".pdf", ".xlsx", ".xls", ".zip", ".png", ".jpg", ".jpeg", ".gif", ".docx",
                                             ".pptx"]:
                        logger.info(f"🗂 Binary file detected ({part.get_filename()}), returning raw bytes")
                        return raw_bytes
                    detected = detect(raw_bytes)
                    encoding = detected["encoding"]
                    if not encoding:
                        logger.warning(
                            f"⚠️ Encoding could not be detected for {part.get_filename()}, defaulting to latin-1")
                        encoding = "latin-1"
                    logger.info(f"📄 Detected encoding: {encoding} for {part.get_filename()}")
                    if return_rawdata:
                        return RawData(file_name=part.get_filename(), data=BytesIO(raw_bytes))
                    else:
                        return raw_bytes.decode(encoding, errors="replace")  # ✅ Decode with replacement for errors
                except UnicodeDecodeError as e:
                    logger.error(f"❌ Failed to decode {part.get_filename()} as text: {e}")
                    if return_rawdata:
                        return RawData(file_name=part.get_filename(), data=BytesIO(raw_bytes))
                    else:
                        return raw_bytes  # ✅ Return raw bytes if decoding fails
        return None


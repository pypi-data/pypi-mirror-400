from urllib.parse import urlparse

# from circles_local_database_python.generic_mapping import GenericMapping
from database_mysql_local.generic_mapping import GenericMapping
from logger_local.MetaLogger import Logger
from logger_local.LoggerComponentEnum import LoggerComponentEnum
import re
from typing import Optional

# TODO DOMAIN_LOCAL -> URL_REMOTE everywhere
DOMAIN_LOCAL_PYTHON_COMPONENT_ID = 5000004
DOMAIN_LOCAL_PYTHON_COMPONENT_NAME = "domain local"
DEVELOPER_EMAIL_ADDRESS = "sahar.g@circ.zone"

object1 = {
    "component_id": DOMAIN_LOCAL_PYTHON_COMPONENT_ID,
    "component_name": DOMAIN_LOCAL_PYTHON_COMPONENT_NAME,
    "component_category": LoggerComponentEnum.ComponentCategory.Code.value,
    "developer_email_address": DEVELOPER_EMAIL_ADDRESS,
}
logger = Logger.create_logger(object=object1)

# TODO Please mark all private methods as private using __


class DomainLocal(GenericMapping):
    """
    DomainLocal is a class that uses regular expressions to parse URLs and extract components.
    """

    def __init__(self):
        self.domain_regex = re.compile(r"^(?:http[s]?://)?(?:www\.)?([^:/\s]+)")
        self.organization_regex = re.compile(r"^(?:http[s]?://)?(?:www\.)?([^\.]+)\.")
        self.username_regex = re.compile(r"^http[s]?://(?:([^:/\s]+)@)?")
        self.tld_regex = re.compile(r"^(?:http[s]?://)?(?:www\.)?[^\.]+\.(.*)")

    def get_domain_name(self, url: str) -> Optional[str]:
        """
        Extracts the domain name from a URL.
        """
        if not self.valid_url(url):
            return None
        match = self.domain_regex.search(url)
        if match:
            return match.group(1)
        return None

    # TODO: test
    # TODO: is it used anywhere?
    def get_url_type(self, url: str) -> Optional[str]:
        """Example: get_url_type("https://www.google.com") -> "https" """
        # Extracts URL type from the URL
        if not self.valid_url(url):
            return None
        url_type = urlparse(url).scheme
        return url_type

    def get_organization_name(self, url: str) -> Optional[str]:
        """
        Extracts the organization name from a URL.
        """
        if not self.valid_url(url):
            return None
        match = self.organization_regex.search(url)
        if match:
            return match.group(1)
        return None

    def get_username(self, url: str) -> Optional[str]:
        """
        Extracts the username from a URL.
        """
        if not self.valid_url(url):
            return None
        match = self.username_regex.search(url)
        if match:
            return match.group(1)
        return None

    def get_tld(self, url: str) -> Optional[str]:
        """
        Extracts the top-level domain (TLD) from a URL.
        """
        if not self.valid_url(url):
            return None
        match = self.tld_regex.search(url)
        if match:
            return match.group(1)
        return None

    def valid_url(self, url: str) -> bool:
        """
        Validates the URL format.
        """
        return re.match(r"^http[s]?://", url) is not None

    def link_contact_to_domain(self, contact_id: int, url: str) -> dict:
        """
        Links a contact to a domain.
        Returns a dictionary containing the following information:
        - contact_id
        - url
        - profile_id
        - internet_domain_id
        - contact_internet_domain_id
        """
        logger.start(
            "link_contact_to_domain", object={"contact_id": contact_id, "url": url}
        )
        try:
            domain_name = self.get_domain_name(url)
            tld = self.get_tld(url)
            data_to_insert = {
                "domain_name": domain_name,
                "tld": tld,
                "profile_id": logger.user_context.get_effective_profile_id(),
            }
            self.set_schema(schema_name="internet_domain")
            internet_domain_id = self.insert(
                table_name="internet_domain_table", data_json=data_to_insert
            )
            self.set_schema(schema_name="contact_internet_domain")
            contact_internet_domain_id = self.insert_mapping(
                # TODO entity1 contact
                # TODO entity2 internet_domain
                entity_name1="contact_internet",
                entity_name2="domain",
                entity_id1=contact_id,
                entity_id2=internet_domain_id,
            )
        except Exception as e:
            logger.error(
                "link_contact_to_domain",
                object={"contact_id": contact_id, "url": url},
                data=e,
            )
            raise e
        insert_information = {
            "contact_id": contact_id,
            "url": url,
            "profile_id": logger.user_context.get_effective_profile_id(),
            "internet_domain_id": internet_domain_id,
            "contact_internet_domain_id": contact_internet_domain_id,
        }
        logger.end(
            "link_contact_to_domain",
            object={"contact_internet_domain_id": contact_internet_domain_id},
        )
        return insert_information

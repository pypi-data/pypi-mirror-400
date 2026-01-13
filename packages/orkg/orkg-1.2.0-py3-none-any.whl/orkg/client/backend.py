from typing import Optional, Union

import hammock
import requests
from requests import HTTPError
from requests.adapters import HTTPAdapter

from orkg.common import Hosts
from orkg.logging_config import initialize_logger
from orkg.out import OrkgResponse
from orkg.utils import check_authentication, follow_location_header, verb_logger
from orkg.version import __version__

from .classes import ClassesClient
from .comparisons import ComparisonsClient
from .contribution_comparisons import ContributionComparisonsClient
from .contributions import ContributionsClient
from .dummy import DummyClient
from .fields import ResearchFieldsClient
from .harvesters import HarvestersClient
from .json import JSONClient
from .lists import ListsClient
from .literals import LiteralsClient
from .objects import ObjectsClient
from .papers import PapersClient
from .predicates import PredicatesClient
from .problems import ResearchProblemsClient
from .resources import ResourcesClient
from .session import Session
from .snapshots import SnapshotsClient
from .statements import StatementsClient
from .stats import StatsClient
from .templates import TemplatesClient

hammock.Hammock.GET = verb_logger("GET")(hammock.Hammock.GET)
hammock.Hammock.POST = check_authentication(verb_logger("POST")(hammock.Hammock.POST))
hammock.Hammock.PUT = check_authentication(verb_logger("PUT")(hammock.Hammock.PUT))
hammock.Hammock.DELETE = check_authentication(
    verb_logger("DELETE")(hammock.Hammock.DELETE)
)
hammock.Hammock.PATCH = check_authentication(
    verb_logger("PATCH")(hammock.Hammock.PATCH)
)

DEFAULT_USER_AGENT = f"ORKG Python Client/{__version__}"


class TimeoutHTTPAdapter(HTTPAdapter):
    def __init__(self, timeout=None, *args, **kwargs):
        self.timeout = timeout
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        kwargs["timeout"] = kwargs.get("timeout") or self.timeout
        return super().send(request, **kwargs)


class ORKG(object):
    """
    The base class for the ORKG client.
    Contains all the methods to interact with the ORKG API.
    """

    host: Optional[Union[str, Hosts]] = None
    simcomp_host: Optional[str] = None
    session: Optional[Session] = None

    def __init__(
        self,
        host: Optional[Union[str, Hosts]] = None,
        auth_host: Optional[str] = "https://accounts.orkg.org",
        simcomp_host: Optional[str] = None,
        creds: Optional[tuple] = None,
        logging_level: Union[str, int] = "WARNING",
        follow_location: bool = True,
        timeout: Optional[float] = None,
        user_agent: Optional[str] = None,
        **kwargs,
    ):
        self._set_host(host)
        self._set_simcomp_host(simcomp_host)

        # Set timeout for hammock sessions
        timeout_adapter = TimeoutHTTPAdapter(timeout=timeout)
        session = requests.Session()
        session.mount("http://", timeout_adapter)
        session.mount("https://", timeout_adapter)

        # Set User-Agent header
        self.user_agent = user_agent or DEFAULT_USER_AGENT
        session.headers["User-Agent"] = self.user_agent

        self.core = hammock.Hammock(self.host, **kwargs)
        self.core._session = session
        if self.simcomp_available:
            self.simcomp = hammock.Hammock(self.simcomp_host, **kwargs)
            self.simcomp._session = session

        initialize_logger(logging_level)
        self.follow_location = follow_location
        if creds is not None and len(creds) == 2:
            self.session = Session(auth_host, creds[0], creds[1])
        else:
            self.session = None
        self.backend = self.core.api
        self.resources = ResourcesClient(self)
        self.predicates = PredicatesClient(self)
        self.classes = ClassesClient(self)
        self.lists = ListsClient(self)
        self.literals = LiteralsClient(self)
        self.stats = StatsClient(self)
        self.statements = StatementsClient(self)
        self.papers = PapersClient(self)
        self.comparisons = ComparisonsClient(self)
        self.contributions = ContributionsClient(self)
        self.objects = ObjectsClient(self)
        self.dummy = DummyClient(self)
        self.json = JSONClient(self)
        self.templates = TemplatesClient(self)
        self.contribution_comparisons = ContributionComparisonsClient(self)
        self.harvesters = HarvestersClient(self)
        self.problems = ResearchProblemsClient(self)
        self.fields = ResearchFieldsClient(self)
        self.snapshots = SnapshotsClient(self)

    @property
    def simcomp_available(self) -> bool:
        """
        Check whether the simcomp host is available or not
        :return: True if the simcomp host is available, False otherwise
        """
        return self.simcomp_host is not None

    def _set_host(self, host: Optional[Union[str, Hosts]]) -> None:
        """
        Set the host value of the backend
        :param host: the host passed by the user or None
        """
        if isinstance(host, Hosts):
            host = host.value
        if host is not None and not host.startswith("http"):
            if "host" not in host.lower():
                raise ValueError("host must begin with http or https")
            else:
                raise ValueError(
                    "the host name was not recognized "
                    "-- use Hosts.PRODUCTION, Hosts.SANDBOX, or Hosts.INCUBATING without quotes"
                )
        if host is not None and host[-1] == "/":
            host = host[:-1]
        self.host = host if host is not None else "https://sandbox.orkg.org"

    def _set_simcomp_host(self, simcomp_host: Optional[str]) -> None:
        """
        Set the simcomp host
        :param simcomp_host: the simcomp host passed by the user (optional)
        """
        if simcomp_host is not None and not simcomp_host.startswith("http"):
            raise ValueError("simcomp host must begin with http or https")
        if simcomp_host is None and "orkg" in self.host:
            simcomp_host = self.host + "/simcomp"
        self.simcomp_host = simcomp_host

    def ping(self) -> bool:
        """
        The ping function checks whether the backend is live or not.
        :returns: True if the backend is live, False otherwise
        """
        try:
            initial_response = requests.get(self.host, timeout=3, allow_redirects=True)
            initial_response.raise_for_status()
            return True
        except HTTPError:
            # TODO: log different status errors
            return False

    def expand_response(self, response):
        url: str = response.headers.get("Location")
        if self.follow_location:
            original_headers = (
                dict(response.request.headers) if hasattr(response, "request") else None
            )
            if original_headers is not None:
                original_headers = {
                    k: v
                    for k, v in original_headers.items()
                    if k in ["Authorization", "Content-Type", "Accept", "User-Agent"]
                }
            return self.wrap_response(
                follow_location_header(url, headers=original_headers)
            )
        else:
            return self.wrap_response(
                status_code=str(response.status_code), content={}, url=url
            )

    def wrap_response(
        self,
        response=None,
        status_code: str = None,
        content: Union[list, dict, str] = None,
        url: str = None,
    ) -> OrkgResponse:
        """
        Wraps the response from the backend into a OrkgResponse object
        :param response: the response from the backend
        :param status_code: the status code of the response
        :param content: the content of the response
        :param url: the url of the response
        :return: OrkgResponse object
        """
        return OrkgResponse(
            client=self,
            response=response,
            status_code=status_code,
            content=content,
            url=url,
        )

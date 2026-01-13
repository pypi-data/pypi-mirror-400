"""
Keywords, helper classes and helper functions for the Robot Framework Relukko
package.
"""
from datetime import datetime
from typing import List, Union

from pyrelukko import RelukkoClient, RelukkoDTO
from robot.api import SkipExecution, logger
from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn
from robot.utils.robottime import timestr_to_secs


class Relukko:
    """
    Robot Framework keywords to acquire locks from a
    [https://gitlab.com/relukko/relukko|Relukko backend].

    == Table of contents ==
    %TOC%

    = Example Usage =
    The library can be configured at initializing time or later with the
    keyword `Setup Relukko`.

    Example set up:
    | ***** Settings *****
    | Library    Relukko    creator=Demo Creator
    |
    |
    | ***** Test Cases *****
    | Test Resource Lock
    |     [Tags]    test_case_id:eb3a4185-185b-4ac6-a63d-5d1f20e55134
    |     Set Up Relukko    http://localhost:3000    some-api-key
    |     Acquire Relukko For Test

    = Kwargs =
    The keywords `Importing` and `Setup Relukko` pass through the ``kwargs``
    to underlying libraries, following a non-exhaustive selection of kwargs
    which are passed further.

    | =kwarg=                     | =used in=                | =Comments=     |
    | check_hostname              | SSLContext               | (1)            |
    | hostname_checks_common_name | SSLContext               | (1)            |
    | verify_mode                 | SSLContext               | (1)            |
    | verify_flags                | SSLContext               | (1)            |
    | options                     | SSLContext               | (1)            |
    | cafile                      | SSLContext               | (1), (5), (10) |
    | capath                      | SSLContext               | (1), (5), (10) |
    | cadata                      | SSLContext               | (1), (5), (10) |
    | tries                       | pyrelukko.retry          | (2) |
    | delay                       | pyrelukko.retry          | (2) |
    | backoff                     | pyrelukko.retry          | (2) |
    | max_delay                   | pyrelukko.retry          | (2) |
    | exceptions                  | pyrelukko.retry          | (2) |
    | total                       | urllib3.util.Retry       | (3) |
    | connect                     | urllib3.util.Retry       | (3) |
    | read                        | urllib3.util.Retry       | (3) |
    | redirect                    | urllib3.util.Retry       | (3) |
    | status                      | urllib3.util.Retry       | (3) |
    | other                       | urllib3.util.Retry       | (3) |
    | backoff_factor              | urllib3.util.Retry       | (3) |
    | backoff_max                 | urllib3.util.Retry       | (3) |
    | backoff_jitter              | urllib3.util.Retry       | (3) |
    | raise_on_redirect           | urllib3.util.Retry       | (3) |
    | raise_on_status             | urllib3.util.Retry       | (3) |
    | headers                     | requests.Session         | (4), (7) |
    | cookies                     | requests.Session         | (4) |
    | auth                        | requests.Session         | (4) |
    | proxies                     | requests.Session         | (4), (6) |
    | hooks                       | requests.Session         | (4) |
    | params                      | requests.Session         | (4) |
    | verify                      | requests.Session         | (4), (9), (10) |
    | cert                        | requests.Session         | (4), (9), (10) |
    | adapters                    | requests.Session         | (4), (8) |
    | stream                      | requests.Session         | (4) |
    | trust_env                   | requests.Session         | (4), (6) |
    | max_redirects               | requests.Session         | (4) |
    | acquire_wait_for_timeout    | pyrelukko.relukko_client |     |
    | acquire_modulo              | pyrelukko.relukko_client |     |
    | disable_websocket           | pyrelukko.relukko_client |     |
    | raise_when_acquire_fails    | pyrelukko.relukko_client | (11) |
    | ws_ping_interval            | pyrelukko.relukko_client |     |
    | ws_ping_timeout             | pyrelukko.relukko_client |     |
    | ws_wait_for_timeout         | pyrelukko.relukko_client |     |

    - *(1)* TLS settings only used for the WebSockets, not for the HTTP
      requests! See:
      [https://docs.python.org/3/library/ssl.html#ssl.SSLContext|SSLContext]
    - *(2)* See:
      [https://gitlab.com/relukko/pyrelukko/-/blob/master/src/pyrelukko/retry.py?ref_type=heads#L9|Retry]
    - *(3)* See:
      [https://urllib3.readthedocs.io/en/stable/reference/urllib3.util.html#urllib3.util.Retry|urllib3.util.Retry]
    - *(4)* See:
      [https://docs.python-requests.org/en/latest/api/#request-sessions|Request Sessions]
    - *(5)* Used in:
      [https://docs.python.org/3/library/ssl.html#ssl.SSLContext.load_verify_locations|load_verify_locations]
    - *(6)* Proxies only work for the HTTP requests! But not for the
      WebSockets used to monitor for deletions! So will probably not work as
      expected.
    - *(7)* This overwrites the header entry set for the API-KEY! Ensure to add
      it yourself (``X-api-Key``)!
    - *(8)* Interferes with the "Retry" from ``urllib3``!
    - *(9)* TLS settings only used for the HTTP requests, not for the
      WebSockets!
    - *(10)* Also takes the environment variables ``REQUESTS_CA_BUNDLE`` or
      ``CURL_CA_BUNDLE`` into account! But the arguments take precedence over
      the environment variables. For HTTP requests use of the variables see
      [https://requests.readthedocs.io/en/stable/user/advanced/#ssl-cert-verification|SSL Cert Verification].
      The behavior for the WebSockets should be the same.
    - *(11)* Do not change! It will break things.

    = Relukko Data Transfer Object =
    DTO of a "Relukko" lock:
    | {
    |   "id": "950daa20-a814-451e-9407-ec496cf9c136",
    |   "lock_name": "eb3a4185-185b-4ac6-a63d-5d1f20e55134",
    |   "creator": "Demo Creator",
    |   "ip": "10.89.0.6",
    |   "expires_at": "2024-10-31T20:14:43.9313Z",
    |   "created_at": "2024-10-31T20:04:43.9313Z",
    |   "updated_at": "2024-10-31T20:04:43.9313Z"
    | }

    = Skip locking =
    During development it might be that you need the resource for your self and
    don't want other test runs to interfere, so you don't have to wait to get
    lock. You can do the following:

    - Create the needed lock (or locks) by hand from the Web UI.
    - Set the expire time far in the future.
    - Set the environment variable ``RELUKKO_TRUST_ME_IT_IS_LOCKED`` to an
      value, e.g. ``yes``.
    - Start your coding session with debug runs.
    - Once you are done, unset the environment variable and delete the lock
      from the Web UI.
    """
    # pylint: disable=too-many-instance-attributes
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(
            self, base_url: str="", api_key: str="",
            creator: str=None, **kwargs):
        """
        ``base_url`` The URL of the Relukko back end (without ``/v1/locks``).

        ``api_key`` The API Key to do the HTTP REST calls.

        ``creator`` An optional name of the creator of the lock, only for
                    information.

        ``**kwargs`` The kwargs are passed to various underlying libraries to
                     fine tune their configuration. For details see `Kwargs`.
        """

        self.client = RelukkoClient(
            base_url=base_url, api_key=api_key,
            raise_when_acquire_fails=False,
            **kwargs)

        self.creator: str = creator
        self.builtin = BuiltIn()

        # Forward declaration will be filled later
        self.lock: RelukkoDTO = None
        self.lock_id: str = None

    def set_up_relukko(
            self, base_url: str=None, api_key: str=None,
            creator: str=None, **kwargs):
        """
        It might not be possible to configure everything already when the
        library is imported. This keyword allows to finish the configuration.

        Arguments given to this keyword take precedence of already configured
        values during import!

        ``base_url`` The URL of the Relukko back end (without
                     ``/v1/locks``).

        ``api_key`` The API Key to do the HTTP REST calls.

        ``creator`` An optional name of the creator of the lock, only for
                    information.

        ``**kwargs`` The kwargs are passed to various underlying libraries to
                     fine tune their configuration. For details see `Kwargs`.
        """
        self.client.reconfigure_relukko(
            base_url = base_url or self.client.base_url,
            api_key = api_key or self.client.api_key,
            raise_when_acquire_fails=False,
            **kwargs
        )

        self.creator = creator or self.creator

    def acquire_relukko(
            self,
            lock_name: str,
            max_wait_time: str="600s",
            creator: str=None,
        ) -> Union[RelukkoDTO, None]:
        """
        Create (acquire) a lock from the Relukko back end. If the ``lock_name``
        already exists in the Relukko back end, then it blocks the execution
        until it gets the lock or gives up.

        ``lock_name`` The name of the lock that shall be acquired.

        ``max_runtime`` The amount of time to wait maximal to acquire the lock,
                        default: 600 seconds.

        The ``max_wait_time`` must follow Robot Framework's
        [https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#time-format|Time Format].

        ``creator`` An optional name of the creator of the lock, only for
                    information. If omitted the value set during library
                    configuration (see: `Importing` or `Setup Relukko`) is used.

        Example:
        | Acquire Relukko   LockName    CreatorName    1h34m13s

        Returns the created DTO of the lock (RelukkoDTO).
        """

        max_run_time = timestr_to_secs(max_wait_time)
        logger.info("\nStart acquiring Relukko... "
                    f"waiting for maximal {max_run_time}s [{max_wait_time}]\n",
                    also_console=True)
        self.lock = self.client.acquire_relukko(
            lock_name=lock_name,
            creator=creator or self.creator,
            max_run_time=max_run_time)

        if self.lock is not None and isinstance(self.lock, RelukkoDTO):
            self.lock_id = self.lock.id
            logger.info(f"Relukko created: {self.lock}")
            return self.lock

        raise SkipExecution("Could not acquire lock")


    def keep_relukko_alive_for_the_next_5_min(self) -> Union[RelukkoDTO, None]:
        """
        Keeps the current Relukko lock alive by setting the expires at time to
        5 minutes from _now_ into the future.

        Returns the updated DTO of the lock (RelukkoDTO).
        """
        self.lock = self.client.keep_relukko_alive(self.lock_id)
        logger.info(f"Relukko kept alive: {self.lock}")
        return self.lock

    @keyword(
        name='Keep Relukko Alive For The Next "${seconds}" Seconds',
        types=[int])
    def keep_relukko_alive_for_x_seconds(
        self, seconds: int) -> Union[RelukkoDTO, None]:
        """
        Keeps the current Relukko lock alive by setting the expires at time to
        the amount of seconds provided from _now_ into the future.

        ``seconds`` The amount of seconds to at to from now.

        Returns the updated DTO of the lock (RelukkoDTO).
        """
        self.lock = self.client.keep_relukko_alive_put(self.lock_id, seconds)
        logger.info(f"Relukko kept alive: {self.lock}")
        return self.lock

    def keep_relukko_alive_for_the_next(
            self, timestr: str) -> Union[RelukkoDTO, None]:
        """
        Keeps the current Relukko lock alive by setting the expires at time to
        the amount of time provided in the ``timestr`` from _now_ into the future.

        The ``timestr`` must follow Robot Framework's
        [https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#time-format|Time Format].

        Example:
        | Keep Relukko Alive For The Next    1h34m13s

        ``timestr`` The amount of time to set the expires at time into the
                    future.

        Returns the updated DTO of the lock (RelukkoDTO).
        """
        return self.keep_relukko_alive_for_x_seconds(
            timestr_to_secs(timestr=timestr))

    def add_to_current_relukko_expire_at_time_5_min(
            self) -> Union[RelukkoDTO, None]:
        """
        Keeps the current Relukko lock alive by adding 5 minutes to the
        current expires at time.

        Returns the updated DTO of the lock (RelukkoDTO).
        """
        self.lock = self.client.add_to_expires_at_time(self.lock_id)
        logger.info(f"Time added to Relukko expires at: {self.lock}")
        return self.lock

    @keyword(
        name='Add To Current Relukko Expire At Time "${seconds}" Seconds',
        types=[int])
    def add_to_current_relukko_expire_time_x_seconds(
        self, seconds: int) -> Union[RelukkoDTO, None]:
        """
        Keeps the current Relukko lock alive by adding the provided amount of
        seconds to the current expires at time.

        ``seconds`` The amount of seconds to at to the current expires at time.

        Returns the updated DTO of the lock (RelukkoDTO).
        """
        self.lock = self.client.add_to_expires_at_time_put(
            self.lock_id, seconds)
        logger.info(f"Time added to Relukko expires at: {self.lock}")
        return self.lock

    def add_to_current_relukko_expire_at_time(
            self, timestr: str) -> Union[RelukkoDTO, None]:
        """
        Keeps the current Relukko lock alive by adding the amount of time
        provided in the ``timestr`` to the current expires at time.

        The ``timestr`` must follow Robot Framework's
        [https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#time-format|Time Format].

        Example:
        | Add To Current Relukko Expire At Time    1h34m13s

        Returns the updated DTO of the lock (RelukkoDTO)
        """
        return self.add_to_current_relukko_expire_time_x_seconds(
            timestr_to_secs(timestr=timestr))

    def update_relukko(
            self,
            creator: str=None,
            expires_at: Union[str, datetime]=None) -> Union[RelukkoDTO, None]:
        """
        Allows to change the "creator" of the lock and/or the expires at time
        to any time.

        ``creator`` An name to set as the creator of the lock, if omitted the
                    value does not change in the Relukko back end.

        ``expires_at`` The new to set expires at time either as string in the
                       RFC3339 format (``YYYY-MM-DDThh:mm:ss.ssssssZ``) or as
                       datetime object, if omitted the value does not change
                       in the Relukko back end.

        Returns the updated DTO of the lock (RelukkoDTO).
        """
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)

        self.lock = self.client.update_relukko(
            self.lock_id, creator=creator, expires_at=expires_at)

        logger.info(f"Relukko updated: {self.lock}")
        return self.lock

    def delete_relukko(self) -> Union[RelukkoDTO, None]:
        """
        Deletes the Relukko lock from the back end.

        Returns the deleted DTO of the lock (RelukkoDTO).
        """
        lock = self.client.delete_relukko(self.lock_id)
        self.lock = None
        self.lock_id = None
        logger.info(f"Relukko deleted: {lock}")
        return lock

    def get_current_relukko(
            self, refresh: bool=False) -> Union[RelukkoDTO, None]:
        """
        If ``refresh`` is ``True`` it fetches an up to date version of the
        Relukko DTO from the back end and returns it. Otherwise by default
        it returns the stored Relukko lock DTO.

        ``refresh`` Shall the Relukko DTO be fetched from the Relukko back end.

        Returns the current DTO of the lock (RelukkoDTO)
        """
        if refresh:
            self.lock = self.client.get_lock(self.lock_id)
        logger.info(self.lock)
        return self.lock

    def get_relukko_expires_at_time(self, refresh: bool=False) -> datetime:
        """
        If ``refresh`` is ``True`` it fetches an up to date version of the
        Relukko DTO from the back end. Otherwise by default it returns the
        stored expires at as ``datetime`` object.

        ``refresh`` Shall the Relukko DTO be fetched from the Relukko back end.

        Returns the expires at time as ``datetime``
        """
        if refresh or self.lock is None:
            self.lock = self.client.get_lock(self.lock_id)

        logger.info(self.lock.expires_at)
        return self.lock.expires_at

    def get_relukko_created_at_time(self, refresh: bool=False) -> datetime:
        """
        If ``refresh`` is ``True`` it fetches an up to date version of the
        Relukko DTO from the back end. Otherwise by default it returns the
        stored updated at as ``datetime`` object.

        ``refresh`` Shall the Relukko DTO be fetched from the Relukko back end.

        Returns the created at time as ``datetime``
        """
        if refresh or self.lock is None:
            self.lock = self.client.get_lock(self.lock_id)

        logger.info(self.lock.created_at)
        return self.lock.created_at

    def acquire_relukko_for_test(self) -> Union[RelukkoDTO, None]:
        """
        Create (acquire) a lock from the Relukko back end. The ``lock_name``
        is derived either from the tag that starts with ``test_case_id:`` or if
        no such tag is found from the suite and test case name. For the
        ``creator`` the configured value is used (see: `Importing` or
        `Setup Relukko`).

        If derived from ``test_case_id`` tag only the part after the `:` (colon)
        is used, from the tag:
        ```test_case_id:81f2c642-ddaf-400d-9f6b-4b1c89ef9732`` the resulting
        lock name will be: ``81f2c642-ddaf-400d-9f6b-4b1c89ef9732``.

        If derived from suite name and test case, the lock name will be:
        ``f"{suite_name}:{test_name}"``

        Returns the created DTO of the lock (RelukkoDTO)
        """
        test_tags = self.builtin.get_variable_value("@{TEST TAGS}")
        test_case_id_tag = [
            x for x in test_tags if x.startswith('test_case_id:')]
        if test_case_id_tag:
            lock_name = test_case_id_tag[0][13:]
        else:
            test_name = self.builtin.get_variable_value("${TEST NAME}")
            suite_name = self.builtin.get_variable_value("${SUITE NAME}")
            lock_name = f"{suite_name}:{test_name}"

        logger.info(f"Derived lock name: {lock_name}")
        return self.acquire_relukko(lock_name=lock_name)

    def get_all_relukkos(self) -> List[RelukkoDTO]:
        """
        Returns a list of current Relukkos (locks) (RelukkoDTO) in the back-end
        """
        return self.client.get_locks()

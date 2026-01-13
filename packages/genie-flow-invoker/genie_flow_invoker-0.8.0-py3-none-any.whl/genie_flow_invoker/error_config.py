from dataclasses import dataclass
from typing import TypedDict, Optional, List, Type

from genie_flow_invoker.class_utils import get_class_from_fully_qualified_name


class OnErrorConfig(TypedDict):
    event: Optional[str]
    content: Optional[str]


@dataclass
class OnErrorSpecs(object):
    event: Optional[str]
    content: Optional[str]

    @classmethod
    def from_config(cls, config: str | OnErrorConfig) -> "OnErrorSpecs":
        if isinstance(config, str):
            return cls(event=None, content=config)
        else:
            return cls(
                event=config.get("event"),
                content=config.get("content", None),
            )


class RetryConfig(TypedDict):
    autoretry_for: Optional[List[str]]
    max_retries: Optional[int]
    retry_backoff: Optional[bool | float]
    retry_backoff_max: Optional[float]
    retry_jitter: Optional[float]


@dataclass
class RetrySpecs(object):
    """
    Dataclass that contains the following keys:
    * `autoretry_for`: a list of exception classes to trigger a retry for
    * `max_retries`: the maximum number of times the invoker will be retried for
    * `retry_backoff`: a boolean or float specifying if an exponential backoff should be
                       applied with base 1 second (boolean) or the given base number of
                       seconds.
    * `retry_backoff_max`: the max number of seconds to backoff.
    * `retry_jitter`: a boolean to specify if a random number must be subtract from the backoff
    """

    autoretry_for: Optional[List[Type[Exception]]] = None
    max_retries: Optional[int] = None
    retry_backoff: Optional[bool | float] = None
    retry_backoff_max: Optional[float] = None
    retry_jitter: Optional[float] = None

    @classmethod
    def from_config(cls, config: RetryConfig) -> "RetrySpecs":
        exceptions: List[Type[Exception]] = []
        for retry_fqn in config.get("autoretry_for", []):
            retry_exception = get_class_from_fully_qualified_name(retry_fqn)
            if not issubclass(retry_exception, Exception):
                raise ValueError(
                    f"The class {retry_fqn} is not a subclass of {Exception.__class__}"
                )
            exceptions.append(retry_exception)

        return cls(
            autoretry_for=exceptions,
            max_retries=config.get("max_retries", None),
            retry_backoff=config.get("retry_backoff", None),
            retry_backoff_max=config.get("retry_backoff_max", None),
            retry_jitter=config.get("retry_jitter", None),
        )

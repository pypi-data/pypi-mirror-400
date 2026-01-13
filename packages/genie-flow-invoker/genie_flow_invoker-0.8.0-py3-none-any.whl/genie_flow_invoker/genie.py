from abc import ABC, abstractmethod
from typing import Optional

from genie_flow_invoker.error_config import (
    OnErrorConfig,
    RetryConfig,
    RetrySpecs,
    OnErrorSpecs,
)


class GenieInvoker(ABC):
    """
    The super class of all Genie Invokers. The standard interface to invoke large language models,
    database retrievals, etc.

    This is an abstraction around calls that take a text content and pass that to a lower level
    service for processing. The returned value is always a result string.

    This class is subclassed with specific classes for external services.
    """

    _on_error_specs: Optional[OnErrorSpecs] = None
    _retry_specs: Optional[RetrySpecs] = None

    @classmethod
    def from_config_with_error_handling(
        cls,
        config: dict,
        on_error: Optional[str | OnErrorConfig],
        retry: Optional[RetryConfig],
    ):
        """
        Create a new instance of the invoker with optional error handling and retry configs.
        The configs are set on the resulting invoker after the `from_config` method is used
        to create an instance.

        `on_error` can be either a string or a dictionary. If it is a string, then it will
        be used as a template to render the result when the invoker errors out. If a dict,
        then it needs to have a key 'event' for the event to be sent when the invoker errors
        out. That dict can optionally have a 'content' key that will be a template that is
        rendered as parameter to the sending that event.

        `retry` is an optional `RetryConfig` with the appropriate properties

        :param config: the configuration dictionary for the invoker
        :param on_error: optionally, either a string or a dictionary
        :param retry: an optional dictionary
        :return: a new instance of the invoker
        """
        invoker = cls.from_config(config)

        if on_error is not None:
            invoker._on_error_specs = OnErrorSpecs.from_config(on_error)
        if retry is not None:
            invoker._retry_specs = RetrySpecs.from_config(retry)

        return invoker

    @classmethod
    @abstractmethod
    def from_config(cls, config: dict):
        raise NotImplementedError()

    @abstractmethod
    def invoke(self, content: str) -> str:
        """
        Invoke the underlying service with the supplied content and dialogue.

        :param content: The text content to invoke the underlying service. The format of
        this string is Invoker dependent. Some may simply expect a string, others may
        need to get a structured document as string - for instance a JSON string - that
        incorporates the values that one needs to pass.
        :return: The result string.
        """
        raise NotImplementedError()

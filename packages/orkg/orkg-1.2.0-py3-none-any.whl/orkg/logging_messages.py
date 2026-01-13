from typing import Callable, Dict, List, Optional, Tuple, Union


class MessageBuilder:
    @staticmethod
    def method_call(attr: Callable, method_name: str, args: Tuple, kwargs: Dict) -> str:
        """
        Returns message for logging a call to a method (with module path) and arguments passed to it

        :param attr: method object
        :param method_name: name of method
        :param args: the positional arguments passed to the method
        :param kwargs: the keyword arguments passed to the method
        :return: logging message
        """
        arg_str = MessageBuilder._format_args(args, kwargs)
        func = (
            f"{attr.__module__}.{method_name}"
            if hasattr(attr, "__module__")
            else f"{method_name}"
        )
        return f"Calling: {func}({arg_str})"

    @staticmethod
    def execution_complete(attr: Callable, method_name: str) -> str:
        """
        Returns message for logging that a method has finished executing

        :param attr: method object
        :param method_name: name of method
        """
        func = (
            f"{attr.__module__}.{method_name}"
            if hasattr(attr, "__module__")
            else f"{method_name}"
        )
        return f"Execution complete: {func}"

    @staticmethod
    def api_call_simple(verb: str, args: Tuple) -> str:
        """
        Returns message for logging API calls

        :param verb: the HTTP method
        :param args: url and parameters for the api request
        :return: logging message
        """
        return f"API-{verb} {'/'.join([str(param) for param in args])}"

    @staticmethod
    def api_call_with_request_body(verb: str, args: Tuple, kwargs: Dict) -> str:
        """
        Returns message for logging API calls

        :param verb: the HTTP method
        :param args: url and parameters for the api request
        :param kwargs: body of the request
        :return: logging message
        """
        return f"API-{verb} {'/'.join([str(param) for param in args])} body: {kwargs if 'json' not in kwargs else kwargs['json']}"

    @staticmethod
    def backend_response(
        content: Union[Dict, List], status_code: Union[int, str], url: Optional[str]
    ) -> str:
        """
        Returns message for logging the response from the backend
        """
        size = len(content) if type(content) is list else 1
        content = content[0:5] if type(content) is list else content
        return f"Backend response - status code: {status_code}, content length: {size}, content (max 5 objects): {content}, url: {url}"

    @staticmethod
    def backend_response_none() -> str:
        return "No response from backend!"

    @staticmethod
    def deprecation_warning(feature: str) -> str:
        """
        Returns message for logging usage of a deprecated feature

        :param feature: parameter/method/variable/etc. which is deprecated
        :return: logging message
        """
        return f"Deprecated feature usage: {feature}"

    @staticmethod
    def _format_args(args: Tuple[Union[str, Dict, Callable]], kwargs: Dict) -> str:
        """
        Concatenates positional and keyword arguments into a single string

        :param args: the positional arguments passed to the method
        :param kwargs: the keyword arguments passed to the method
        :return: string of all arguments
        """
        arg_str = ""
        if args:
            if isinstance(args[0], str):
                arg_str += ", ".join([str(a) for a in args])
            elif isinstance(args[0], dict):
                arg_str += MessageBuilder._stringify_dict(arg_str, args[0])
            elif callable(args[0]):
                arg_str += f"{args[0].__module__}.{args[0].__name__}"
            else:
                print("args type:", type(args[0]))
        if kwargs:
            arg_str = MessageBuilder._stringify_dict(arg_str, kwargs)
        return arg_str

    @staticmethod
    def _stringify_dict(string: str, dict_: Dict) -> str:
        """
        Converts dict into string formatted as 'key1 = val1, key2 = val2'
        """
        for k, v in dict_.items():
            if string:
                string += f", {k} = {v}"
            else:
                string += f"{k} = {v}"
        return string

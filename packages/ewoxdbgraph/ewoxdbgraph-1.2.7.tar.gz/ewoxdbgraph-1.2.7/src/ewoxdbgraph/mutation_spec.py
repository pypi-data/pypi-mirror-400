from typing import Any, Callable, Generic, List, Dict, Text, Optional, Tuple, Union, TypeVar, Type, cast

class MutationSpec:
    def __init__(self, mutation:str, params:dict[str, Any]) -> None:
        """ Specification for a database mutation operation.
        :param mutation: The mutation query string.
        :param params: A dictionary of parameters for the mutation.
        """
        self.mutation:str = mutation
        self.params:dict[str, Any] = params

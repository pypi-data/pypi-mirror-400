from typing import Any, Callable, Generic, List, Dict, Text, Optional, Tuple, Union, TypeVar, Type, cast
from neo4j import AsyncManagedTransaction, AsyncResult, AsyncSession
from ewoxcore.client.paging_args import PagingArgs
from ewoxcore.utils.json_util import JsonUtil
from ewoxcore.utils.string_util import StringUtil
from ewoxcore.utils.number_util import NumberUtil
from ewoxcore.utils.dictionary_util import DictionaryUtil
from ewoxcore.utils.boolean_util import BooleanUtil
from ewoxcore.client.paging_model import PagingModel
from ewoxdbgraph.mutation_spec import MutationSpec

T = TypeVar('T')

class RepositoryBase:
    """
    Base class for repositories.    
    This class provides a base class for all repositories.
    """
    def __init__(self, cypher_path:str) -> None:
        """
        Initialize the repository with the path to the Cypher queries.
        :param cypher_path: Path to the directory containing Cypher query files.
        """
        if not cypher_path:
            raise ValueError("Cypher path cannot be empty.")

        self._cypher_path:str = cypher_path


    def get_query(self, file_name: str) -> str:
        """
        Load a Cypher query from a file.
        :param path: Path to the directory containing repository file.
        :param file_name: Name to the Cypher query file.
        :return: The Cypher query as a string.
        """
        with open(self._cypher_path + "/queries/" + file_name, "r") as file:
            return file.read()


    def get_mutation(self, file_name: str) -> str:
        """
        Load a Cypher query from a file.
        :param file_name: Name to the Cypher query file.
        :return: The Cypher query as a string.
        """
        with open(self._cypher_path + "/mutations/" + file_name, "r") as file:
            return file.read()


    async def get_items(self,
        session:AsyncSession,
        query:str,
        params: dict[str, Any],
        model_class: Optional[Type[T]] = None,
        result_name:str = "result"
    ) -> list[T]:
        """ Retrieve items from the database using a Cypher query.
        :param session: The database session to use.
        :param query: The Cypher query to execute. 
        :param params: The parameters to pass to the query.
        :param model_class: The class to use for mapping the results.
        :param result_name: The name of the result field in the query.
        :return: A list of items mapped to the specified model class.
        """
        records = await session.execute_read(self._get_items, params, query=query, result_name=result_name)
        if (records is None or len(records) == 0):
            return []

        if (model_class is None):
            return records

        return [model_class(record) for record in records]


    async def _get_items(self, tx:AsyncManagedTransaction, params:dict[str, Any], query:str, result_name:str) -> list[dict[str, Any]]:
        result: AsyncResult = await tx.run(query=query, parameters=params)
        records = await result.data()
        if not records:
            return []

        items:list[dict[str, Any]] = []
        for record in records:
            item:dict[str, Any] = record[result_name]
            items.append(item)

        return items


    async def get_item(self,
        session:AsyncSession,
        query:str,
        params: dict[str, Any],
        model_class: Type[T],
        result_name:str = "result"
    ) -> Optional[T]:
        """ Retrieve items from the database using a Cypher query.
        :param session: The database session to use.
        :param query: The Cypher query to execute. 
        :param params: The parameters to pass to the query.
        :param model_class: The class to use for mapping the results.
        :param result_name: The name of the result field in the query.
        :return: An item mapped to the specified model class.
        """
        records = await session.execute_read(self._get_item, params, query=query, result_name=result_name)
        if not records:
            return None
       
        item:T = model_class(records[0])

        return item


    async def _get_singular_value(self,
        session:AsyncSession,
        query:str,
        params: dict[str, Any],
        result_name:str = "result"
    ) -> Any:
        records = await session.execute_read(self._get_item, params, query=query, result_name=result_name)
        if not records:
            return None

        result:Any = records[0]

        return result


    async def get_singular_string(self,
        session:AsyncSession,
        query:str,
        params: dict[str, Any],
        result_name:str = "result"
    ) -> str:
        """ Get a singular string value from the database. 
        :param session: The database session to use.
        :param query: The Cypher query to execute. 
        :param params: The parameters to pass to the query.
        :param result_name: The name of the result field in the query.
        :return: The string value.
        """
        value:Any = await self._get_singular_value(session, query, params, result_name)
        result:str = StringUtil.get_safe_string(value)

        return result


    async def get_singular_int(self,
        session:AsyncSession,
        query:str,
        params: dict[str, Any],
        result_name:str = "result"
    ) -> int:
        """ Get a singular integer value from the database. 
        :param session: The database session to use.
        :param query: The Cypher query to execute. 
        :param params: The parameters to pass to the query.
        :param result_name: The name of the result field in the query.
        :return: The integer value.
        """
        value:Any = await self._get_singular_value(session, query, params, result_name)
        result:int = NumberUtil.get_safe_int(value)

        return result


    async def get_singular_float(self,
        session:AsyncSession,
        query:str,
        params: dict[str, Any],
        result_name:str = "result"
    ) -> float:
        """ Get a singular float value from the database. 
        :param session: The database session to use.
        :param query: The Cypher query to execute. 
        :param params: The parameters to pass to the query.
        :param result_name: The name of the result field in the query.
        :return: The float value.
        """
        value:Any = await self._get_singular_value(session, query, params, result_name)
        result:float = NumberUtil.get_safe_float(value)

        return result


    async def get_paging_item(self,
        session:AsyncSession,
        query:str,
        args:PagingArgs,
        params: dict[str, Any],
        model_class: type[T],
        factory:Callable[[Any], T] = None,
        result_name:str = "result"
    ) -> Optional[PagingModel[T]]:
        """ Retrieve items from the database using a Cypher query.
        :param session: The database session to use.
        :param query: The Cypher query to execute. 
        :param params: The parameters to pass to the query.
        :param model_class: The class to use for mapping the results.
        :param result_name: The name of the result field in the query.
        :return: A paging model mapped to the specified model class.
        """
        args_params:dict[str, Any] = args.to_dict()
        args_params.update(params)

        records = await session.execute_read(self._get_item, args_params, query=query, result_name=result_name)
        if not records:
            return None

        factory = factory if (factory is not None) else model_class
        item:PagingModel[T] = PagingModel[T](records[0], item_factory=factory)
        item.skip = args.skip + args.num
        item.num = args.num

        return item


    async def _get_item(self, tx:AsyncManagedTransaction, params:dict[str, Any], query:str, result_name:str) -> Any:
        result: AsyncResult = await tx.run(query=query, parameters=params)
        record = await result.single()

        return record


    async def save_item(self, 
        session:AsyncSession, 
        mutation:str,
        model: T
    ) -> bool:
        """ Save an item to the database using a Cypher mutation.
        :param session: The database session to use.
        :param mutation: The Cypher mutation to execute.
        :param model: The model instance to save.
        :return: True if the save was successful."""
        try:
            entity:dict[str, Any] = DictionaryUtil.to_dict(model)
            result:bool = await session.execute_write(self._save_item, entity, mutation=mutation)
            return result
        except Exception as e:
            print(f"Error: {e}")
            raise
        

    async def save_entity(self, 
        session:AsyncSession, 
        mutation:str,
        entity:dict[str, Any]
    ) -> bool:
        """ Save an entity to the database using a Cypher mutation.
        :param session: The database session to use.
        :param mutation: The Cypher mutation to execute.
        :param entity: The entity dictionary to save.
        :return: True if the save was successful."""
        try:
            result:bool = await session.execute_write(self._save_item, entity, mutation=mutation)
            return result
        except Exception as e:
            print(f"Error: {e}")
            raise


    async def _save_item(self, tx:AsyncManagedTransaction, params:dict[str, Any], mutation:str) -> bool:
        result: AsyncResult = await tx.run(query=mutation, parameters=params)
        record = await result.single()
        if not record:
            return False
 
        return True


    async def exists_item(self,
        session:AsyncSession,
        query:str,
        params: dict[str, Any],
        result_name:str = "result"
    ) -> bool:
        """ Check if an item exists in the database using a Cypher query.
        :param session: The database session to use.
        :param query: The Cypher query to execute.
        :param params: The parameters to pass to the query.
        :param result_name: The name of the result field in the query.
        :return: True if the item exists."""
        records = await session.execute_read(self._get_item, params, query=query, result_name=result_name)
        if not records:
            return None
        
        result:bool = BooleanUtil.get_safe_bool(records[0])       

        return result


    async def execute_write_entity(self, 
        session:AsyncSession, 
        mutation:str,
        entity:dict[str, Any]
    ) -> bool:
        """ Execute a write mutation with the given entity.
        :param session: The database session to use.
        :param mutation: The Cypher mutation to execute.
        :param entity: The entity dictionary to use as parameters.
        :return: True if the mutation was successful."""
        try:
            result:bool = await session.execute_write(self._save_item, entity, mutation=mutation)
            return result
        except Exception as e:
            print(f"Error: {e}")
            raise


    async def save_entities(self, 
        session:AsyncSession, 
        mutations:list[MutationSpec]
    ) -> bool:
        """ Save multiple entities to the database using Cypher mutations. 
        :param session: The database session to use.
        :param mutations: A list of MutationSpec objects containing the mutation queries and parameters.
        :return: True if all mutations were successful."""
        try:
            result:bool = await session.execute_write(self._save_items, list(mutations))
            return result
        except Exception as e:
            print(f"Error: {e}")
            raise


    async def _save_items(self, tx:AsyncManagedTransaction, mutations:list[MutationSpec]) -> bool:
        for i, m in enumerate(mutations, start=1):
            result: AsyncResult = await tx.run(m.mutation, parameters=m.params)

            record = await result.single()
            if not record:
                raise Exception(f"Mutation {i} returned no record / did not match")
 
        return True

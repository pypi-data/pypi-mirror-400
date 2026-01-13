from typing import cast, Any, Literal, ClassVar, Generator, get_origin, get_args

import logging
logger = logging.getLogger(__name__)

import io
import re

from time import sleep
import pandas as pd

from collections.abc import Mapping
from dataclasses import dataclass, field

from pathlib import Path

from inspect import getmembers

from joblib import Parallel, delayed

from turbodbc.options import Options
from turbodbc import Megabytes
from turbodbc.connection import Connection
from turbodbc.cursor import Cursor
from turbodbc import connect, make_options
from turbodbc.exceptions import InterfaceError, DatabaseError




def is_property(x):
    return isinstance(x, config_property)


class config_property(property):
    def __set__(self, __instance: Any, __value: Any) -> None:
        if is_property(__value):
            """
            "Dataclass tries to set a default and uses the `getattr(cls, name)`.  
            But the real default will come from: `_attr = field(..., default=...)`"
            See https://florimond.dev/en/posts/2018/10/reconciling-dataclasses-and-properties-in-python  
            """
            return
        if __value is None:
            """
            This will reset value to class-default when the original value is set to None.
            NOTE Requires @classmethod `classvar_map()`
            """
            for classvar_name, classvar_value in __instance.__class__.classvar_map().items():
                if (
                    type(classvar_value) in get_args(self.fget.__annotations__['return']) 
                    and self.fget.__name__ in classvar_name
                ):
                    __value = classvar_value
                    break
        return super().__set__(__instance, __value)


@dataclass
class AbsConfig:

    @classmethod
    def classvar_map(cls):
        logger.debug('Get classvar map.')
        mapping = {}
        for key, value in cls.__dataclass_fields__.items():
            if get_origin(value.type) is ClassVar:
                mapping[key] = getattr(cls, key)
        return mapping
    
    def property_map(self):
        logger.debug('Get connection property map.')
        mapping = {}
        for prop, _ in getmembers(self.__class__, predicate=is_property):
            mapping[prop] = getattr(self, prop)
        return mapping
    

    def __post_init__(self):
        for name, value in self.property_map().items():
            if value is None:

                for classvar_name, classvar_value in self.__class__.classvar_map().items():
                    if name in classvar_name:
                        value = classvar_value
                        break
                setattr(self, name, value)

@dataclass
class TurbODBCOptions(AbsConfig):
    """
    This class should hold all the advanced options for turbodbc 
    """
    autocommit: bool = field(default=None, compare=False)
    _autocommit: bool | None = field(init=False, repr=False, default=None)
    default_autocommit: ClassVar[bool] = field(init=False, default=True, compare=False)
    @config_property
    def autocommit(self) -> bool | None:
        return self._autocommit
    @autocommit.setter
    def autocommit(self, autocommit: bool | None):
        self._autocommit = autocommit

    use_async_io: bool = field(default=None, compare=False)
    _use_async_io: bool | None = field(init=False, repr=False, default=None)
    default_use_async_io: ClassVar[bool] = field(init=False, default=True, compare=False)
    @config_property
    def use_async_io(self) -> bool | None:
        return self._use_async_io
    @use_async_io.setter
    def use_async_io(self, use_async_io: bool | None):
        self._use_async_io = use_async_io

    prefer_unicode: bool = field(default=None, compare=False)
    _prefer_unicode: bool | None = field(init=False, repr=False, default=None)
    default_prefer_unicode: ClassVar[bool] = field(init=False, default=True, compare=False)
    @config_property
    def prefer_unicode(self) -> bool | None:
        return self._prefer_unicode
    @prefer_unicode.setter
    def prefer_unicode(self, prefer_unicode: bool | None):
        self._prefer_unicode = prefer_unicode
    
    read_buffer_size: Megabytes = field(default=None, compare=False)
    _read_buffer_size: Megabytes | None = field(init=False, repr=False, default=None)
    default_read_buffer_size: ClassVar[Megabytes] = field(init=False, default=Megabytes(42), compare=False)
    @config_property
    def read_buffer_size(self) -> Megabytes | None:
        return self._read_buffer_size
    @read_buffer_size.setter
    def read_buffer_size(self, read_buffer_size: Megabytes | None):
        self._read_buffer_size = read_buffer_size
    
    # parameter_sets_to_buffer: int = field(default=None, compare=False)
    # _parameter_sets_to_buffer: int | None = field(init=False, repr=False, default=None)
    # default_parameter_sets_to_buffer: ClassVar[int] = field(init=False, default=1000, compare=False)
    # @config_property
    # def parameter_sets_to_buffer(self) -> int | None:
    #     return self._parameter_sets_to_buffer
    # @parameter_sets_to_buffer.setter
    # def parameter_sets_to_buffer(self, parameter_sets_to_buffer: int | None):
    #     self._parameter_sets_to_buffer = parameter_sets_to_buffer
    
    varchar_max_character_limit: int = field(default=None, compare=False)
    _varchar_max_character_limit: int | None = field(init=False, repr=False, default=None)
    default_varchar_max_character_limit: ClassVar[int] = field(init=False, default=65535, compare=False)
    @config_property
    def varchar_max_character_limit(self) -> int | None:
        return self._varchar_max_character_limit
    @varchar_max_character_limit.setter
    def varchar_max_character_limit(self, varchar_max_character_limit: int | None):
        self._varchar_max_character_limit = varchar_max_character_limit
    
    large_decimals_as_64_bit_types: bool = field(default=None, compare=False)
    _large_decimals_as_64_bit_types: bool | None = field(init=False, repr=False, default=None)
    default_large_decimals_as_64_bit_types: ClassVar[bool] = field(init=False, default=False, compare=False)
    @config_property
    def large_decimals_as_64_bit_types(self) -> bool | None:
        return self._large_decimals_as_64_bit_types
    @large_decimals_as_64_bit_types.setter
    def large_decimals_as_64_bit_types(self, large_decimals_as_64_bit_types: bool | None):
        self._large_decimals_as_64_bit_types = large_decimals_as_64_bit_types
    
    limit_varchar_results_to_max: bool = field(default=None, compare=False)
    _limit_varchar_results_to_max: bool | None = field(init=False, repr=False, default=None)
    default_limit_varchar_results_to_max: ClassVar[bool] = field(init=False, default=False, compare=False)
    @config_property
    def limit_varchar_results_to_max(self) -> bool | None:
        return self._limit_varchar_results_to_max
    @limit_varchar_results_to_max.setter
    def limit_varchar_results_to_max(self, limit_varchar_results_to_max: bool | None):
        self._limit_varchar_results_to_max = limit_varchar_results_to_max
    
    force_extra_capacity_for_unicode: bool = field(default=None, compare=False)
    _force_extra_capacity_for_unicode: bool | None = field(init=False, repr=False, default=None)
    default_force_extra_capacity_for_unicode: ClassVar[bool] = field(init=False, default=False, compare=False)
    @config_property
    def force_extra_capacity_for_unicode(self) -> bool | None:
        return self._force_extra_capacity_for_unicode
    @force_extra_capacity_for_unicode.setter
    def force_extra_capacity_for_unicode(self, force_extra_capacity_for_unicode: bool | None):
        self._force_extra_capacity_for_unicode = force_extra_capacity_for_unicode
    
    fetch_wchar_as_char: bool = field(default=None, compare=False)
    _fetch_wchar_as_char: bool | None = field(init=False, repr=False, default=None)
    default_fetch_wchar_as_char: ClassVar[bool] = field(init=False, default=False, compare=False)
    @config_property
    def fetch_wchar_as_char(self) -> bool | None:
        return self._fetch_wchar_as_char
    @fetch_wchar_as_char.setter
    def fetch_wchar_as_char(self, fetch_wchar_as_char: bool | None):
        self._fetch_wchar_as_char = fetch_wchar_as_char


@dataclass
class SQLConfig(AbsConfig):
    """
    NOTE: Mind the `driver` field value. It better be (if available) an explicit ODBC driver with specified version, ex. 'ODBC Driver 17 for SQL Server'. Generic values like 'SQL Server' will seriously limit turbodbc capabilities.

    An obscured attribute declaration is intentional here.
    This is very ugly, but is "simplest" way I found so far to 'replace' protected field with a dummy during instantiation.  

    Ex. with `server` attributes:

    server : is a dummy-field that is used on init and gets added to repr. This gets overwriten with property attribute right away. So it is only here to look "pretty".

    _server : a field that holds actual value for an instance

    default_server - is classwide default. Attributes initialized as (or reset to) `None` will borrow from this default.
    """
    server: str = field(default=None, compare=False)
    _server: str | None = field(init=False, repr=False, default=None)
    default_server: ClassVar[str] = field(init=False, default='', compare=False)
    @config_property
    def server(self) -> str | None:
        return self._server
    @server.setter
    def server(self, server: str | None):
        self._server = server
    
    database: str = field(default=None, compare=False)
    _database: str | None = field(init=False, repr=False, default=None)
    default_database: ClassVar[str] = field(init=False, default='', compare=False)
    @config_property
    def database(self) -> str | None:
        return self._database
    @database.setter
    def database(self, database: str):
        self._database = database
    
    driver: str = field(default=None, compare=False)
    _driver: str | None = field(init=False, repr=False, default=None)
    default_driver: ClassVar[str] = field(init=False, default=r'ODBC Driver 17 for SQL Server', compare=False)
    @config_property
    def driver(self) -> str | None:
        return self._driver
    @driver.setter
    def driver(self, driver: str):
        self._driver = driver
    
    trusted_connection: bool | Literal['YES', 'NO']  = field(default=None, compare=False)
    _trusted_connection: bool | Literal['YES', 'NO'] | None = field(init=False, repr=False, default=None)
    default_trusted_connection: ClassVar[bool | Literal['YES', 'NO']] = field(init=False, default='YES', compare=False)
    @config_property
    def trusted_connection(self) -> bool | Literal['YES', 'NO'] | None:
        return self._trusted_connection
    @trusted_connection.setter
    def trusted_connection(self, trusted_connection: bool):
        self._trusted_connection = trusted_connection

    turbodbc_options: Options = field(default=None, compare=False)
    _turbodbc_options: Options | TurbODBCOptions | None = field(init=False, repr=False, default=None)
    @config_property
    def turbodbc_options(self) -> Options | None:
        return self._turbodbc_options
    @turbodbc_options.setter
    def turbodbc_options(self, turbodbc_options: Options | TurbODBCOptions):
        if type(turbodbc_options) is TurbODBCOptions:
            turbodbc_options = make_options(**self.property_map())
        self._turbodbc_options = turbodbc_options
    

    def __post_init__(self):
        super().__post_init__()
        if self._turbodbc_options is None:
            self._turbodbc_options = TurbODBCOptions()
        self.turbodbc_options = make_options(**self._turbodbc_options.property_map())
    

    def pre_connect(self) -> None:
        """
        Actions that precede connection creation.

        Example: 
        ```
        if time_between(start, end):
            sleep(30 * 60)
        ```
        """
        logger.debug('Running default pre-connection placeholder procedure.')
        pass

    def get_connection(self) -> Connection:

        self.pre_connect()

        mapping = self.property_map()

        logger.debug('Opening connection')
        return connect(**mapping)
    
    def get_cursor(self) -> Cursor:

        connection = self.get_connection()

        logger.debug('Preparing cursor object')
        return connection.cursor()


@dataclass
class Query:
    """
    Single Query object.

    ---
    Attributes:  
    `stmt` :  query statement (alternatively can be a file path, see `__post_init__`)
    `data` :  input/output data (contextual)
    `conf` :  connection configuration
    `complete` : completion flag
    `nattempts` : number of retry attempts
    `fsleep` : sleeptime after failed attempt

    ---
    NOTE(S)
    dataclass's default_factory acts funny on inheritance.
    
    Running multi-statement transactions with turbodbc can be challenging.  
    
    To name a few examples: 
        - MARS Transactions, see `Query().update_stmt()`
        - Non T-SQL statements like GO must be avoided
        - Very much driver dependent. Driver better be specified explicitly.
    """

    stmt: str | Path = '' 
    data: pd.DataFrame = cast(pd.DataFrame, None)
    # conf: SQLConfig = field(default_factory=SQLConfig)
    conf: SQLConfig = cast(SQLConfig, None)
    complete: bool = False
    nattempts: int = 1
    fsleep: int = 0


    def __post_init__(self):
        if self.conf is None:
            self.conf = SQLConfig()
        
        try:
            # self.stmt = Path(self.stmt).read_text(encoding='utf-8')
            with io.open(self.stmt, mode='rt+', encoding='utf-8') as file:
                self.stmt = file.read()
            logger.debug('Statement is a file path')
        except FileNotFoundError as error:
            logger.exception(f'File not found: {self.stmt}', exc_info=error)
            # logger.exception(f'File not found: {self.stmt}')
            # pass
        except OSError:
            logger.debug('Statement is a string.')
            # pass

        if not isinstance(self.stmt, str):
            raise TypeError('Statement should be a valid SQL string by now.')
        
        # remove inline comments
        self.stmt = re.sub(r'--.*?\n', ' ', self.stmt)
        # logger.debug(f"Cleaned up statement:\n{self.stmt}")

        # self.placeholders = re.findall(r'\?', self.stmt)
        # logger.debug(f"Placeholders:\n{self.placeholders}")
        self.update_stmt()
    

    def execute_once(self, cursor: Cursor | None = None) -> pd.DataFrame:
        """
        Main wrapper to execute `Query` statement.
        """

        if not cursor:
            cursor = self.conf.get_cursor()

        match self.data:
            case pd.DataFrame():
                
                # to correctly convert any missing values to SQL NULLs
                if self.data.isna().any(axis=None):
                    self.data = self.data.astype('object').where(self.data.notna(), None)
                
                # dt_cols = self.data.select_dtypes(include='datetime64[ns]').columns
                # if not dt_cols.empty:
                #     self.data[dt_cols] = self.data[dt_cols].stack().dt.strftime('%Y-%m-%d %H:%M:%S').unstack()
                
                cursor.executemany(self.stmt, self.data.itertuples(index=False))
            case None:
                cursor.execute(self.stmt)
            case _:
                raise TypeError
        
        try:
            result = cursor.fetchallnumpy()
            self.data = pd.DataFrame.from_dict(result)
            return self.data
        except InterfaceError:
            # This error only raised after statement was executed
            # Thus assume it only happens when no result is returned
            return cast(pd.DataFrame, None)
        finally:
            self.complete = True
    
    def execute(self, cursor: Cursor | None = None) -> pd.DataFrame:
        errors = []
        for attempt in range(self.nattempts):
            try:
                return self.execute_once(cursor)
            except DatabaseError as error:
                if self.nattempts <= 1:
                    raise error
                logger.exception(f'Attempt {attempt + 1}/{self.nattempts} failed.', exc_info=True)
                errors.append(error)
                if self.fsleep:
                    shou = self.fsleep // 3600
                    smin = (self.fsleep % 3600) // 60
                    ssec = self.fsleep % 60
                    logger.info(f'Sleeping for {shou:02d}:{smin:02d}:{ssec:02d}')
                    sleep(self.fsleep)
        raise ExceptionGroup(f'All execution retries failed ({self.nattempts=}).', errors)
        
    def update_stmt(self):
        """
        Usecase / Example:  

        Transactions with Multiple Active Result Sets (MARS) 
        may return nothing without `SET NOCOUNT ON` header.  

        `self.stmt = 'SET NOCOUNT ON;\n' + self.stmt`
        """
        logger.debug('Running default statement update placeholder procedure.')
        pass


class Mixin():
    """
    Helper mixin class
    """
    
    def __len__(self):
        return len(self.__dict__)

    def __iter__(self):
        return iter(self.__dict__)

    def __setitem__(self, __name: str, __value) -> None:
        self.__dict__[__name] = __value

    def __getitem__(self, __name: str) -> Any:
        return self.__dict__[__name]


    def __getattr__(self, __name: str) -> Any:
        try:
            return self.__dict__[__name]
        except KeyError:
            raise AttributeError(__name)

    def __setattr__(self, __name: str, __value: Any) -> None:
        self.__dict__[__name] = __value


@dataclass
class QuerySequence(Mixin, Mapping):

    def run_par(self) -> None:
        """
        Moved to joblib implementation over multiprocessing.
        Cleaner, simpler and no issues with pickling.
        Joblib cons are: extra dependency, not as parallel, logging sucks (latter is yet irrelevant here)
        """
        with Parallel(backend='threading', n_jobs=-1) as parallel:
        # with Parallel(backend='loky', n_jobs=-1, verbose=True) as parallel:
            dfunc = delayed(Query.execute)
            dqueries = (dfunc(query) for query in self.values())
            parallel(dqueries)


    def all_confs_equal(self) -> bool:
        """
        Checks if `conf`s are identical instances across all `Query` objects in `QuerySequence`.
        """
        iter_queries = iter(self.values())
        try:
            first = next(iter_queries).conf
        except StopIteration:
            return True
        return all(((first == query.conf) for query in iter_queries))


    def prep_cursor(self) -> Cursor | None:
        """
        Only relevant for sequential query run.  
        Creates (and keeps open) a common `cursor()` instance in case all `conf`s are identical.   
        Otherwise each `cursor` created separately per `Query` execution.
        """
        if self.all_confs_equal():
            query: Query = next(iter(self.values()))
            logger.debug('SQL configs identical => Creating group cursor.')
            return query.conf.get_cursor()
        else:
            logger.debug('SQL configs differ => Each query will get its own cursor.')
            return None

    def gen_seq(self) -> Generator[pd.DataFrame | None, None, None]:
        """
        Generator for sequential execution of multiple `Query` objects.
        """
        cursor = self.prep_cursor()

        for key, query in self.items():
            logger.info(f'Running query: {key}')
            yield query.execute(cursor)
            
        if cursor:
            cursor.close()


    def run_seq(self) -> None:
        """
        Main wrapper for sequential execution.
        """
        for num, data in enumerate(self.gen_seq()):
            
            match data:
                case pd.DataFrame():
                    logger.info(f'Data shape: {data.shape}')
                case _:
                    logger.info('No data returned')
            
            logger.info(f'{num + 1} / {len(self)} queries complete.')

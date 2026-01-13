from typing import List, Dict, Literal, Optional, TYPE_CHECKING, Union, Any
from urllib.parse import urljoin

from geobox.enums import TableExportFormat

from .base import AsyncBase
from .task import AsyncTask
from ..enums import FieldType
from ..exception import NotFoundError
from ..utils import clean_data

if TYPE_CHECKING:
    from . import AsyncGeoboxClient
    from .user import AsyncUser
    from .. import GeoboxClient
    from .file import AsyncFile
    from ..table import Table, TableField, TableRow


class AsyncTableRow(AsyncBase):

    def __init__(self, 
        table: 'AsyncTable',
        data: Optional[Dict] = {},
    ):
        """
        Constructs all the necessary attributes for the AsyncTableRow object.

        Args:
            table (AsyncTable): The table that the row belongs to.
            data (Dict, optional): The data of the field.
        """
        super().__init__(api=table.api, data=data)
        self.table = table
        self.endpoint = urljoin(table.endpoint, f'rows/{self.id}/') if self.data.get('id') else None


    def __repr__(self) -> str:
        """
        Return a string representation of the AsyncTableRow.

        Returns:
            str: The string representation of the AsyncTableRow.
        """
        return f"AsyncTableRow(id={self.id}, table_name={self.table.data.get('name', 'None')})"


    @classmethod
    async def create_row(cls, table: 'AsyncTable', **kwargs) -> 'AsyncTableRow':
        """
        [async] Create a new row in the table.

        Each keyword argument represents a field value for the row, where:
            - The keyword is the field name
            - The value is the field value

        Args:
            table (AsyncTable): table instance

        Keyword Args: 
            **kwargs: Arbitrary field values matching the table schema.

        Returns:
            AsyncTableRow: created table row instance

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.table import AsyncTable, AsyncTableRow
            >>> async with AsyncGeoboxClient() as client:
            >>>     table = await client.get_table(uuid="12345678-1234-5678-1234-567812345678")
            or
            >>>     table = await AsyncTable.get_table(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     row_data = {
            ...        'field1': 'value1'
            ...     }
            >>>     row = await table.create_row(row_data)
            or
            >>>     row = await AsyncTableRow.create_row(table, row_data)
        """
        endpoint = urljoin(table.endpoint, 'rows/')
        return await cls._create(table.api, endpoint, kwargs, factory_func=lambda api, item: AsyncTableRow(table, data=item))


    @classmethod
    async def get_row(cls, 
        table: 'AsyncTable', 
        row_id: int,
        user_id: Optional[int],
    ) -> 'AsyncTableRow':
        """
        [async] Get a row by its id

        Args:
            table (AsyncTable): the table instance
            row_id (int): the row id
            user_id (int, optional): specific user. privileges required.

        Returns:
            TanbleRow: the table row instance

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.table import AsyncTable, AsyncTableRow
            >>> async with AsyncGeoboxClient() as client:
            >>>     table = await client.get_table(uuid="12345678-1234-5678-1234-567812345678")
            or
            >>>     table = await AsyncTable.get_table(client, uuid="12345678-1234-5678-1234-567812345678")

            >>>     row = await table.get_row(row_id=1)
            or
            >>>     row = await AsyncTableRow.get_row(table, row_id=1)
        """
        param = {
            'f': 'json',
            'user_id': user_id
        }
        endpoint = urljoin(table.endpoint, f'rows/')
        return await cls._get_detail(table.api, endpoint, uuid=row_id, params=param, factory_func=lambda api, item: AsyncTableRow(table, data=item))


    async def update(self, **kwargs) -> Dict:
        """
        [async] Update a row

        Keyword Args:
            fields to update

        Returns:
            Dict: updated row data

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     table = await client.get_table(uuid="12345678-1234-5678-1234-567812345678")
            >>>     row = await table.get_row(row_id=1)
            >>>     await row.update(field1='new_value')
        """
        await super()._update(self.endpoint, self.data, clean=False)
        return self.data


    async def delete(self) -> None:
        """
        [async] Delete a row

        Returns: 
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     table = await client.get_table(uuid="12345678-1234-5678-1234-567812345678")
            >>>     row = await table.get_row(row_id=1)
            >>>     await row.delete()
        """
        await super()._delete(self.endpoint)


    def to_sync(self, sync_client: 'GeoboxClient') -> 'TableRow':
        """
        Switch to sync version of the table row instance to have access to the sync methods

        Args:
            sync_client (GeoboxClient): The sync version of the GeoboxClient instance for making requests.

        Returns:
            TableRow: the sync instance of the TableRow.

        Example:
            >>> from geobox import Geoboxclient
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     table = await client.get_table(uuid="12345678-1234-5678-1234-567812345678")
            >>>     row = await table.get_row(row_id=1)
            >>>     sync_client = GeoboxClient()
            >>>     sync_row = row.to_sync(sync_client)
        """
        from ..table import TableRow

        sync_table = self.table.to_sync(sync_client=sync_client)
        return TableRow(table=sync_table, data=self.data)



class AsyncTableField(AsyncBase):

    def __init__(self, 
        table: 'AsyncTable',
        data_type: 'FieldType',
        field_id: int = None,
        data: Optional[Dict] = {},
    ):
        """
        Constructs all the necessary attributes for the Field object.

        Args:
            table (AsyncTable): The table that the field belongs to.
            data_type (FieldType): type of the field
            field_id (int): the id of the field
            data (Dict, optional): The data of the field.
        """
        super().__init__(api=table.api, data=data)
        self.table = table
        self.field_id = field_id
        if not isinstance(data_type, FieldType):
            raise ValueError("data_type must be a FieldType instance")
        self.data_type = data_type
        self.endpoint = urljoin(table.endpoint, f'fields/{self.id}/') if self.data.get('id') else None


    def __repr__(self) -> str:
        """
        Return a string representation of the field.

        Returns:
            str: The string representation of the field.
        """
        return f"AsyncTableField(id={self.id}, name={self.name}, data_type={self.data_type})"

        
    def __getattr__(self, name: str) -> Any:
        """
        Get an attribute from the resource.

        Args:
            name (str): The name of the attribute
        """
        if name == 'datatype':
            return FieldType(self.data['datatype'])
        return super().__getattr__(name)


    @property
    def domain(self) -> Dict:
        """
        Domain property

        Returns:
            Dict: domain data
        """
        return self.data.get('domain')


    @domain.setter
    def domain(self, value: Dict) -> None:
        """
        Domain property setter

        Returns:
            None
        """
        self.data['domain'] = value
        

    @classmethod
    async def create_field(cls, 
        table: 'AsyncTable', 
        name: str, 
        data_type: 'FieldType', 
        data: Dict = {},
    ) -> 'AsyncTableField':
        """
        [async] Create a new field

        Args:
            table (AsyncTable): field's table
            name (str): name of the field
            data_type (FieldType): type of the field
            data (Dict, optional): the data of the field

        Returns:
            AsyncTableField: the created field object

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.table import AsyncTable, AsyncTableField
            >>> async with AsyncGeoboxClient() as client:
            >>>     table = await client.get_table(uuid="12345678-1234-5678-1234-567812345678")

            >>>     field = await table.create_field(name='test', data_type=FieldType.Integer)
            or
            >>>     field = await AsyncTableField.create_field(client, table=table, name='test', data_type=FieldType.Integer)
        """
        data.update({
            "name": name,
            "datatype": data_type.value
        })
        endpoint = urljoin(table.endpoint, 'fields/')
        return await super()._create(table.api, endpoint, data, factory_func=lambda api, item: AsyncTableField(table, data_type, item['id'], item))


    async def delete(self) -> None:
        """
        [async] Delete the field.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.field import AsyncTableField
            >>> async with AsyncGeoboxClient() as client:
            >>>     table = await client.get_table(uuid="12345678-1234-5678-1234-567812345678")
            >>>     field = await table.get_field(field_id=1)
            >>>     await field.delete()
        """
        await super()._delete(self.endpoint)
        self.field_id = None


    async def update(self, **kwargs) -> Dict:
        """
        [async] Update the field.

        Keyword Args:
            name (str): The name of the field.
            display_name (str): The display name of the field.
            description (str): The description of the field.
            domain (Dict): the domain of the field
            hyperlink (bool): the hyperlink field.

        Returns:
            Dict: The updated data.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.table import AsyncTableField
            >>> async with AsyncGeoboxClient() as client:
            >>>     table = await client.get_table(uuid="12345678-1234-5678-1234-567812345678")
            >>>     field = await table.get_field(field_id=1)
            >>>     await field.update(name="my_field", display_name="My Field", description="My Field Description")
        """       
        data = {
            "name": kwargs.get('name'),
            "display_name": kwargs.get('display_name'),
            "description": kwargs.get('description'),
            "domain": kwargs.get('domain'),
            "hyperlink": kwargs.get('hyperlink')
        }
        return await super()._update(self.endpoint, data)


    async def update_domain(self, 
        range_domain: Dict = None, 
        list_domain: Dict = None,
    ) -> Dict:
        """
        [async] Update field domian values

        Args:
            range_domain (Dict): a dictionary with min and max keys.
            list_domain (Dict): a dictionary containing the domain codes and values.

        Returns:
            Dict: the updated field domain

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     field = await client.get_table(uuid="12345678-1234-5678-1234-567812345678").get_fields()[0]
            >>>     range_d = {'min': 1, 'max': 10}
            >>>     await field.update_domain(range_domain = range_d)
            or 
            >>>     list_d = {'1': 'value1', '2': 'value2'}
            >>>     await field.update_domain(list_domain=list_d)
        """
        if not self.domain:
            self.domain = {'min': None, 'max': None, 'items': {}}

        if range_domain:
            self.domain['min'] = range_domain['min']
            self.domain['max'] = range_domain['max']

        if list_domain:
            self.domain['items'] = {**self.domain['items'], **list_domain}

        await self.update(domain=self.domain)
        return self.domain


    def to_sync(self, sync_client: 'GeoboxClient') -> 'TableField':
        """
        Switch to sync version of the table field instance to have access to the sync methods

        Args:
            sync_client (GeoboxClient): The sync version of the GeoboxClient instance for making requests.

        Returns:
            TableField: the sync instance of the TableField.

        Example:
            >>> from geobox import Geoboxclient
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     table = await client.get_table(uuid="12345678-1234-5678-1234-567812345678")
            >>>     field = await table.get_field(field_id=1)
            >>>     sync_client = GeoboxClient()
            >>>     sync_field = field.to_sync(sync_client)
        """
        from ..table import TableField

        sync_table = self.table.to_sync(sync_client=sync_client)
        return TableField(table=sync_table, data_type=self.data_type, field_id=self.field_id, data=self.data)



class AsyncTable(AsyncBase):

    BASE_ENDPOINT = 'tables/'

    def __init__(self, 
        api: 'AsyncGeoboxClient', 
        uuid: str,
        data: Optional[Dict] = {}):
        """
        Initialize a table instance.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            uuid (str): The unique identifier for the table.
            data (Dict): The response data of the table.
        """
        super().__init__(api, uuid=uuid, data=data)


    @classmethod
    async def get_tables(cls, api: 'AsyncGeoboxClient', **kwargs) -> Union[List['AsyncTable'], int]:
        """
        [async] Get list of tables with optional filtering and pagination.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.

        Keyword Args:
            include_settings (bool): Whether to include table settings. default: False
            temporary (bool): Whether to return temporary tables. default: False
            q (str): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'"
            search (str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored
            search_fields (str): comma separated list of fields for searching
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count (bool): Whether to return total count. default: False.
            skip (int): Number of items to skip. default: 0
            limit (int): Number of items to return. default: 10
            user_id (int): Specific user. privileges required
            shared (bool): Whether to return shared tables. default: False

        Returns:
            List[AsyncTable] | int: A list of table instances or the total number of tables.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.table import AsyncTable
            >>> async with AsyncGeoboxClient() as client:
            >>>     tables = await client.get_tables(q="name LIKE '%My table%'")
            or
            >>>     tables = await AsyncTable.get_tables(client, q="name LIKE '%My table%'")
        """
        params = {
           'f': 'json',
           'include_settings': kwargs.get('include_settings', False),
           'temporary': kwargs.get('temporary'),
           'q': kwargs.get('q'),
           'search': kwargs.get('search'),
           'search_fields': kwargs.get('search_fields'),
           'order_by': kwargs.get('order_by'),
           'return_count': kwargs.get('return_count', False),
           'skip': kwargs.get('skip', 0),
           'limit': kwargs.get('limit', 10),
           'user_id': kwargs.get('user_id'),
           'shared': kwargs.get('shared', False)
        }
        return await super()._get_list(api, cls.BASE_ENDPOINT, params, factory_func=lambda api, item: AsyncTable(api, item['uuid'], item))
    

    @classmethod
    async def create_table(cls, 
        api: 'AsyncGeoboxClient', 
        name: str, 
        display_name: Optional[str] = None, 
        description: Optional[str] = None, 
        temporary: bool = False,
        fields: Optional[List[Dict]] = None,
    ) -> 'AsyncTable':
        """
        [async] Create a new table.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            name (str): The name of the AsyncTable.
            display_name (str, optional): The display name of the table.
            description (str, optional): The description of the table.
            temporary (bool, optional): Whether to create a temporary tables. default: False
            fields (List[Dict], optional): raw table fields. you can use create_field method for simpler and safer field addition. required dictionary keys: name, datatype

        Returns:
            AsyncTable: The newly created table instance.

        Raises:
            ValidationError: If the table data is invalid.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.table import AsyncTable
            >>> async with AsyncGeoboxClient() as client:
            >>>     table = await client.create_table(name="my_table")
            or
            >>>     table = await AsyncTable.create_table(client, name="my_table")            
        """
        data = {
            "name": name,
            "display_name": display_name,
            "description": description,
            "temporary": temporary,
            "fields": fields,
        }
        return await super()._create(api, cls.BASE_ENDPOINT, data, factory_func=lambda api, item: AsyncTable(api, item['uuid'], item))

    
    @classmethod
    async def get_table(cls, api: 'AsyncGeoboxClient', uuid: str, user_id: int = None) -> 'AsyncTable':
        """
        [async] Get a table by UUID.

        Args:
            api (AsyncGeoboxClient): The GeoboxClient instance for making requests.
            uuid (str): The UUID of the table to get.
            user_id (int): Specific user. privileges required.

        Returns:
            AsyncTable: The AsyncTable object.

        Raises:
            NotFoundError: If the table with the specified UUID is not found.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.table import AsyncTable
            >>> async with AsyncGeoboxClient() as client:
            >>>     table = await client.get_table(uuid="12345678-1234-5678-1234-567812345678")
            or
            >>>     table = await AsyncTable.get_table(client, uuid="12345678-1234-5678-1234-567812345678")
        """
        params = {
            'f': 'json',
            'user_id': user_id,
        }
        return await super()._get_detail(api, cls.BASE_ENDPOINT, uuid, params, factory_func=lambda api, item: AsyncTable(api, item['uuid'], item))


    @classmethod
    async def get_table_by_name(cls, api: 'AsyncGeoboxClient', name: str, user_id: int = None) -> Union['AsyncTable', None]:
        """
        [async] Get a table by name

        Args:
            api (AsyncGeoboxClient): The GeoboxClient instance for making requests.
            name (str): the name of the table to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            AsyncTable | None: returns the table if a table matches the given name, else None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.table import AsyncTable
            >>> async with AsyncGeoboxClient() as client:
            >>>     table = await client.get_table_by_name(name='test')
            or
            >>>     table = await AsyncTable.get_table_by_name(client, name='test')
        """
        tables = await cls.get_tables(api, q=f"name = '{name}'", user_id=user_id)
        if tables and tables[0].name == name:
            return tables[0]
        else:
            return None


    async def update(self, **kwargs) -> Dict:
        """
        [async] Update the table.

        Keyword Args:
            name (str): The name of the table.
            display_name (str): The display name of the table.
            description (str): The description of the table.

        Returns:
            Dict: The updated table data.

        Raises:
            ValidationError: If the table data is invalid.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.table import AsyncTable
            >>> async with AsyncGeoboxClient() as client:
            >>>     table = await AsyncTable.get_table(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await table.update_table(display_name="New Display Name")
        """
        data = {
            "name": kwargs.get('name'),
            "display_name": kwargs.get('display_name'),   
            "description": kwargs.get('description'),
        }
        return await super()._update(self.endpoint, data)
    

    async def delete(self) -> None:
        """
        [async] Delete the AsyncTable.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.table import AsyncTable
            >>> async with AsyncGeoboxClient() as client:
            >>>     table = await AsyncTable.get_table(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await table.delete()
        """
        await super()._delete(self.endpoint)


    @property
    async def settings(self) -> Dict:
        """
        [async] Get the table's settings.
        
        Returns:
            Dict: The table settings.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.table import AsyncTable
            >>> async with AsyncGeoboxClient() as client:
            >>>     table = await AsyncTable.get_table(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     setting = await table.settings
        """
        return await super()._get_settings(endpoint=self.endpoint)
    

    async def update_settings(self, settings: Dict) -> Dict:
        """
        [async] Update the settings

        settings (Dict): settings dictionary

        Returns:
            Dict: updated settings

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     table1 = await client.get_table(uuid="12345678-1234-5678-1234-567812345678")
            >>>     table2 = await client.get_table(uuid="12345678-1234-5678-1234-567812345678")
            >>>     await table1.update_settings(table2.settings)
        """
        return await super()._set_settings(self.endpoint, settings)


    async def get_fields(self) -> List['AsyncTableField']:
        """
        [async] Get all fields of the table.
        
        Returns:
            List[AsyncTableField]: A list of Field instances representing the table's fields.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.table import AsyncTable
            >>> async with AsyncGeoboxClient() as client:
            >>>     table = await AsyncTable.get_table(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     fields = await table.get_fields()
        """
        endpoint = urljoin(self.endpoint, 'fields/')
        return await super()._get_list(
            api=self.api,
            endpoint=endpoint,
            factory_func=lambda api, item: AsyncTableField(table=self, data_type=FieldType(item['datatype']), field_id=item['id'], data=item),
        )


    async def get_field(self, field_id: int) -> 'AsyncTableField':
        """
        [async] Get a specific field by ID.
        
        Args:
            field_id (int, optional): The ID of the field to retrieve.

        Returns:
            AsyncTableField: The requested field instance.
            
        Raises:
            NotFoundError: If the field with the specified ID is not found. 

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.table import AsyncTable
            >>> async with AsyncGeoboxClient() as client:
            >>>     table = await AsyncTable.get_table(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     field = await table.get_field(field_id=1)
        """        
        field = next((f for f in await self.get_fields() if f.id == field_id), None)
        if not field:
            raise NotFoundError(f'Field with ID {field_id} not found in table {self.name}')
            
        return field


    async def get_field_by_name(self, name: str) -> 'AsyncTableField':
        """
        [async] Get a specific field by name.
        
        Args:
            name (str): The name of the field to retrieve.

        Returns:
            AsyncTableField: The requested field instance.
            
        Raises:
            NotFoundError: If the field with the specified name is not found. 

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.table import AsyncTable
            >>> async with AsyncGeoboxClient() as client:
            >>>     table = await AsyncTable.get_table(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     field = await table.get_field_by_name(name='test')
        """        
        field = next((f for f in await self.get_fields() if f.name == name), None)
        if not field:
            raise NotFoundError(f"Field with name '{name}' not found in table {self.name}")
            
        return field


    async def add_field(self, name: str, data_type: 'FieldType', data: Dict = {}) -> 'AsyncTableField':
        """
        [async] Add a new field to the table.
        
        Args:
            name (str): The name of the new field.
            data_type (FieldType): The data type of the new field.
            data (Dict, optional): Additional field properties (display_name, description, etc.).
            
        Returns:
            Field: The newly created field instance.
            
        Raises:
            ValidationError: If the field data is invalid.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.table import AsyncTable
            >>> async with AsyncGeoboxClient() as client:
            >>>     table = await AsyncTable.get_table(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     field = await table.add_field(name="new_field", data_type=FieldType.String)
        """
        return await AsyncTableField.create_field(self, name=name, data_type=data_type, data=data)


    async def calculate_field(self, 
        target_field: str, 
        expression: str, 
        q: Optional[str] = None, 
        search: Optional[str] = None, 
        search_fields: Optional[str] = None, 
        row_ids: Optional[str] = None, 
        run_async: bool = True, 
        user_id: Optional[int] = None,
    ) -> Union['AsyncTask', Dict]:
        """
        [async] Calculate values for a field based on an expression.
        
        Args:
            target_field (str): The field to calculate values for.
            expression (str): The expression to use for calculation.
            q (str, optional): Query to filter features. default: None.
            search (str, optional): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value
            search_fields (str, optional): comma separated list of fields for searching
            row_ids (str, optional): List of specific row IDs to include. default: None
            run_async (bool, optional): Whether to run the calculation asynchronously. default: True.
            user_id (int, optional): Specific user. privileges required.
            
        Returns:
            Task | Dict: The task instance of the calculation operation or the api response if the run_async=False.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.table import AsyncTable
            >>> async with AsyncGeoboxClient() as client:
            >>>     table = await AsyncTable.get_table(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     task = await table.calculate_field(target_field="target_field", 
            ...         expression="expression", 
            ...         q="name like 'my_layer'", 
            ...         row_ids=[1, 2, 3], 
            ...         run_async=True)
        """
        data = clean_data({
            "target_field": target_field,
            "expression": expression,
            "q": q,
            "search": search,
            "search_fields": search_fields,
            "row_ids": row_ids,
            "run_async": run_async,
            "user_id": user_id
        })
        
        endpoint = urljoin(self.endpoint, 'calculateField/')
        response = await self.api.post(endpoint, data, is_json=False)
        if run_async:
            task = await AsyncTask.get_task(self.api, response.get('task_id'))
            return task

        return response


    async def get_rows(self, **kwargs) -> List['AsyncTableRow']:
        """
        [async] Query rows of a table

        Keyword Args:
            q (str): Advanced filtering expression, e.g., 'status = "active" and age > 20'
            search (str): Search term for keyword-based searching among fields/columns
            search_fields (str): Comma separated column names to search in
            row_ids (str): Comma separated list of row ids to filter for
            fields (str): Comma separated column names to include in results, or [ALL]
            exclude (str): Comma separated column names to exclude from result
            order_by (str): Comma separated list for ordering, e.g., 'name A, id D'
            skip (int): Number of records to skip for pagination. default: 0
            limit (int): Maximum number of records to return. default: 100
            return_count (bool): If true, returns only the count of matching rows
            user_id (int): Specific user. privileges required

        Returns:
            List[AsyncTableRow]: list of table rows objects

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.table import AsyncTable
            >>> async with AsyncGeoboxClient() as client:
            >>>     table = await client.get_table(uuid="12345678-1234-5678-1234-567812345678")
            or
            >>>     table = await AsyncTable.get_table(client, uuid="12345678-1234-5678-1234-567812345678")

            >>>     rows = await table.get_rows()
        """
        params = {
            'f': 'json',
            'q': kwargs.get('q'),
            'search': kwargs.get('search'),
            'search_fields': kwargs.get('search_fields'),
            'row_ids': kwargs.get('row_ids'),
            'fields': kwargs.get('fields'),
            'exclude': kwargs.get('exclude'),
            'order_by': kwargs.get('order_by'),
            'skip': kwargs.get('skip', 0),
            'limit': kwargs.get('limit', 100),
            'return_count': kwargs.get('return_count', False),
            'user_id': kwargs.get('user_id'),
        }

        endpoint = f'{self.endpoint}rows/'

        return await super()._get_list(
            api=self.api,
            endpoint=endpoint,
            params=params,
            factory_func=lambda api, item: AsyncTableRow(self, item),
        )


    async def get_row(self, 
        row_id: int, 
        user_id: Optional[int] = None,
    ) -> 'AsyncTableRow':
        """
        [async] Get a row by its id

        Args:
            row_id (int): the row id
            user_id (int, optional): specific user. privileges required.

        Returns:
            TanbleRow: the table row instance

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.table import AsyncTable
            >>> async with AsyncGeoboxClient() as client:
            >>>     table = await client.get_table(uuid="12345678-1234-5678-1234-567812345678")
            or
            >>>     table = await AsyncTable.get_table(client, uuid="12345678-1234-5678-1234-567812345678")

            >>>     row = await table.get_row(row_id=1)
        """
        return await AsyncTableRow.get_row(self, row_id, user_id)


    async def create_row(self, **kwargs) -> 'AsyncTableRow':
        """
        [async] Create a new row in the table.

        Each keyword argument represents a field value for the row, where:
            - The keyword is the field name
            - The value is the field value

        Keyword Args: 
            **kwargs: Arbitrary field values matching the table schema.

        Returns:
            AsyncTableRow: created table row instance

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.table import AsyncTable
            >>> async with AsyncGeoboxClient() as client:
            >>>     table = await client.get_table(uuid="12345678-1234-5678-1234-567812345678")
            or
            >>>     table = await AsyncTable.get_table(client, uuid="12345678-1234-5678-1234-567812345678")

            >>>     row = await table.create_row(
            ...         field1=value1
            ...     )
        """
        return await AsyncTableRow.create_row(self, **kwargs)


    async def import_rows(self, 
        file: 'AsyncFile',
        *,
        file_encoding: str = "utf-8",
        input_dataset: Optional[str] = None,
        delimiter: str = ',',
        has_header: bool = True,
        report_errors: bool = False,
        bulk_insert: bool = True,
    ) -> 'AsyncTask':
        """
        Import rows from a CSV file into a table
        
        Args:
            file (AsyncFile): file object to import.
            file_encoding (str, optional): Character encoding of the input file. default: utf-8
            input_dataset (str, optional): Name of the dataset in the input file.
            delimiter (str, optional): the delimiter of the dataset. default: ,
            has_header (bool, optional): Whether the file has header or not. default: True
            report_errors (bool, optional): Whether to report import errors. default: False
            bulk_insert (bool, optional): 
            
        Returns:
            AsyncTask: The task instance of the import operation.
            
        Raises:
            ValidationError: If the import parameters are invalid.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.table import AsyncTable
            >>> async with AsyncGeoboxClient() as client:
            >>>     table = await AsyncTable.get_table(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     file = await client.get_file(uuid="12345678-1234-5678-1234-567812345678")
            >>>     task = await table.import_rows(
            ...         file=file,
            ...     )
        """
        data = clean_data({
            "file_uuid": file.uuid,
            "file_encoding": file_encoding,
            "input_dataset": file.name if not input_dataset else input_dataset,
            "delimiter": delimiter,
            "has_header": has_header,
            "report_errors": report_errors,
            "bulk_insert": bulk_insert,
        })

        endpoint = urljoin(self.endpoint, 'import-csv/')
        response = await self.api.post(endpoint, data, is_json=False)
        task = await AsyncTask.get_task(self.api, response.get('task_id'))
        return task


    async def export_rows(self,
        out_filename: str,
        *,
        out_format: 'TableExportFormat' = TableExportFormat.CSV, 
        q: Optional[str] = None,
        search: Optional[str] = None,
        search_fields: Optional[str] = None,
        row_ids: Optional[str] = None,
        fields: Optional[str] = None,
        exclude: Optional[str] = None,
        order_by: Optional[str] = None,
        zipped: bool = False,
        run_async: bool = True,
    ) -> Union['AsyncTask', str]:
        """
        [async] Export rows of a table to a file
        
        Args:
            out_filename (str): Name of the output file without the format (.csv) 
            out_format (TableExportFormat, optional): Format of the output file
            q (str, optional): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'"
            search (str, optional): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value
            search_fields (str, optional): comma separated list of fields for searching
            row_ids (str, optional): List of specific row IDs to include
            fields (str, optional): List of specific field names to include
            exclude (str, optional): List of specific field names to exclude
            order_by (str, optional): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            zipped (str, optional): Whether to compress the output file
            run_async (bool, optional): Whether to run the export asynchronously. default: True
            
        Returns:
            AsyncTask | Dict: The task instance of the export operation (run_async=True) or the export result (run_async=False)
            
        Raises:
            ValidationError: If the export parameters are invalid.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.table import AsyncTable
            >>> async with AsyncGeoboxClient() as client:
            >>>     table = await AsyncTable.get_table(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     file = await client.get_file(uuid="12345678-1234-5678-1234-567812345678")
            >>>     task = await table.export_rows(
            ...         file=file,
            ...     )
        """
        data = clean_data({
            "out_filename": out_filename,
            "out_format": out_format.value if out_format else None,
            "q": q,
            "search": search,
            "search_fields": search_fields,
            "row_ids": row_ids,
            "fields": fields,
            "exclude": exclude,
            "order_by": order_by,
            "zipped": zipped,
            "run_async": run_async,
        })

        endpoint = urljoin(self.endpoint, 'export/')
        response = await self.api.post(endpoint, data, is_json=False)
        if run_async:
            task = await AsyncTask.get_task(self.api, response.get('task_id'))
            return task

        return response


    async def share(self, users: List['AsyncUser']) -> None:
        """
        [async] Shares the table with specified users.

        Args:
            users (List[AsyncUser]): The list of user objects to share the table with.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient             
            >>> from geobox.aio.table import AsyncTable
            >>> async with AsyncGeoboxClient() as client:
            >>>     table = await AsyncTable.get_table(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     users = await client.search_users(search='John')
            >>>     await table.share(users=users)
        """
        await super()._share(self.endpoint, users)
    

    async def unshare(self, users: List['AsyncUser']) -> None:
        """
        [async] Unshares the table with specified users.

        Args:
            users (List[User]): The list of user objects to unshare the table with.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient             
            >>> from geobox.aio.table import AsyncTable
            >>> async with AsyncGeoboxClient() as client:
            >>>     table = await AsyncTable.get_table(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     users = await client.search_users(search='John')
            >>>     await table.unshare(users=users)
        """
        await super()._unshare(self.endpoint, users)


    async def get_shared_users(self, search: str = None, skip: int = 0, limit: int = 10) -> List['AsyncUser']:
        """
        [async] Retrieves the list of users the table is shared with.

        Args:
            search (str, optional): The search query.
            skip (int, optional): The number of users to skip.
            limit (int, optional): The maximum number of users to retrieve.

        Returns:
            List[AsyncUser]: The list of shared users.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.table import AsyncTable
            >>> async with AsyncGeoboxClient() as client:
            >>>     table = await AsyncTable.get_table(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await table.get_shared_users(search='John', skip=0, limit=10)
        """
        params = {
            'search': search,
            'skip': skip,
            'limit': limit
        }
        return await super()._get_shared_users(self.endpoint, params)


    def to_sync(self, sync_client: 'GeoboxClient') -> 'Table':
        """
        Switch to sync version of the table instance to have access to the sync methods

        Args:
            sync_client (GeoboxClient): The sync version of the GeoboxClient instance for making requests.

        Returns:
            Table: the sync instance of the table.

        Example:
            >>> from geobox import Geoboxclient
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.table import AsyncTable
            >>> async with AsyncGeoboxClient() as client:
            >>>     table = await AsyncTable.get_table(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     sync_client = GeoboxClient()
            >>>     sync_table = table.to_async(sync_client)
        """
        from ..table import Table

        return Table(api=sync_client, uuid=self.uuid, data=self.data)
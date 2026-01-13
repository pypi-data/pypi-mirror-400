from typing import List, Dict, Optional, TYPE_CHECKING, Union, Any
from urllib.parse import urljoin

from geobox.enums import TableExportFormat

from .base import Base
from .task import Task
from .enums import FieldType
from .exception import NotFoundError
from .utils import clean_data

if TYPE_CHECKING:
    from . import GeoboxClient
    from .user import User
    from .aio import AsyncGeoboxClient
    from .file import File
    from .aio.table import Table as AsyncTable, AsyncTableRow, AsyncTableField



class TableRow(Base):

    def __init__(self, 
        table: 'Table',
        data: Optional[Dict] = {},
    ):
        """
        Constructs all the necessary attributes for the TableRow object.

        Args:
            table (Table): The table that the row belongs to.
            data (Dict, optional): The data of the field.
        """
        super().__init__(api=table.api, data=data)
        self.table = table
        self.endpoint = urljoin(table.endpoint, f'rows/{self.id}/') if self.data.get('id') else None


    def __repr__(self) -> str:
        """
        Return a string representation of the TableRow.

        Returns:
            str: The string representation of the TableRow.
        """
        return f"TableRow(id={self.id}, table_name={self.table.data.get('name', 'None')})"


    @classmethod
    def create_row(cls, table: 'Table', **kwargs) -> 'TableRow':
        """
        Create a new row in the table.

        Each keyword argument represents a field value for the row, where:
            - The keyword is the field name
            - The value is the field value

        Args:
            table (Table): table instance

        Keyword Args: 
            **kwargs: Arbitrary field values matching the table schema.

        Returns:
            TableRow: created table row instance

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.table import Table, TableRow
            >>> client = GeoboxClient()
            >>> table = client.get_table(uuid="12345678-1234-5678-1234-567812345678")
            or
            >>> table = Table.get_table(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> row_data = {
                'field1': 'value1'
            }
            >>> row = TableRow.create_row(table, row_data)
        """
        endpoint = urljoin(table.endpoint, 'rows/')
        return cls._create(table.api, endpoint, kwargs, factory_func=lambda api, item: TableRow(table, data=item))


    @classmethod
    def get_row(cls, 
        table: 'Table', 
        row_id: int,
        user_id: Optional[int],
    ) -> 'TableRow':
        """
        Get a row by its id

        Args:
            table (Table): the table instance
            row_id (int): the row id
            user_id (int, optional): specific user. privileges required.

        Returns:
            TanbleRow: the table row instance

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.table import Table, TableRow
            >>> client = GeoboxClient()
            >>> table = client.get_table(uuid="12345678-1234-5678-1234-567812345678")
            or
            >>> table = Table.get_table(client, uuid="12345678-1234-5678-1234-567812345678")

            >>> row = TableRow.get_row(table, row_id=1)
        """
        param = {
            'f': 'json',
            'user_id': user_id
        }
        endpoint = urljoin(table.endpoint, f'rows/')
        return cls._get_detail(table.api, endpoint, uuid=row_id, params=param, factory_func=lambda api, item: TableRow(table, data=item))


    def update(self, **kwargs) -> Dict:
        """
        Update a row

        Keyword Args:
            fields to update

        Returns:
            Dict: updated row data

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> table = client.get_table(uuid="12345678-1234-5678-1234-567812345678")
            >>> row = table.get_row(row_id=1)
            >>> row.update(field1='new_value')
        """
        super()._update(self.endpoint, self.data, clean=False)
        return self.data


    def delete(self) -> None:
        """
        Delete a row

        Returns: 
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> table = client.get_table(uuid="12345678-1234-5678-1234-567812345678")
            >>> row = table.get_row(row_id=1)
            >>> row.delete()
        """
        super()._delete(self.endpoint)


    def to_async(self, async_client: 'AsyncGeoboxClient') -> 'AsyncTableRow':
        """
        Switch to async version of the table row instance to have access to the async methods

        Args:
            async_client (AsyncGeoboxClient): The async version of the GeoboxClient instance for making requests.

        Returns:
            AsyncTableRow: the async instance of the TableRow.

        Example:
            >>> from geobox import Geoboxclient
            >>> from geobox.aio import AsyncGeoboxClient
            >>> client = GeoboxClient()
            >>> table = client.get_table(uuid="12345678-1234-5678-1234-567812345678")
            >>> row = table.get_row(row_id=1)
            >>> async with AsyncGeoboxClient() as async_client:
            >>>     async_row = row.to_async(async_client)
        """
        from .aio.table import AsyncTableRow

        async_table = self.table.to_async(async_client=async_client)
        return AsyncTableRow(table=async_table, data=self.data)



class TableField(Base):

    def __init__(self, 
        table: 'Table',
        data_type: 'FieldType',
        field_id: int = None,
        data: Optional[Dict] = {},
    ):
        """
        Constructs all the necessary attributes for the Field object.

        Args:
            table (Table): The table that the field belongs to.
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
        return f"TableField(id={self.id}, name={self.name}, data_type={self.data_type})"

        
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
    def create_field(cls, 
        table: 'Table', 
        name: str, 
        data_type: 'FieldType', 
        data: Dict = {},
    ) -> 'TableField':
        """
        Create a new field

        Args:
            table (Table): field's table
            name (str): name of the field
            data_type (FieldType): type of the field
            data (Dict, optional): the data of the field

        Returns:
            Field: the created field object

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.table import Table
            >>> from geobox.field import Field
            >>> client = GeoboxClient()
            >>> table = client.get_table(uuid="12345678-1234-5678-1234-567812345678")
            >>> field = Field.create_field(client, table=table, name='test', data_type=FieldType.Integer)
        """
        data.update({
            "name": name,
            "datatype": data_type.value
        })
        endpoint = urljoin(table.endpoint, 'fields/')
        return super()._create(table.api, endpoint, data, factory_func=lambda api, item: TableField(table, data_type, item['id'], item))


    def delete(self) -> None:
        """
        Delete the field.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.field import TableField
            >>> client = GeoboxClient()
            >>> table = client.get_table(uuid="12345678-1234-5678-1234-567812345678")
            >>> field = table.get_field(name='test')
            >>> field.delete()
        """
        super()._delete(self.endpoint)
        self.field_id = None


    def update(self, **kwargs) -> Dict:
        """
        Update the field.

        Keyword Args:
            name (str): The name of the field.
            display_name (str): The display name of the field.
            description (str): The description of the field.
            domain (Dict): the domain of the field
            hyperlink (bool): the hyperlink field.

        Returns:
            Dict: The updated data.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.field import TableField
            >>> client = GeoboxClient()
            >>> table = client.get_table(uuid="12345678-1234-5678-1234-567812345678")
            >>> field = table.get_field(name='test')
            >>> field.update(name="my_field", display_name="My Field", description="My Field Description")
        """       
        data = {
            "name": kwargs.get('name'),
            "display_name": kwargs.get('display_name'),
            "description": kwargs.get('description'),
            "domain": kwargs.get('domain'),
            "hyperlink": kwargs.get('hyperlink')
        }
        return super()._update(self.endpoint, data)


    def update_domain(self, 
        range_domain: Dict = None, 
        list_domain: Dict = None,
    ) -> Dict:
        """
        Update field domian values

        Args:
            range_domain (Dict): a dictionary with min and max keys.
            list_domain (Dict): a dictionary containing the domain codes and values.

        Returns:
            Dict: the updated field domain

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> field = client.get_table(uuid="12345678-1234-5678-1234-567812345678").get_fields()[0]
            >>> range_d = {'min': 1, 'max': 10}
            >>> field.update_domain(range_domain = range_d)
            or 
            >>> list_d = {'1': 'value1', '2': 'value2'}
            >>> field.update_domain(list_domain=list_d)
        """
        if not self.domain:
            self.domain = {'min': None, 'max': None, 'items': {}}

        if range_domain:
            self.domain['min'] = range_domain['min']
            self.domain['max'] = range_domain['max']

        if list_domain:
            self.domain['items'] = {**self.domain['items'], **list_domain}

        self.update(domain=self.domain)
        return self.domain


    def to_async(self, async_client: 'AsyncGeoboxClient') -> 'AsyncTableField':
        """
        Switch to async version of the field instance to have access to the async methods

        Args:
            async_client (AsyncGeoboxClient): The async version of the GeoboxClient instance for making requests.

        Returns:
            AsyncField: the async instance of the field.

        Example:
            >>> from geobox import Geoboxclient
            >>> from geobox.aio import AsyncGeoboxClient
            >>> client = GeoboxClient()
            >>> table = client.get_table(uuid="12345678-1234-5678-1234-567812345678")
            >>> field = table.get_field(name='test')
            >>> async with AsyncGeoboxClient() as async_client:
            >>>     async_field = field.to_async(async_client)
        """
        from .aio.table import AsyncTableField

        async_table = self.table.to_async(async_client=async_client)
        return AsyncTableField(table=async_table, data_type=self.data_type, field_id=self.field_id, data=self.data)



class Table(Base):

    BASE_ENDPOINT = 'tables/'

    def __init__(self, 
        api: 'GeoboxClient', 
        uuid: str,
        data: Optional[Dict] = {}):
        """
        Initialize a table instance.

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            uuid (str): The unique identifier for the table.
            data (Dict): The response data of the table.
        """
        super().__init__(api, uuid=uuid, data=data)


    @classmethod
    def get_tables(cls, api: 'GeoboxClient', **kwargs) -> Union[List['Table'], int]:
        """
        Get list of tables with optional filtering and pagination.

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.

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
            List[Table] | int: A list of table instances or the total number of tables.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.table import Table
            >>> client = GeoboxClient()
            >>> tables = client.get_tables(q="name LIKE '%My table%'")
            or
            >>> tables = Table.get_tables(client, q="name LIKE '%My table%'")
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
        return super()._get_list(api, cls.BASE_ENDPOINT, params, factory_func=lambda api, item: Table(api, item['uuid'], item))
    

    @classmethod
    def create_table(cls,
        api: 'GeoboxClient', 
        name: str, 
        display_name: Optional[str] = None, 
        description: Optional[str] = None, 
        temporary: bool = False,
        fields: Optional[List[Dict]] = None,
    ) -> 'Table':
        """
        Create a new table.

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            name (str): The name of the Table.
            display_name (str, optional): The display name of the table.
            description (str, optional): The description of the table.
            temporary (bool, optional): Whether to create a temporary tables. default: False
            fields (List[Dict], optional): raw table fields. you can use create_field method for simpler and safer field addition. required dictionary keys: name, datatype

        Returns:
            Table: The newly created table instance.

        Raises:
            ValidationError: If the table data is invalid.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.table import Table
            >>> client = GeoboxClient()
            >>> table = client.create_table(name="my_table")
            or
            >>> table = Table.create_table(client, name="my_table")            
        """
        data = {
            "name": name,
            "display_name": display_name,
            "description": description,
            "temporary": temporary,
            "fields": fields,
        }
        return super()._create(api, cls.BASE_ENDPOINT, data, factory_func=lambda api, item: Table(api, item['uuid'], item))

    
    @classmethod
    def get_table(cls, api: 'GeoboxClient', uuid: str, user_id: int = None) -> 'Table':
        """
        Get a table by UUID.

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            uuid (str): The UUID of the table to get.
            user_id (int): Specific user. privileges required.

        Returns:
            Table: The Table object.

        Raises:
            NotFoundError: If the table with the specified UUID is not found.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.table import Table
            >>> client = GeoboxClient()
            >>> table = client.get_table(uuid="12345678-1234-5678-1234-567812345678")
            or
            >>> table = Table.get_table(client, uuid="12345678-1234-5678-1234-567812345678")
        """
        params = {
            'f': 'json',
            'user_id': user_id,
        }
        return super()._get_detail(api, cls.BASE_ENDPOINT, uuid, params, factory_func=lambda api, item: Table(api, item['uuid'], item))


    @classmethod
    def get_table_by_name(cls, api: 'GeoboxClient', name: str, user_id: int = None) -> Union['Table', None]:
        """
        Get a table by name

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            name (str): the name of the table to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            Table | None: returns the table if a table matches the given name, else None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.table import Table
            >>> client = GeoboxClient()
            >>> table = client.get_table_by_name(name='test')
            or
            >>> table = Table.get_table_by_name(client, name='test')
        """
        tables = cls.get_tables(api, q=f"name = '{name}'", user_id=user_id)
        if tables and tables[0].name == name:
            return tables[0]
        else:
            return None


    def update(self, **kwargs) -> Dict:
        """
        Update the table.

        Keyword Args:
            name (str): The name of the table.
            display_name (str): The display name of the table.
            description (str): The description of the table.

        Returns:
            Dict: The updated table data.

        Raises:
            ValidationError: If the table data is invalid.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.table import Table
            >>> client = GeoboxClient()
            >>> table = Table.get_table(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> table.update_table(display_name="New Display Name")
        """
        data = {
            "name": kwargs.get('name'),
            "display_name": kwargs.get('display_name'),   
            "description": kwargs.get('description'),
        }
        return super()._update(self.endpoint, data)
    

    def delete(self) -> None:
        """
        Delete the Table.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.table import Table
            >>> client = GeoboxClient()
            >>> table = Table.get_table(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> table.delete()
        """
        super()._delete(self.endpoint)


    @property
    def settings(self) -> Dict:
        """
        Get the table's settings.
        
        Returns:
            Dict: The table settings.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.table import Table
            >>> client = GeoboxClient()
            >>> table = Table.get_table(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>> setting = table.setting
        """
        return super()._get_settings(endpoint=self.endpoint)
    

    def update_settings(self, settings: Dict) -> Dict:
        """
        Update the settings

        settings (Dict): settings dictionary

        Returns:
            Dict: updated settings

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> table1 = client.get_table(uuid="12345678-1234-5678-1234-567812345678")
            >>> table2 = client.get_table(uuid="12345678-1234-5678-1234-567812345678")
            >>> table1.update_settings(table2.settings)
        """
        return super()._set_settings(self.endpoint, settings)


    def get_fields(self) -> List['TableField']:
        """
        Get all fields of the table.
        
        Returns:
            List[TableField]: A list of Field instances representing the table's fields.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.table import Table
            >>> client = GeoboxClient()
            >>> table = Table.get_table(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>> fields = table.get_fields()
        """
        endpoint = urljoin(self.endpoint, 'fields/')
        return super()._get_list(api=self.api, 
            endpoint=endpoint,
            factory_func=lambda api, item: TableField(table=self, data_type=FieldType(item['datatype']), field_id=item['id'], data=item))


    def get_field(self, field_id: int) -> 'TableField':
        """
        Get a specific field by ID.
        
        Args:
            field_id (int, optional): The ID of the field to retrieve.

        Returns:
            TableField: The requested field instance.
            
        Raises:
            NotFoundError: If the field with the specified ID is not found. 

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.table import Table
            >>> client = GeoboxClient()
            >>> table = Table.get_table(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>> field = table.get_field(field_id=1)
        """        
        field = next((f for f in self.get_fields() if f.id == field_id), None)
        if not field:
            raise NotFoundError(f'Field with ID {field_id} not found in table {self.name}')
            
        return field


    def get_field_by_name(self, name: str) -> 'TableField':
        """
        Get a specific field by name.
        
        Args:
            name (str): The name of the field to retrieve.

        Returns:
            TableField: The requested field instance.
            
        Raises:
            NotFoundError: If the field with the specified name is not found. 

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.table import Table
            >>> client = GeoboxClient()
            >>> table = Table.get_table(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>> field = table.get_field_by_name(name='test')
        """        
        field = next((f for f in self.get_fields() if f.name == name), None)
        if not field:
            raise NotFoundError(f"Field with name '{name}' not found in table {self.name}")
            
        return field


    def add_field(self, name: str, data_type: 'FieldType', data: Dict = {}) -> 'TableField':
        """
        Add a new field to the table.
        
        Args:
            name (str): The name of the new field.
            data_type (FieldType): The data type of the new field.
            data (Dict, optional): Additional field properties (display_name, description, etc.).
            
        Returns:
            Field: The newly created field instance.
            
        Raises:
            ValidationError: If the field data is invalid.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.table import Table
            >>> client = GeoboxClient()
            >>> table = Table.get_table(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>> field = table.add_field(name="new_field", data_type=FieldType.String)
        """
        return TableField.create_field(table=self, name=name, data_type=data_type, data=data)


    def calculate_field(self, 
        target_field: str, 
        expression: str, 
        q: Optional[str] = None, 
        search: Optional[str] = None, 
        search_fields: Optional[str] = None, 
        row_ids: Optional[str] = None, 
        run_async: bool = True, 
        user_id: Optional[int] = None,
    ) -> Union['Task', Dict]:
        """
        Calculate values for a field based on an expression.
        
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
            >>> from geobox import GeoboxClient
            >>> from geobox.table import Table
            >>> client = GeoboxClient()
            >>> table = Table.get_table(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>> task = table.calculate_field(target_field="target_field", 
            ...     expression="expression", 
            ...     q="name like 'my_layer'", 
            ...     row_ids=[1, 2, 3], 
            ...     run_async=True)
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
        response = self.api.post(endpoint, data, is_json=False)
        if run_async:
            task = Task.get_task(self.api, response.get('task_id'))
            return task

        return response


    def get_rows(self, **kwargs) -> List['TableRow']:
        """
        Query rows of a table

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
            List[TableRow]: list of table rows objects

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.table import Table
            >>> client = GeoboxClient()
            >>> table = client.get_table(uuid="12345678-1234-5678-1234-567812345678")
            or
            >>> table = Table.get_table(client, uuid="12345678-1234-5678-1234-567812345678")

            >>> rows = table.get_rows()
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

        return super()._get_list(api=self.api,
            endpoint=endpoint,
            params=params,
            factory_func=lambda api, item: TableRow(self, item))


    def get_row(self, 
        row_id: int, 
        user_id: Optional[int] = None,
    ) -> 'TableRow':
        """
        Get a row by its id

        Args:
            row_id (int): the row id
            user_id (int, optional): specific user. privileges required.

        Returns:
            TanbleRow: the table row instance

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.table import Table
            >>> client = GeoboxClient()
            >>> table = client.get_table(uuid="12345678-1234-5678-1234-567812345678")
            or
            >>> table = Table.get_table(client, uuid="12345678-1234-5678-1234-567812345678")

            >>> row = table.get_row(row_id=1)
        """
        return TableRow.get_row(self, row_id, user_id)


    def create_row(self, **kwargs) -> 'TableRow':
        """
        Create a new row in the table.

        Each keyword argument represents a field value for the row, where:
            - The keyword is the field name
            - The value is the field value

        Keyword Args: 
            **kwargs: Arbitrary field values matching the table schema.

        Returns:
            TableRow: created table row instance

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.table import Table
            >>> client = GeoboxClient()
            >>> table = client.get_table(uuid="12345678-1234-5678-1234-567812345678")
            or
            >>> table = Table.get_table(client, uuid="12345678-1234-5678-1234-567812345678")

            >>> row = table.create_row(
            ...     field1=value1
            ... )
        """
        return TableRow.create_row(self, **kwargs)


    def import_rows(self, 
        file: 'File',
        *,
        file_encoding: str = "utf-8",
        input_dataset: Optional[str] = None,
        delimiter: str = ',',
        has_header: bool = True,
        report_errors: bool = False,
        bulk_insert: bool = True,
    ) -> 'Task':
        """
        Import rows from a CSV file into a table
        
        Args:
            file (File): file object to import.
            file_encoding (str, optional): Character encoding of the input file. default: utf-8
            input_dataset (str, optional): Name of the dataset in the input file.
            delimiter (str, optional): the delimiter of the dataset. default: ,
            has_header (bool, optional): Whether the file has header or not. default: True
            report_errors (bool, optional): Whether to report import errors. default: False
            bulk_insert (bool, optional): 
            
        Returns:
            Task: The task instance of the import operation.
            
        Raises:
            ValidationError: If the import parameters are invalid.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.table import Table
            >>> client = GeoboxClient()
            >>> table = Table.get_table(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>> file = client.get_file(uuid="12345678-1234-5678-1234-567812345678")
            >>> task = table.import_rows(
            ...     file=file,
            ... )
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
        response = self.api.post(endpoint, data, is_json=False)
        task = Task.get_task(self.api, response.get('task_id'))
        return task


    def export_rows(self,
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
    ) -> Union['Task', str]:
        """
        Export rows of a table to a file
        
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
            Task | Dict: The task instance of the export operation (run_async=True) or the export result (run_async=False)
            
        Raises:
            ValidationError: If the export parameters are invalid.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.table import Table
            >>> client = GeoboxClient()
            >>> table = Table.get_table(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>> file = client.get_file(uuid="12345678-1234-5678-1234-567812345678")
            >>> task = table.export_rows(
            ...     file=file,
            ... )
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
        response = self.api.post(endpoint, data, is_json=False)
        if run_async:
            task = Task.get_task(self.api, response.get('task_id'))
            return task

        return response


    def share(self, users: List['User']) -> None:
        """
        Shares the table with specified users.

        Args:
            users (List[User]): The list of user objects to share the table with.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient             
            >>> from geobox.table import Table
            >>> client = GeoboxClient()
            >>> table = Table.get_table(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> users = client.search_users(search='John')
            >>> table.share(users=users)
        """
        super()._share(self.endpoint, users)
    

    def unshare(self, users: List['User']) -> None:
        """
        Unshares the table with specified users.

        Args:
            users (List[User]): The list of user objects to unshare the table with.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient             
            >>> from geobox.table import Table
            >>> client = GeoboxClient()
            >>> table = Table.get_table(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> users = client.search_users(search='John')
            >>> table.unshare(users=users)
        """
        super()._unshare(self.endpoint, users)


    def get_shared_users(self, search: str = None, skip: int = 0, limit: int = 10) -> List['User']:
        """
        Retrieves the list of users the table is shared with.

        Args:
            search (str, optional): The search query.
            skip (int, optional): The number of users to skip.
            limit (int, optional): The maximum number of users to retrieve.

        Returns:
            List[User]: The list of shared users.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.table import Table
            >>> client = GeoboxClient()
            >>> table = Table.get_table(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> table.get_shared_users(search='John', skip=0, limit=10)
        """
        params = {
            'search': search,
            'skip': skip,
            'limit': limit
        }
        return super()._get_shared_users(self.endpoint, params)


    def to_async(self, async_client: 'AsyncGeoboxClient') -> 'AsyncTable':
        """
        Switch to async version of the table instance to have access to the async methods

        Args:
            async_client (AsyncGeoboxClient): The async version of the GeoboxClient instance for making requests.

        Returns:
            AsyncTable: the async instance of the table.

        Example:
            >>> from geobox import Geoboxclient
            >>> from geobox.aio import AsyncGeoboxClient
            >>> client = GeoboxClient()
            >>> table = Table.get_table(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> async with AsyncGeoboxClient() as async_client:
            >>>     async_table = table.to_async(async_client)
        """
        from .aio.table import AsyncTable

        return AsyncTable(api=async_client, uuid=self.uuid, data=self.data)
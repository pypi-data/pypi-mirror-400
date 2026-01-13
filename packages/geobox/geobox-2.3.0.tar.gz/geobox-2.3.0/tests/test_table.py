import pytest
from unittest.mock import patch

from geobox.aio.table import AsyncTableField, AsyncTableRow
from geobox.enums import FieldType
from geobox.exception import NotFoundError
from geobox.file import File
from geobox.table import Table, TableField, TableRow
from geobox.task import Task
from geobox.user import User

def test_init(api, mock_table_data):
    table = Table(api, mock_table_data['uuid'], mock_table_data)
    assert table.name == mock_table_data['name']
    assert table.uuid == mock_table_data['uuid']
    assert table.data == mock_table_data
    assert table.endpoint == f'{Table.BASE_ENDPOINT}{table.uuid}/'


def test_get_tables(api, mock_table_data):
    api.get.return_value = [mock_table_data, mock_table_data]
    tables = Table.get_tables(api)
    api.get.assert_called_once_with(f'{Table.BASE_ENDPOINT}?f=json&include_settings=False&return_count=False&skip=0&limit=10&shared=False')
    assert len(tables) == 2
    assert type(tables[0]) == Table
    assert tables[0].data == mock_table_data


def test_create_table(api, mock_table_data, mock_table_field_data):
    api.post.return_value = mock_table_data
    table = Table.create_table(api,
        name=mock_table_data['name'],
        display_name=mock_table_data['display_name'],
        description=mock_table_data['description'],
        temporary=mock_table_data['temporary'],
        fields=[mock_table_field_data])
    api.post.assert_called_once_with(Table.BASE_ENDPOINT, {'name': 'test', 'temporary': False, 'fields': [mock_table_field_data]})
    assert type(table) == Table
    assert table.uuid == mock_table_data['uuid']
    assert table.data == mock_table_data


def test_get_table(api, mock_table_data):
    api.get.return_value = mock_table_data
    table = Table.get_table(api, uuid=mock_table_data['uuid'])
    api.get.assert_called_once_with(f"{Table.BASE_ENDPOINT}{mock_table_data['uuid']}/?f=json")
    assert type(table) == Table
    assert table.uuid == mock_table_data['uuid']
    assert table.data == mock_table_data


def test_get_table_by_name(api, mock_table_data):
    api.get.return_value = [mock_table_data]
    table = Table.get_table_by_name(api, name=mock_table_data['name'])
    api.get.assert_called_once_with(f"{Table.BASE_ENDPOINT}?f=json&include_settings=False&q=name+%3D+%27test%27&return_count=False&skip=0&limit=10&shared=False")
    assert type(table) == Table
    assert table.uuid == mock_table_data['uuid']
    assert table.data == mock_table_data
    # not found
    table = Table.get_table_by_name(api, name='not_found')
    assert table == None


def test_update(api, mock_table_data):
    table = Table(api, mock_table_data['uuid'], mock_table_data)
    updated_data = {
        **mock_table_data,
        'name': 'update',
        'display_name': 'update display name',
        'description': 'update description',
    }

    api.put.return_value = updated_data
    result = table.update(name='update', display_name='update display name', description='update description')
    api.put.assert_called_once_with(table.endpoint, {'name': 'update', 'display_name': 'update display name', 'description': 'update description'})
    assert updated_data == result
    assert table.data == updated_data


def test_delete(api, mock_table_data):
    table = Table(api, mock_table_data['uuid'], mock_table_data)
    endpoint = table.endpoint
    table.delete()
    api.delete.assert_called_once_with(endpoint)
    assert table.uuid is None
    assert table.endpoint is None


def test_get_settings(api, mock_table_data):
    table = Table(api, mock_table_data['uuid'], mock_table_data)
    api.get.return_value = mock_table_data['settings']
    settings = table.settings
    assert settings == mock_table_data['settings']
    api.get.assert_called_once_with(f"{table.endpoint}settings/?f=json")


def test_update_settings(api, mock_table_data):
    table = Table(api, mock_table_data['uuid'], mock_table_data)
    api.get.return_value = mock_table_data['settings']
    settings = table.settings
    settings['edit_settings']['allow_delete'] = False
    api.put.return_value = settings
    result = table.update_settings(settings)
    assert result == settings


def test_get_fields(api, mock_table_data, mock_table_field_data):
    table = Table(api, mock_table_data['uuid'], mock_table_data)
    api.get.return_value = [mock_table_field_data, mock_table_field_data]
    fields = table.get_fields()
    assert len(fields) == 2
    assert type(fields[0]) == TableField
    assert fields[0].data == mock_table_field_data


def test_get_field(api, mock_table_data, mock_table_field_data):
    table = Table(api, mock_table_data['uuid'], mock_table_data)
    api.get.return_value = [mock_table_field_data, mock_table_field_data]
    field = table.get_field(field_id=mock_table_field_data['id'])
    assert type(field) == TableField
    assert field.data == mock_table_field_data


def test_get_field_by_name(api, mock_table_data, mock_table_field_data):
    table = Table(api, mock_table_data['uuid'], mock_table_data)
    api.get.return_value = [mock_table_field_data, mock_table_field_data]
    field = table.get_field_by_name(mock_table_field_data['name'])
    assert type(field) == TableField
    assert field.data == mock_table_field_data


def test_get_field_not_found_error(api, mock_table_data, mock_table_field_data):
    table = Table(api, mock_table_data['uuid'], mock_table_data)
    api.get.return_value = [mock_table_field_data, mock_table_field_data]
    with pytest.raises(NotFoundError):
        table.get_field(10)

    with pytest.raises(NotFoundError):
        table.get_field_by_name('t')


def test_add_field(api, mock_table_data, mock_table_field_data):
    table = Table(api, mock_table_data['uuid'], mock_table_data)
    api.post.return_value = mock_table_field_data
    field = table.add_field(name='field1', data_type=FieldType.String)
    assert type(field) == TableField
    assert field.data == mock_table_field_data


def test_calculate_field(api, mock_table_data, mock_success_task_data):
    table = Table(api, mock_table_data['uuid'], mock_table_data)
    api.get.return_value = mock_success_task_data
    task = table.calculate_field(target_field='field1', expression='upper( field1  )')
    assert type(task) == Task
    api.post.assert_called_once_with(f"{table.endpoint}calculateField/", {'target_field': 'field1', 'expression': 'upper( field1  )', 'run_async': True}, is_json=False)


def test_calculate_field_sync(api, mock_table_data):
    table = Table(api, mock_table_data['uuid'], mock_table_data)
    api.post.return_value = {'result': 'value'}
    result = table.calculate_field(target_field='field1', expression='upper( field1  )', run_async=False)
    assert result == {'result': 'value'}
    api.post.assert_called_once_with(f"{table.endpoint}calculateField/", {'target_field': 'field1', 'expression': 'upper( field1  )', 'run_async': False}, is_json=False)


def test_get_rows(api, mock_table_data, mock_table_row_data):
    table = Table(api, mock_table_data['uuid'], mock_table_data)
    api.get.return_value = [mock_table_row_data, mock_table_row_data]
    rows = table.get_rows()
    assert len(rows) == 2
    assert type(rows[0]) == TableRow
    assert rows[0].data == mock_table_row_data
    api.get.assert_called_once_with(f"{table.endpoint}rows/?f=json&skip=0&limit=100&return_count=False")


def test_get_row(api, mock_table_data, mock_table_row_data):
    table = Table(api, mock_table_data['uuid'], mock_table_data)
    api.get.return_value = mock_table_row_data
    row = table.get_row(row_id=mock_table_row_data['id'])
    assert type(row) == TableRow
    assert row.data == mock_table_row_data
    api.get.assert_called_once_with(f"{row.endpoint}?f=json")


def test_create_row(api, mock_table_data, mock_table_row_data):
    table = Table(api, mock_table_data['uuid'], mock_table_data)
    api.post.return_value = mock_table_row_data
    row = table.create_row(field1='test')
    assert type(row) == TableRow
    assert row.data == mock_table_row_data
    api.post.assert_called_once_with(f"{table.endpoint}rows/", {'field1': 'test'})


def test_import_rows(api, mock_table_data, mock_file_data, mock_success_task_data):
    table = Table(api, mock_table_data['uuid'], mock_table_data)
    file = File(api, mock_file_data['uuid'], mock_file_data)
    api.post.return_value = {'task_id': mock_success_task_data['uuid']}
    api.get.return_value = mock_success_task_data
    task = table.import_rows(file)
    assert type(task) == Task
    assert task.data == mock_success_task_data
    api.post.assert_called_once_with(f"{table.endpoint}import-csv/", {'file_uuid': '2228a886-870e-4a0a-8e3b-6f51efee2eae', 'file_encoding': 'utf-8', 'input_dataset': 'world_boundaries.shp', 'delimiter': ',', 'has_header': True, 'report_errors': False, 'bulk_insert': True}, is_json=False)
    api.get.assert_called_once_with(task.endpoint)


def test_export_rows(api, mock_table_data, mock_success_task_data):
    table = Table(api, mock_table_data['uuid'], mock_table_data)
    api.post.return_value = {'task_id': mock_success_task_data['uuid']}
    api.get.return_value = mock_success_task_data
    task = table.export_rows('test')
    assert type(task) == Task
    assert task.data == mock_success_task_data
    api.post.assert_called_once_with(f"{table.endpoint}export/", {'out_filename': 'test', 'out_format': 'CSV', 'zipped': False, 'run_async': True}, is_json=False)
    api.get.assert_called_once_with(task.endpoint)


def test_export_rows_sync(api, mock_table_data):
    table = Table(api, mock_table_data['uuid'], mock_table_data)
    api.post.return_value = {'result': 'value'}
    result = table.export_rows('test', run_async=False)
    assert result == {'result': 'value'}
    api.post.assert_called_once_with(f"{table.endpoint}export/", {'out_filename': 'test', 'out_format': 'CSV', 'zipped': False, 'run_async': False}, is_json=False)


def test_row_repr(api, mock_table_data, mock_table_row_data):
    table = Table(api, mock_table_data['uuid'], mock_table_data)
    row = TableRow(table, mock_table_row_data)
    assert repr(row) == f"TableRow(id={row.id}, table_name={table.name})"


def test_row_update(api, mock_table_data, mock_table_row_data):
    table = Table(api, mock_table_data['uuid'], mock_table_data)
    row = TableRow(table, mock_table_row_data)
    updated_data = mock_table_row_data
    updated_data['properties'] = {
        'field1': 'updated row'
    }
    api.put.return_value = updated_data
    result = row.update(field1='updated row')
    assert row.properties['field1'] == 'updated row'
    api.put.assert_called_once_with(row.endpoint, {'id': 40, 'properties': {'field1': 'updated row'}})
    assert result == updated_data
    

def test_row_delete(api, mock_table_data, mock_table_row_data):
    table = Table(api, mock_table_data['uuid'], mock_table_data)
    row = TableRow(table, mock_table_row_data)
    endpoint = row.endpoint
    row.delete()
    api.delete.assert_called_once_with(endpoint)


def test_row_to_async(api, async_api, mock_table_data, mock_table_row_data):
    table = Table(api, uuid=mock_table_data['uuid'], data=mock_table_data)
    row = TableRow(table, mock_table_row_data)
    async_instance = row.to_async(async_api)
    assert async_instance.api == async_api
    assert type(async_instance) == AsyncTableRow


def test_field_data_type(api, mock_table_data, mock_table_field_data):
    table = Table(api, mock_table_data['uuid'], mock_table_data)
    field = TableField(table, data_type=FieldType.String, field_id=mock_table_field_data['id'], data=mock_table_field_data)
    assert field.datatype == FieldType.String


def test_field_init_datatype_error(api, mock_table_data, mock_table_field_data):
    table = Table(api, mock_table_data['uuid'], mock_table_data)
    with pytest.raises(ValueError):
        TableField(table, data_type='string', field_id=mock_table_field_data['id'], data=mock_table_field_data)


def test_field_repr(api, mock_table_data, mock_table_field_data):
    table = Table(api, mock_table_data['uuid'], mock_table_data)
    field = TableField(table, data_type=FieldType.String, field_id=mock_table_field_data['id'], data=mock_table_field_data)
    assert repr(field) == f'TableField(id={field.id}, name={field.name}, data_type={field.data_type})'


def test_field_get_domain(api, mock_table_data, mock_table_field_data):
    table = Table(api, mock_table_data['uuid'], mock_table_data)
    field = TableField(table, data_type=FieldType.String, field_id=mock_table_field_data['id'], data=mock_table_field_data)
    assert field.domain == mock_table_field_data['domain']
    

def test_field_set_domain(api, mock_table_data, mock_table_field_data):
    table = Table(api, mock_table_data['uuid'], mock_table_data)
    field = TableField(table, data_type=FieldType.String, field_id=mock_table_field_data['id'], data=mock_table_field_data)
    domain = {
        'min': 10,
        'max': 20,
        'items': {}
    }
    field.domain = domain
    assert field.domain == domain


def test_field_delete(api, mock_table_data, mock_table_field_data):
    table = Table(api, mock_table_data['uuid'], mock_table_data)
    field = TableField(table, data_type=FieldType.String, field_id=mock_table_field_data['id'], data=mock_table_field_data)
    endpoint = field.endpoint
    field.delete()
    api.delete.assert_called_once_with(endpoint)


def test_field_update(api, mock_table_data, mock_table_field_data):
    table = Table(api, mock_table_data['uuid'], mock_table_data)
    field = TableField(table, data_type=FieldType.String, field_id=mock_table_field_data['id'], data=mock_table_field_data)
    updated_data = {
        'name': 'updated_name',
        'display_name': 'updated display name',
        'description': 'updated description',
        'domain': {'min': 11, 'max': 22},
        'hyperlink': True
    }
    api.put.return_value = updated_data
    result = field.update(**updated_data)
    for key, value in updated_data.items():
        assert field.data[key] == value

    assert result == updated_data
    api.put.assert_called_once_with(field.endpoint, updated_data)


def test_field_update_domain(api, mock_table_data, mock_table_field_data):
    table = Table(api, mock_table_data['uuid'], mock_table_data)
    field = TableField(table, data_type=FieldType.String, field_id=mock_table_field_data['id'], data=mock_table_field_data)
    field.domain = None
    domain = {'min': 15, 'max': 25, 'items': {'1': 'test1', '2': 'test2'}}
    api.put.return_value = {
        **mock_table_field_data,
        **domain
    }
    result = field.update_domain(range_domain={'min': 15, 'max': 25}, list_domain={'1': 'test1', '2': 'test2'})
    assert result == field.domain


def test_field_to_async(api, async_api, mock_table_data, mock_table_field_data):
    table = Table(api, uuid=mock_table_data['uuid'], data=mock_table_data)
    field = TableField(table, data_type=FieldType.String, field_id=mock_table_field_data['id'], data=mock_table_field_data)
    async_instance = field.to_async(async_api)
    assert async_instance.api == async_api
    assert type(async_instance) == AsyncTableField


def test_share(api, mock_table_data, mock_user_data):
    """Test file sharing."""
    with patch.object(api, 'post'):
        table = Table(api, uuid=mock_table_data['uuid'], data=mock_table_data)
        users = [
            User(api, user_id=mock_user_data['1']['id'], data=mock_user_data['1']),
            User(api, user_id=mock_user_data['2']['id'], data=mock_user_data['2'])
        ]
        table.share(users=users)
        api.post.assert_called_once_with(
            f'{table.endpoint}share/',
            {'user_ids': [1, 2]}, is_json=False
        )


def test_unshare(api, mock_table_data, mock_user_data):
    """Test file unsharing."""
    with patch.object(api, 'post'):
        table = Table(api, uuid=mock_table_data['uuid'], data=mock_table_data)
        users = [
            User(api, user_id=mock_user_data['1']['id'], data=mock_user_data['1']),
            User(api, user_id=mock_user_data['2']['id'], data=mock_user_data['2'])
        ]
        table.unshare(users=users)
        
        # Verify the API call
        api.post.assert_called_once_with(
            f'{table.endpoint}unshare/',
            {'user_ids': [1, 2]}, is_json=False
        )


def test_get_shared_users(api, mock_table_data, mock_user_data):
    """Test getting shared users."""
    mock_response = [
        mock_user_data['1'],
        mock_user_data['2']
    ]
    
    with patch.object(api, 'get', return_value=mock_response):
        table = Table(api, uuid=mock_table_data['uuid'], data=mock_table_data)
        result = table.get_shared_users(search='user', limit=2)

        api.get.assert_called_once_with(
            f'{table.endpoint}shared-with-users/?search=user&skip=0&limit=2'
        )

        assert len(result) == 2
        assert result[0].first_name == 'test 1'
        assert result[0].last_name == 'test 1'
        assert result[1].first_name == 'test 2'
        assert result[1].last_name == 'test 2'


def test_to_async(api, async_api, mock_table_data):
    table = Table(api, uuid=mock_table_data['uuid'], data=mock_table_data)
    async_instance = table.to_async(async_api)
    assert async_instance.api == async_api
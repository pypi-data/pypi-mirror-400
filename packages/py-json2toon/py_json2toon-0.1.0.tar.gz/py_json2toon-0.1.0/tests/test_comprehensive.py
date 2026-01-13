"""Comprehensive test suite for json2toon package."""
import pytest
from json2toon import ToonEncoder, ToonDecoder, ToonConfig


def _roundtrip(data, config: ToonConfig | None = None):
    """Encode then decode using the provided config."""
    encoder = ToonEncoder(config)
    decoder = ToonDecoder(config)
    toon = encoder.encode(data)
    return decoder.decode(toon)


@pytest.mark.parametrize(
    "data",
    [
        {'name': 'John', 'age': 30},
        {'numbers': [1, 2, 3]},
        {'strings': ['a', 'b', 'c']},
        {
            'users': [
                {'id': 1, 'name': 'Alice'},
                {'id': 2, 'name': 'Bob'}
            ]
        },
        {'items': [{'key': 'value'}]},
        {'nested': {'a': {'b': 'c'}}},
        {
            'text': 'hello',
            'num': 42,
            'bool': True,
            'null': None,
            'array': [1, 2]
        },
        {'level1': {'level2': {'level3': {'level4': 'deep'}}}},
    ],
)
def test_core_conversions(data):
    assert _roundtrip(data) == data


@pytest.mark.parametrize(
    "data",
    [
        {'items': []},
        {'data': {}},
        {'text': ''},
        {'text': 'Hello "world" with \'quotes\''},
        {'text': 'Line 1\nLine 2'},
        {'big': 999999999999, 'small': -999999999},
        {'pi': 3.14159, 'e': 2.71828},
        {'emoji': '🎉', 'chinese': '你好'},
        {'items': [1, 'text', {'key': 'value'}]},
        {'users': [{'name': 'Alice', 'info': {'age': 30}}]},
    ],
)
def test_edge_cases(data):
    assert _roundtrip(data) == data


@pytest.mark.parametrize(
    "config",
    [
        ToonConfig(),
        ToonConfig(quote_strings=True),
        ToonConfig(indent_size=4),
        ToonConfig(table_separator='|'),
        ToonConfig(quote_strings=True, indent_size=4, table_separator='|'),
    ],
)
def test_configurations(config: ToonConfig):
    test_data = {
        'users': [
            {'id': 1, 'name': 'Alice'},
            {'id': 2, 'name': 'Bob'}
        ],
        'items': ['a', 'b', 'c']
    }

    assert _roundtrip(test_data, config) == test_data


@pytest.mark.parametrize(
    "data",
    [
        {'items': [1, 2, 3]},
        {'items': ['a', 'b', 'c']},
        {'users': [{'name': 'Alice'}]},
        {
            'list1': [{'a': 1}],
            'list2': [{'b': 2}],
        },
        {'users': [{'name': 'Alice', 'info': {'age': 30}}]},
        {'data': [1, 'text', {'nested': 'value'}]},
    ],
)
def test_list_formats(data):
    assert _roundtrip(data) == data

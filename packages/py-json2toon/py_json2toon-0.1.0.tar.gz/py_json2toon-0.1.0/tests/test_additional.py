"""Additional edge case tests."""
import pytest
from json2toon import ToonEncoder, ToonDecoder


@pytest.fixture()
def encoder():
    return ToonEncoder()


@pytest.fixture()
def decoder():
    return ToonDecoder()


@pytest.mark.parametrize(
    "data",
    [
        {'path': 'C\\Users\\file.txt'},
        {'text': 'Line 1\n\nLine 3'},
        {'text': 'Tab\there'},
        {'text': 'Path: C\\test\\n\\file.txt\nNew line'},
        {'text': 'This is a very long string ' * 50},
        {'data': [[[[[1, 2, 3]]]]]},
        {'level1': {'level2': [{'level3': {'level4': [1, 2, 3]}}]}},
        {
            'true_val': True,
            'false_val': False,
            'in_array': [True, False],
        },
        {
            'null_val': None,
            'in_array': [None, 1, None],
            'in_dict': {'a': None, 'b': 'value'},
        },
    ],
)
def test_additional_edge_cases(encoder: ToonEncoder, decoder: ToonDecoder, data):
    toon = encoder.encode(data)
    assert decoder.decode(toon) == data

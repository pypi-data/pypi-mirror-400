#!/usr/bin/env python3
"""Test for the ee.string module."""
import json
from typing import Any, Dict
import unittest

import unittest
import le
from le import apitestcase


def make_expression_graph(
    function_invocation_value: Dict[str, Any]
) -> Dict[str, Any]:
  return {
      'result': '0',
      'values': {'0': {'functionInvocationValue': function_invocation_value}},
  }


class StringTest(apitestcase.ApiTestCase):

  def test_string(self):
    """Verifies basic behavior of ee.String."""
    bare_string = le.String('foo')
    self.assertEqual('foo', bare_string.encode())

    computed = le.String('foo').cat('bar')
    self.assertIsInstance(computed, le.String)
    self.assertEqual(le.ApiFunction.lookup('String.cat'), computed.func)
    self.assertEqual({
        'string1': le.String('foo'),
        'string2': le.String('bar')
    }, computed.args)

    # Casting a non-string ComputedObject.
    obj = le.Number(1).add(1)
    s = le.String(obj)
    self.assertIsInstance(s, le.String)
    self.assertEqual(le.ApiFunction.lookup('String'), s.func)
    self.assertEqual({'input': obj}, s.args)

  def test_internals(self):
    """Test eq(), ne() and hash()."""
    a = le.String('one')
    b = le.String('two')
    c = le.String('one')

    self.assertEqual(a, a)
    self.assertNotEqual(a, b)
    self.assertEqual(a, c)
    self.assertNotEqual(b, c)
    self.assertNotEqual(hash(a), hash(b))

  def test_bad_arg(self):
    message = r'Invalid argument specified for ee\.String\(\): 123'
    with self.assertRaisesRegex(le.EEException, message):
      le.String(123)  # pytype: disable=wrong-arg-types

  def test_cat(self):
    expect = make_expression_graph({
        'arguments': {
            'string1': {'constantValue': 'foo'},
            'string2': {'constantValue': 'bar'},
        },
        'functionName': 'String.cat',
    })
    expression = le.String('foo').cat('bar')
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.String('foo').cat(string2='bar')
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_compare_to(self):
    expect = make_expression_graph({
        'arguments': {
            'string1': {'constantValue': 'a'},
            'string2': {'constantValue': 'b'},
        },
        'functionName': 'String.compareTo',
    })
    expression = le.String('a').compareTo('b')
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.String('a').compareTo(string2='b')
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_decode_json(self):
    expect = make_expression_graph({
        'arguments': {'string': {'constantValue': 'a'}},
        'functionName': 'String.decodeJSON',
    })
    expression = le.String('a').decodeJSON()
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_encode_json(self):
    expect = make_expression_graph({
        'arguments': {'object': {'constantValue': 'a'}},
        'functionName': 'String.encodeJSON',
    })
    expression = le.String.encodeJSON('a')
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_equals(self):
    expect = make_expression_graph({
        'arguments': {
            'reference': {'constantValue': 'a'},
            'target': {'constantValue': 'b'},
        },
        'functionName': 'String.equals',
    })
    expression = le.String('a').equals('b')
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.String('a').equals(target='b')
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_index(self):
    expect = make_expression_graph({
        'functionName': 'String.index',
        'arguments': {
            'target': {'constantValue': 'abc'},
            'pattern': {'constantValue': 'b'},
        },
    })
    expression = le.String('abc').index('b')
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.String('abc').index(pattern='b')
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_length(self):
    expect = make_expression_graph({
        'functionName': 'String.length',
        'arguments': {'string': {'constantValue': 'abc'}},
    })
    expression = le.String('abc').length()
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_match(self):
    expect = make_expression_graph({
        'functionName': 'String.match',
        'arguments': {
            'input': {'constantValue': 'abc'},
            'regex': {'constantValue': 'bc'},
        },
    })
    expression = le.String('abc').match('bc')
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.String('abc').match(regex='bc')
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_replace(self):
    expect = make_expression_graph({
        'functionName': 'String.replace',
        'arguments': {
            'input': {'constantValue': 'abc'},
            'regex': {'constantValue': 'bc'},
            'replacement': {'constantValue': '123'},
        },
    })
    expression = le.String('abc').replace('bc', '123')
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.String('abc').replace(regex='bc', replacement='123')
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_rindex(self):
    expect = make_expression_graph({
        'functionName': 'String.rindex',
        'arguments': {
            'target': {'constantValue': 'abc'},
            'pattern': {'constantValue': 'b'},
        },
    })
    expression = le.String('abc').rindex('b')
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.String('abc').rindex(pattern='b')
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_slice(self):
    expect = make_expression_graph({
        'functionName': 'String.slice',
        'arguments': {
            'start': {'constantValue': -3},
            'string': {'constantValue': 'abc'},
        },
    })
    expression = le.String('abc').slice(-3)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.String('abc').slice(start=-3)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_slice2(self):
    expect = make_expression_graph({
        'functionName': 'String.slice',
        'arguments': {
            'string': {'constantValue': 'abc'},
            'start': {'constantValue': 1},
            'end': {'constantValue': 2},
        },
    })
    expression = le.String('abc').slice(1, 2)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.String('abc').slice(start=1, end=2)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_split(self):
    expect = make_expression_graph({
        'functionName': 'String.split',
        'arguments': {
            'regex': {'constantValue': 'b'},
            'string': {'constantValue': 'abc'},
        },
    })
    expression = le.String('abc').split('b')
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.String('abc').split(regex='b')
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_to_lower_case(self):
    expect = make_expression_graph({
        'functionName': 'String.toLowerCase',
        'arguments': {'string': {'constantValue': 'Abc'}},
    })
    expression = le.String('Abc').toLowerCase()
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_to_upper_case(self):
    expect = make_expression_graph({
        'functionName': 'String.toUpperCase',
        'arguments': {'string': {'constantValue': 'Abc'}},
    })
    expression = le.String('Abc').toUpperCase()
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_trim(self):
    expect = make_expression_graph({
        'functionName': 'String.trim',
        'arguments': {'string': {'constantValue': 'abc'}},
    })
    expression = le.String('abc').trim()
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  @unittest.mock.patch.object(le.ComputedObject, 'encode')
  def test_encode_opt_params(self, mock_encode):
    a_string = le.String(le.Dictionary({'a': 'a_string'}).get('a'))

    mock_encoder = unittest.mock.Mock()
    a_string.encode(opt_encoder=mock_encoder)

    mock_encode.assert_called_once_with(mock_encoder)

  @unittest.mock.patch.object(le.ComputedObject, 'encode_cloud_value')
  def test_encode_cloud_value_opt_params(self, mock_encode_cloud_value):
    a_string = le.String(le.Dictionary({'a': 'a_string'}).get('a'))

    mock_encoder = unittest.mock.Mock()
    a_string.encode_cloud_value(opt_encoder=mock_encoder)

    mock_encode_cloud_value.assert_called_once_with(mock_encoder)


if __name__ == '__main__':
  unittest.main()

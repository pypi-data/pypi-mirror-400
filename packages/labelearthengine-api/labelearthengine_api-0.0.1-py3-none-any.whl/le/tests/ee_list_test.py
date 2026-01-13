#!/usr/bin/env python3
"""Test for the ee.list module."""
import json
from typing import Any, Dict

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


class ListTest(apitestcase.ApiTestCase):

  def test_list(self):
    """Verifies basic behavior of ee.List."""
    l = le.List([1, 2, 3])
    self.assertEqual([1, 2, 3], le.Serializer(False)._encode(l))

    computed = le.List([1, 2, 3]).slice(0)    # pylint: disable=no-member
    self.assertIsInstance(computed, le.List)
    self.assertEqual(le.ApiFunction.lookup('List.slice'), computed.func)
    self.assertEqual(
        {
            'list': le.List([1, 2, 3]),
            'start': le.Number(0),
            'end': None,
            'step': None,
        },
        computed.args,
    )

  def test_empty(self):
    expect = {'result': '0', 'values': {'0': {'constantValue': []}}}
    self.assertEqual(expect, json.loads(le.List(tuple()).serialize()))
    self.assertEqual(expect, json.loads(le.List([]).serialize()))

  def test_single(self):
    expect = {'result': '0', 'values': {'0': {'constantValue': [42]}}}
    self.assertEqual(expect, json.loads(le.List(tuple([42])).serialize()))
    self.assertEqual(expect, json.loads(le.List([42]).serialize()))

  def test_mapping(self):
    lst = le.List(['foo', 'bar'])
    body = lambda s: le.String(s).cat('bar')
    mapped = lst.map(body)

    self.assertIsInstance(mapped, le.List)
    self.assertEqual(le.ApiFunction.lookup('List.map'), mapped.func)
    self.assertEqual(lst, mapped.args['list'])

    # Need to do a serialized comparison for the function body because
    # variables returned from CustomFunction.variable() do not implement
    # __eq__.
    sig = {
        'returns': 'Object',
        'args': [{'name': '_MAPPING_VAR_0_0', 'type': 'Object'}]
    }
    expected_function = le.CustomFunction(sig, body)
    self.assertEqual(expected_function.serialize(),
                     mapped.args['baseAlgorithm'].serialize())
    self.assertEqual(
        expected_function.serialize(for_cloud_api=True),
        mapped.args['baseAlgorithm'].serialize(for_cloud_api=True))

  def test_internals(self):
    """Test eq(), ne() and hash()."""
    a = le.List([1, 2])
    b = le.List([2, 1])
    c = le.List([1, 2])

    self.assertTrue(a.__eq__(a))
    self.assertFalse(a.__eq__(b))
    self.assertTrue(a.__eq__(c))
    self.assertTrue(b.__ne__(c))
    self.assertNotEqual(a.__hash__(), b.__hash__())
    self.assertEqual(a.__hash__(), c.__hash__())

  def test_add(self):
    expect = make_expression_graph({
        'arguments': {
            'element': {'constantValue': 'b'},
            'list': {'constantValue': ['a']},
        },
        'functionName': 'List.add',
    })
    expression = le.List(['a']).add('b')
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.List(['a']).add(element='b')
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_cat(self):
    expect = make_expression_graph({
        'arguments': {
            'list': {'constantValue': [1]},
            'other': {'constantValue': [2]},
        },
        'functionName': 'List.cat',
    })
    expression = le.List([1]).cat([2])
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.List([1]).cat(other=[2])
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_contains(self):
    expect = make_expression_graph({
        'arguments': {
            'list': {'constantValue': [1]},
            'element': {'constantValue': 2},
        },
        'functionName': 'List.contains',
    })
    expression = le.List([1]).contains(2)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.List([1]).contains(element=2)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_containsAll(self):
    expect = make_expression_graph({
        'arguments': {
            'list': {'constantValue': [1, 2]},
            'other': {'constantValue': [3, 4]},
        },
        'functionName': 'List.containsAll',
    })
    expression = le.List([1, 2]).containsAll([3, 4])
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.List([1, 2]).containsAll(other=[3, 4])
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_distinct(self):
    expect = make_expression_graph({
        'arguments': {
            'list': {'constantValue': [1]},
        },
        'functionName': 'List.distinct',
    })
    expression = le.List([1]).distinct()
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.List([1]).distinct()
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_equals(self):
    expect = make_expression_graph({
        'arguments': {
            'list': {'constantValue': [1]},
            'other': {'constantValue': [2]},
        },
        'functionName': 'List.equals',
    })
    expression = le.List([1]).equals([2])
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.List([1]).equals(other=[2])
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_filter(self):
    expect = make_expression_graph({
        'arguments': {
            'list': {'constantValue': [1]},
            'filter': {
                'functionInvocationValue': {
                    'functionName': 'Filter.greaterThan',
                    'arguments': {
                        'leftField': {'constantValue': 'item'},
                        'rightValue': {'constantValue': 3},
                    },
                }
            },
        },
        'functionName': 'List.filter',
    })
    a_filter = le.Filter.gt('item', 3)
    expression = le.List([1]).filter(a_filter)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.List([1]).filter(filter=a_filter)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_flatten(self):
    expect = make_expression_graph({
        'arguments': {
            'list': {'constantValue': [1]},
        },
        'functionName': 'List.flatten',
    })
    expression = le.List([1]).flatten()
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_frequency(self):
    expect = make_expression_graph({
        'arguments': {
            'list': {'constantValue': [1]},
            'element': {'constantValue': 2},
        },
        'functionName': 'List.frequency',
    })
    expression = le.List([1]).frequency(2)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.List([1]).frequency(element=2)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_get(self):
    expect = make_expression_graph({
        'arguments': {
            'list': {'constantValue': [1]},
            'index': {'constantValue': 2},
        },
        'functionName': 'List.get',
    })
    expression = le.List([1]).get(2)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.List([1]).get(index=2)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_getArray(self):
    expect = make_expression_graph({
        'arguments': {
            'list': {'constantValue': [1]},
            'index': {'constantValue': 2},
        },
        'functionName': 'List.getArray',
    })
    expression = le.List([1]).getArray(2)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.List([1]).getArray(index=2)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_getGeometry(self):
    expect = make_expression_graph({
        'arguments': {
            'list': {'constantValue': [1]},
            'index': {'constantValue': 2},
        },
        'functionName': 'List.getGeometry',
    })
    expression = le.List([1]).getGeometry(2)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.List([1]).getGeometry(index=2)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_getNumber(self):
    expect = make_expression_graph({
        'arguments': {
            'list': {'constantValue': [1]},
            'index': {'constantValue': 2},
        },
        'functionName': 'List.getNumber',
    })
    expression = le.List([1]).getNumber(2)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.List([1]).getNumber(index=2)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_get_string(self):
    expect = make_expression_graph({
        'arguments': {
            'list': {'constantValue': [1]},
            'index': {'constantValue': 2},
        },
        'functionName': 'List.getString',
    })
    expression = le.List([1]).getString(2)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.List([1]).getString(index=2)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_index_of(self):
    expect = make_expression_graph({
        'arguments': {
            'list': {'constantValue': [1]},
            'element': {'constantValue': 2},
        },
        'functionName': 'List.indexOf',
    })
    expression = le.List([1]).indexOf(2)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.List([1]).indexOf(element=2)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_index_of_sublist(self):
    expect = make_expression_graph({
        'arguments': {
            'list': {'constantValue': [1]},
            'target': {'constantValue': [2, 3]},
        },
        'functionName': 'List.indexOfSublist',
    })
    expression = le.List([1]).indexOfSublist([2, 3])
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.List([1]).indexOfSublist(target=[2, 3])
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_insert(self):
    expect = make_expression_graph({
        'arguments': {
            'list': {'constantValue': [1]},
            'index': {'constantValue': 2},
            'element': {'constantValue': 3},
        },
        'functionName': 'List.insert',
    })
    expression = le.List([1]).insert(2, 3)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.List([1]).insert(index=2, element=3)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  # TODO: test_iterate

  def test_join(self):
    expect = make_expression_graph({
        'arguments': {
            'list': {'constantValue': [1]},
            'separator': {'constantValue': 'a'},
        },
        'functionName': 'List.join',
    })
    expression = le.List([1]).join('a')
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.List([1]).join(separator='a')
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_last_index_of_sublist(self):
    expect = make_expression_graph({
        'arguments': {
            'list': {'constantValue': [1]},
            'target': {'constantValue': [2, 3]},
        },
        'functionName': 'List.lastIndexOfSubList',
    })
    expression = le.List([1]).lastIndexOfSubList([2, 3])
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.List([1]).lastIndexOfSubList(target=[2, 3])
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_length(self):
    expect = make_expression_graph({
        'arguments': {
            'list': {'constantValue': [1]},
        },
        'functionName': 'List.length',
    })
    expression = le.List([1]).length()
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  # TODO: test_map

  def test_reduce(self):
    expect = make_expression_graph({
        'arguments': {
            'list': {'constantValue': [1]},
            'reducer': {
                'functionInvocationValue': {
                    'functionName': 'Reducer.count',
                    'arguments': {},
                }
            },
        },
        'functionName': 'List.reduce',
    })
    reducer = le.Reducer.count()
    expression = le.List([1]).reduce(reducer)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.List([1]).reduce(reducer=reducer)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_remove(self):
    expect = make_expression_graph({
        'arguments': {
            'list': {'constantValue': [1]},
            'element': {'constantValue': 2},
        },
        'functionName': 'List.remove',
    })
    expression = le.List([1]).remove(2)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.List([1]).remove(element=2)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_remove_all(self):
    expect = make_expression_graph({
        'arguments': {
            'list': {'constantValue': [1]},
            'other': {'constantValue': [1, 2]},
        },
        'functionName': 'List.removeAll',
    })
    expression = le.List([1]).removeAll([1, 2])
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.List([1]).removeAll(other=[1, 2])
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_repeat(self):
    expect = make_expression_graph({
        'arguments': {
            'value': {'constantValue': 1},
            'count': {'constantValue': 2},
        },
        'functionName': 'List.repeat',
    })
    expression = le.List.repeat(1, 2)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.List.repeat(value=1, count=2)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_replace(self):
    expect = make_expression_graph({
        'arguments': {
            'list': {'constantValue': [1]},
            'oldval': {'constantValue': 2},
            'newval': {'constantValue': 3},
        },
        'functionName': 'List.replace',
    })
    expression = le.List([1]).replace(2, 3)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.List([1]).replace(oldval=2, newval=3)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_replaceAll(self):
    expect = make_expression_graph({
        'arguments': {
            'list': {'constantValue': [1]},
            'oldval': {'constantValue': 2},
            'newval': {'constantValue': 3},
        },
        'functionName': 'List.replaceAll',
    })
    expression = le.List([1]).replaceAll(2, 3)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.List([1]).replaceAll(oldval=2, newval=3)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_reverse(self):
    expect = make_expression_graph({
        'arguments': {
            'list': {'constantValue': [1]},
        },
        'functionName': 'List.reverse',
    })
    expression = le.List([1]).reverse()
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_rotate(self):
    expect = make_expression_graph({
        'arguments': {
            'list': {'constantValue': [1]},
            'distance': {'constantValue': 2},
        },
        'functionName': 'List.rotate',
    })
    expression = le.List([1]).rotate(2)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.List([1]).rotate(distance=2)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_sequence(self):
    expect = make_expression_graph({
        'arguments': {
            'start': {'constantValue': 1},
            'end': {'constantValue': 2},
            'step': {'constantValue': 3},
            'count': {'constantValue': 4},
        },
        'functionName': 'List.sequence',
    })
    expression = le.List.sequence(1, 2, 3, 4)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.List.sequence(start=1, end=2, step=3, count=4)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_set(self):
    expect = make_expression_graph({
        'arguments': {
            'list': {'constantValue': [1]},
            'index': {'constantValue': 2},
            'element': {'constantValue': 3},
        },
        'functionName': 'List.set',
    })
    expression = le.List([1]).set(2, 3)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.List([1]).set(index=2, element=3)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_shuffle(self):
    expect = make_expression_graph({
        'arguments': {
            'list': {'constantValue': [1]},
            'seed': {'constantValue': 2},
        },
        'functionName': 'List.shuffle',
    })
    expression = le.List([1]).shuffle(2)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.List([1]).shuffle(seed=2)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_size(self):
    expect = make_expression_graph({
        'arguments': {
            'list': {'constantValue': [1]},
        },
        'functionName': 'List.size',
    })
    expression = le.List([1]).size()
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_slice(self):
    expect = make_expression_graph({
        'arguments': {
            'list': {'constantValue': [1]},
            'start': {'constantValue': 2},
            'end': {'constantValue': 3},
            'step': {'constantValue': 4},
        },
        'functionName': 'List.slice',
    })
    expression = le.List([1]).slice(2, 3, 4)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.List([1]).slice(start=2, end=3, step=4)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_sort(self):
    expect = make_expression_graph({
        'arguments': {
            'list': {'constantValue': [1]},
            'keys': {'constantValue': [2]},
        },
        'functionName': 'List.sort',
    })
    expression = le.List([1]).sort([2])
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.List([1]).sort(keys=[2])
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_splice(self):
    expect = make_expression_graph({
        'arguments': {
            'list': {'constantValue': [1]},
            'start': {'constantValue': 2},
            'count': {'constantValue': 3},
            'other': {'constantValue': [4]},
        },
        'functionName': 'List.splice',
    })
    expression = le.List([1]).splice(2, 3, [4])
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.List([1]).splice(start=2, count=3, other=[4])
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_swap(self):
    expect = make_expression_graph({
        'arguments': {
            'list': {'constantValue': [1]},
            'pos1': {'constantValue': 2},
            'pos2': {'constantValue': 3},
        },
        'functionName': 'List.swap',
    })
    expression = le.List([1]).swap(2, 3)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.List([1]).swap(pos1=2, pos2=3)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_unzip(self):
    expect = make_expression_graph({
        'arguments': {
            'list': {'constantValue': [1]},
        },
        'functionName': 'List.unzip',
    })
    expression = le.List([1]).unzip()
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_zip(self):
    expect = make_expression_graph({
        'arguments': {
            'list': {'constantValue': [1]},
            'other': {'constantValue': [2]},
        },
        'functionName': 'List.zip',
    })
    expression = le.List([1]).zip([2])
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.List([1]).zip(other=[2])
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)


if __name__ == '__main__':
  unittest.main()

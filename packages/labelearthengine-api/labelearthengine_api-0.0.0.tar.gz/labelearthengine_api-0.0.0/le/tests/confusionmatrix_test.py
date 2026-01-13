#!/usr/bin/env python3
"""Tests for the ee.ConfusionMatrix module."""

import json
from typing import Any, Dict

import unittest
import le
from le import apitestcase


MATRIX = {
    'functionInvocationValue': {
        'functionName': 'ConfusionMatrix',
        'arguments': {
            'array': {
                'functionInvocationValue': {
                    'functionName': 'Array',
                    'arguments': {'values': {'constantValue': [[1]]}},
                }
            },
            'order': {'constantValue': [2]},
        },
    }
}


def make_expression_graph(
    function_invocation_value: Dict[str, Any],
) -> Dict[str, Any]:
  return {
      'result': '0',
      'values': {'0': {'functionInvocationValue': function_invocation_value}},
  }


class ConfusionMatrixTest(apitestcase.ApiTestCase):

  def test_init(self):
    array = le.Array([[0, 0], [0, 0]])
    order = le.List([2, 1])
    confusion_matrix = le.ConfusionMatrix(array, order)
    self.assertEqual({'value': 'fakeValue'}, confusion_matrix.getInfo())

    func = le.ApiFunction.lookup('ConfusionMatrix')
    self.assertEqual(func, confusion_matrix.func)
    self.assertFalse(confusion_matrix.isVariable())
    self.assertEqual({'array': array, 'order': order}, confusion_matrix.args)

  def test_init_order_literal(self):
    array = le.Array([[0, 0], [0, 0]])
    order = [2, 1]
    confusion_matrix = le.ConfusionMatrix(array, order)
    self.assertEqual({'value': 'fakeValue'}, confusion_matrix.getInfo())

    func = le.ApiFunction.lookup('ConfusionMatrix')
    self.assertEqual(func, confusion_matrix.func)
    self.assertFalse(confusion_matrix.isVariable())
    self.assertEqual(
        {'array': array, 'order': le.List(order)}, confusion_matrix.args
    )

  def test_init_no_order(self):
    array = le.Array([[0, 0], [0, 0]])
    confusion_matrix = le.ConfusionMatrix(array, None)
    self.assertEqual({'value': 'fakeValue'}, confusion_matrix.getInfo())

    func = le.ApiFunction.lookup('ConfusionMatrix')
    self.assertEqual(func, confusion_matrix.func)
    self.assertFalse(confusion_matrix.isVariable())
    self.assertEqual({'array': array}, confusion_matrix.args)

  def test_serialize(self):
    confusion_matrix = le.ConfusionMatrix(le.Array([[0, 0], [0, 0]]), [1, 2])
    result = json.loads(confusion_matrix.serialize())
    expected = {
        'result': '0',
        'values': {
            '1': {'constantValue': [0, 0]},
            '0': {
                'functionInvocationValue': {
                    'functionName': 'ConfusionMatrix',
                    'arguments': {
                        'array': {
                            'functionInvocationValue': {
                                'functionName': 'Array',
                                'arguments': {
                                    'values': {
                                        'arrayValue': {
                                            'values': [
                                                {'valueReference': '1'},
                                                {'valueReference': '1'},
                                            ]
                                        }
                                    }
                                },
                            }
                        },
                        'order': {'constantValue': [1, 2]},
                    },
                }
            },
        },
    }
    self.assertEqual(expected, result)

  def test_cast(self):
    array = le.Array([[0, 0], [0, 0]])
    order = le.List([2, 1])
    confusion_matrix = le.ConfusionMatrix(array, order)
    result = json.loads(le.ConfusionMatrix(confusion_matrix).serialize())
    expect = {
        'result': '0',
        'values': {
            '1': {'constantValue': [0, 0]},
            '0': {
                'functionInvocationValue': {
                    'functionName': 'ConfusionMatrix',
                    'arguments': {
                        'array': {
                            'functionInvocationValue': {
                                'functionName': 'Array',
                                'arguments': {
                                    'values': {
                                        'arrayValue': {
                                            'values': [
                                                {'valueReference': '1'},
                                                {'valueReference': '1'},
                                            ]
                                        }
                                    }
                                },
                            }
                        },
                        'order': {'constantValue': [2, 1]},
                    },
                }
            },
        },
    }
    self.assertEqual(expect, result)

  def test_accuracy(self):
    expect = make_expression_graph({
        'arguments': {'confusionMatrix': MATRIX},
        'functionName': 'ConfusionMatrix.accuracy',
    })
    expression = le.ConfusionMatrix(le.Array([[1]]), [2]).accuracy()
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_array(self):
    expect = make_expression_graph({
        'arguments': {'confusionMatrix': MATRIX},
        'functionName': 'ConfusionMatrix.array',
    })
    expression = le.ConfusionMatrix(le.Array([[1]]), [2]).array()
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_consumersAccuracy(self):
    expect = make_expression_graph({
        'arguments': {'confusionMatrix': MATRIX},
        'functionName': 'ConfusionMatrix.consumersAccuracy',
    })
    expression = le.ConfusionMatrix(le.Array([[1]]), [2]).consumersAccuracy()
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_fscore(self):
    expect = make_expression_graph({
        'arguments': {
            'confusionMatrix': MATRIX,
            'beta': {'constantValue': 3},
        },
        'functionName': 'ConfusionMatrix.fscore',
    })
    expression = le.ConfusionMatrix(le.Array([[1]]), [2]).fscore(3)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.ConfusionMatrix(le.Array([[1]]), [2]).fscore(beta=3)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_kappa(self):
    expect = make_expression_graph({
        'arguments': {'confusionMatrix': MATRIX},
        'functionName': 'ConfusionMatrix.kappa',
    })
    expression = le.ConfusionMatrix(le.Array([[1]]), [2]).kappa()
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_order(self):
    expect = make_expression_graph({
        'arguments': {'confusionMatrix': MATRIX},
        'functionName': 'ConfusionMatrix.order',
    })
    expression = le.ConfusionMatrix(le.Array([[1]]), [2]).order()
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_producersAccuracy(self):
    expect = make_expression_graph({
        'arguments': {'confusionMatrix': MATRIX},
        'functionName': 'ConfusionMatrix.producersAccuracy',
    })
    expression = le.ConfusionMatrix(le.Array([[1]]), [2]).producersAccuracy()
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)


if __name__ == '__main__':
  unittest.main()

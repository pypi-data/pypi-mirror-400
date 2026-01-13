#!/usr/bin/env python3
"""Test for the ee.filter module."""

import datetime
import json
from typing import Any, Dict

import unittest
import le
from le import apitestcase


def make_expression_graph(
    function_invocation_value: Dict[str, Any],
) -> Dict[str, Any]:
  return {
      'result': '0',
      'values': {'0': {'functionInvocationValue': function_invocation_value}},
  }


def max_error_expression(max_error: float) -> Dict[str, Any]:
  return {
      'functionInvocationValue': {
          'functionName': 'ErrorMargin',
          'arguments': {'value': {'constantValue': max_error}},
      }
  }


class FilterTest(apitestcase.ApiTestCase):

  def test_constructors(self):
    """Verifies that constructors understand valid parameters."""
    from_static_method = le.Filter.gt('foo', 1)
    from_computed_object = le.Filter(
        le.ApiFunction.call_('Filter.greaterThan', 'foo', 1))
    self.assertEqual(from_static_method, from_computed_object)

    copy = le.Filter(from_static_method)
    self.assertEqual(from_static_method, copy)

  def test_metadata(self):
    """Verifies that the metadata_() method works."""
    self.assertEqual(
        le.ApiFunction.call_('Filter.equals', 'x', 1),
        le.Filter.metadata_('x', 'equals', 1))
    self.assertEqual(
        le.Filter.metadata_('x', 'equals', 1), le.Filter.eq('x', 1))
    self.assertEqual(
        le.Filter.metadata_('x', 'EQUALS', 1), le.Filter.eq('x', 1))
    self.assertEqual(
        le.Filter.metadata_('x', 'not_equals', 1), le.Filter.neq('x', 1))
    self.assertEqual(
        le.Filter.metadata_('x', 'less_than', 1), le.Filter.lt('x', 1))
    self.assertEqual(
        le.Filter.metadata_('x', 'not_greater_than', 1), le.Filter.lte('x', 1))
    self.assertEqual(
        le.Filter.metadata_('x', 'greater_than', 1), le.Filter.gt('x', 1))
    self.assertEqual(
        le.Filter.metadata_('x', 'not_less_than', 1), le.Filter.gte('x', 1))

  def test_logical_combinations(self):
    """Verifies that the and() and or() methods work."""
    f1 = le.Filter.eq('x', 1)
    f2 = le.Filter.eq('x', 2)

    or_filter = le.Filter.Or(f1, f2)
    self.assertEqual(le.ApiFunction.call_('Filter.or', (f1, f2)), or_filter)

    and_filter = le.Filter.And(f1, f2)
    self.assertEqual(le.ApiFunction.call_('Filter.and', (f1, f2)), and_filter)

    self.assertEqual(
        le.ApiFunction.call_('Filter.or', (or_filter, and_filter)),
        le.Filter.Or(or_filter, and_filter))

  def test_date(self):
    """Verifies that date filters work."""
    d1 = datetime.datetime(2000, 1, 1)
    d2 = datetime.datetime(2001, 1, 1)
    instant_range = le.ApiFunction.call_('DateRange', d1, None)
    long_range = le.ApiFunction.call_('DateRange', d1, d2)

    instant_filter = le.Filter.date(d1)
    self.assertEqual(
        le.ApiFunction.lookup('Filter.dateRangeContains'), instant_filter.func)
    self.assertEqual({
        'leftValue': instant_range,
        'rightField': le.String('system:time_start')
    }, instant_filter.args)

    long_filter = le.Filter.date(d1, d2)
    self.assertEqual(
        le.ApiFunction.lookup('Filter.dateRangeContains'), long_filter.func)
    self.assertEqual({
        'leftValue': long_range,
        'rightField': le.String('system:time_start')
    }, long_filter.args)

  def test_bounds(self):
    """Verifies that geometry intersection filters work."""
    polygon = le.Geometry.Polygon(1, 2, 3, 4, 5, 6)
    self.assertEqual(
        le.ApiFunction.call_('Filter.intersects', '.all',
                             le.ApiFunction.call_('Feature', polygon)),
        le.Filter.geometry(polygon))

    # Collection-to-geometry promotion.
    collection = le.FeatureCollection('foo')
    feature = le.ApiFunction.call_(
        'Feature', le.ApiFunction.call_('Collection.geometry', collection))
    self.assertEqual(
        le.ApiFunction.call_('Filter.intersects', '.all', feature),
        le.Filter.geometry(collection))

    # Check the bounds() alias.
    self.assertEqual(
        le.ApiFunction.call_('Filter.intersects', '.all',
                             le.ApiFunction.call_('Feature', polygon)),
        le.Filter.bounds(polygon))

  def test_in_list(self):
    """Verifies that list membership filters work."""
    self.assertEqual(
        le.Filter.listContains(None, None, 'foo', [1, 2]),  # pytype: disable=attribute-error
        le.Filter.inList('foo', [1, 2]))

  def test_internals(self):
    """Test eq(), ne() and hash()."""
    a = le.Filter.eq('x', 1)
    b = le.Filter.eq('x', 2)
    c = le.Filter.eq('x', 1)

    self.assertEqual(a, a)
    self.assertNotEqual(a, b)
    self.assertEqual(a, c)
    self.assertNotEqual(b, c)
    self.assertNotEqual(hash(a), hash(b))

  def test_init_opt_params(self):
    result = le.Filter(opt_filter=[le.Filter.gt('prop', 1)]).serialize()
    self.assertIn('"functionName": "Filter.greaterThan"', result)

  def test_date_opt_params(self):
    result = le.Filter.date(
        start='1996-01-01T00:00', opt_end='2023-01-01T00:00'
    ).serialize()
    self.assertIn('"end": {"constantValue": "2023-01-01T00:00"}', result)

  def test_in_list_opt_params(self):
    result = le.Filter.inList(
        opt_leftField='lf',
        opt_rightValue='rv',
        opt_rightField='rf',
        opt_leftValue='lv',
    ).serialize()
    self.assertIn('"leftField": {"constantValue": "rf"}', result)
    self.assertIn('"leftValue": {"constantValue": "rv"}', result)
    self.assertIn('"rightField": {"constantValue": "lf"}', result)
    self.assertIn('"rightValue": {"constantValue": "lv"}', result)

  def test_bounds_opt_params(self):
    result = le.Filter.bounds(
        geometry=le.Geometry.Point(0, 0), opt_errorMargin=12345
    ).serialize()
    self.assertIn('"value": {"constantValue": 12345}', result)

  def test_and(self):
    expect = make_expression_graph({
        'arguments': {'filters': {'constantValue': []}},
        'functionName': 'Filter.and',
    })
    expression = le.Filter.And([])
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    # TODO: ee.Filter.And(filters=[]) does not currently work.

  def test_area(self):
    min_val = 1
    max_val = 2
    max_error = 3
    geometry_selector = 'a'
    expect = make_expression_graph({
        'arguments': {
            'min': {'constantValue': min_val},
            'max': {'constantValue': max_val},
            'maxError': max_error_expression(max_error),
            'geometrySelector': {'constantValue': geometry_selector},
        },
        'functionName': 'Filter.area',
    })
    expression = le.Filter.area(min_val, max_val, max_error, geometry_selector)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Filter.area(
        min=min_val,
        max=max_val,
        maxError=max_error,
        geometrySelector=geometry_selector,
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_calendar_range(self):
    start = 1
    end = 2
    field = 'year'
    expect = make_expression_graph({
        'arguments': {
            'start': {'constantValue': start},
            'end': {'constantValue': end},
            'field': {'constantValue': field},
        },
        'functionName': 'Filter.calendarRange',
    })
    expression = le.Filter.calendarRange(start, end, field)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Filter.calendarRange(start=start, end=end, field=field)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_contains(self):
    left_field = 'a'
    right_value = 1
    right_field = 'b'
    left_value = 2
    max_error = 3
    expect = make_expression_graph({
        'arguments': {
            'leftField': {'constantValue': left_field},
            'rightValue': {'constantValue': right_value},
            'rightField': {'constantValue': right_field},
            'leftValue': {'constantValue': left_value},
            'maxError': max_error_expression(max_error),
        },
        'functionName': 'Filter.contains',
    })
    expression = le.Filter.contains(
        left_field, right_value, right_field, left_value, max_error
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Filter.contains(
        leftField=left_field,
        rightValue=right_value,
        rightField=right_field,
        leftValue=left_value,
        maxError=max_error,
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_date_with_datetime(self):
    start = datetime.datetime(2024, 8, 3)
    end = datetime.datetime(2024, 8, 10)
    expect = make_expression_graph({
        'functionName': 'Filter.dateRangeContains',
        'arguments': {
            'leftValue': {
                'functionInvocationValue': {
                    'functionName': 'DateRange',
                    'arguments': {
                        'start': {
                            'functionInvocationValue': {
                                'functionName': 'Date',
                                'arguments': {
                                    'value': {'constantValue': 1722643200000}
                                },
                            }
                        },
                        'end': {
                            'functionInvocationValue': {
                                'functionName': 'Date',
                                'arguments': {
                                    'value': {'constantValue': 1723248000000}
                                },
                            }
                        },
                    },
                }
            },
            'rightField': {'constantValue': 'system:time_start'},
        },
    })
    expression = le.Filter.date(start, end)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Filter.date(start=start, end=end)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_date_range_contains(self):
    left_field = 'a'
    right_value = 1
    right_field = 'b'
    left_value = 2
    expect = make_expression_graph({
        'arguments': {
            'leftField': {'constantValue': left_field},
            'rightValue': {'constantValue': right_value},
            'rightField': {'constantValue': right_field},
            'leftValue': {'constantValue': left_value},
        },
        'functionName': 'Filter.dateRangeContains',
    })
    expression = le.Filter.dateRangeContains(
        left_field, right_value, right_field, left_value
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Filter.dateRangeContains(
        leftField=left_field,
        rightValue=right_value,
        rightField=right_field,
        leftValue=left_value,
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_day_of_year(self):
    start = 1
    end = 2
    expect = make_expression_graph({
        'arguments': {
            'start': {'constantValue': start},
            'end': {'constantValue': end},
        },
        'functionName': 'Filter.dayOfYear',
    })
    expression = le.Filter.dayOfYear(start, end)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Filter.dayOfYear(start=start, end=end)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_disjoint(self):
    left_field = 'a'
    right_value = 1
    right_field = 'b'
    left_value = 2
    max_error = 3
    expect = make_expression_graph({
        'arguments': {
            'leftField': {'constantValue': left_field},
            'rightValue': {'constantValue': right_value},
            'rightField': {'constantValue': right_field},
            'leftValue': {'constantValue': left_value},
            'maxError': max_error_expression(max_error),
        },
        'functionName': 'Filter.disjoint',
    })
    expression = le.Filter.disjoint(
        left_field, right_value, right_field, left_value, max_error
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Filter.disjoint(
        leftField=left_field,
        rightValue=right_value,
        rightField=right_field,
        leftValue=left_value,
        maxError=max_error,
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_eq(self):
    # ee.Filter.eq uses Equals and masks the actual eq call.
    name = 'a'
    value = 1
    expect = make_expression_graph({
        'arguments': {
            'leftField': {'constantValue': name},
            'rightValue': {'constantValue': value},
        },
        'functionName': 'Filter.equals',
    })
    expression = le.Filter.eq(name, value)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Filter.eq(name=name, value=value)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_equals(self):
    left_field = 'a'
    right_value = 1
    right_field = 'b'
    left_value = 2
    expect = make_expression_graph({
        'arguments': {
            'leftField': {'constantValue': left_field},
            'rightValue': {'constantValue': right_value},
            'rightField': {'constantValue': right_field},
            'leftValue': {'constantValue': left_value},
        },
        'functionName': 'Filter.equals',
    })
    expression = le.Filter.equals(
        left_field, right_value, right_field, left_value
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Filter.equals(
        leftValue=left_value,
        rightValue=right_value,
        leftField=left_field,
        rightField=right_field,
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_expression(self):
    expression_str = 'an expression'
    expect = make_expression_graph({
        'arguments': {
            'expression': {'constantValue': expression_str},
        },
        'functionName': 'Filter.expression',
    })
    expression = le.Filter.expression(expression_str)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Filter.expression(expression=expression_str)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_greater_than(self):
    left_field = 'a'
    right_value = 1
    right_field = 'b'
    left_value = 2
    expect = make_expression_graph({
        'arguments': {
            'leftField': {'constantValue': left_field},
            'rightValue': {'constantValue': right_value},
            'rightField': {'constantValue': right_field},
            'leftValue': {'constantValue': left_value},
        },
        'functionName': 'Filter.greaterThan',
    })
    expression = le.Filter.greaterThan(
        left_field, right_value, right_field, left_value
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Filter.greaterThan(
        leftValue=left_value,
        rightValue=right_value,
        leftField=left_field,
        rightField=right_field,
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_greater_than_or_equals(self):
    left_field = 'a'
    right_value = 1
    right_field = 'b'
    left_value = 2
    expect = make_expression_graph({
        'arguments': {
            'leftField': {'constantValue': left_field},
            'rightValue': {'constantValue': right_value},
            'rightField': {'constantValue': right_field},
            'leftValue': {'constantValue': left_value},
        },
        'functionName': 'Filter.greaterThanOrEquals',
    })
    expression = le.Filter.greaterThanOrEquals(
        left_field, right_value, right_field, left_value
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Filter.greaterThanOrEquals(
        leftValue=left_value,
        rightValue=right_value,
        leftField=left_field,
        rightField=right_field,
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_gt(self):
    # ee.Filter.gt uses greaterThan and masks the actual gt call.
    name = 'a'
    value = 1
    expect = make_expression_graph({
        'arguments': {
            'leftField': {'constantValue': name},
            'rightValue': {'constantValue': value},
        },
        'functionName': 'Filter.greaterThan',
    })
    expression = le.Filter.gt(name, value)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Filter.gt(name=name, value=value)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_gte(self):
    # gte is implemented as lt().not().
    name = 'a'
    value = 1
    expect = make_expression_graph({
        'functionName': 'Filter.not',
        'arguments': {
            'filter': {
                'functionInvocationValue': {
                    'functionName': 'Filter.lessThan',
                    'arguments': {
                        'leftField': {'constantValue': name},
                        'rightValue': {'constantValue': value},
                    },
                }
            }
        },
    })
    expression = le.Filter.gte(name, value)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Filter.gte(name=name, value=value)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  # TODO:  test_has_type

  def test_in_list_serialize(self):
    left_field = 'a'
    right_value = 1
    right_field = 'b'
    left_value = 2
    # Warning: inList swaps around args.
    expect = make_expression_graph({
        'arguments': {
            'rightField': {'constantValue': left_field},
            'leftValue': {'constantValue': right_value},
            'leftField': {'constantValue': right_field},
            'rightValue': {'constantValue': left_value},
        },
        # Note this is not 'inList'.
        'functionName': 'Filter.listContains',
    })
    expression = le.Filter.inList(
        left_field, right_value, right_field, left_value
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Filter.inList(
        leftValue=left_value,
        rightValue=right_value,
        leftField=left_field,
        rightField=right_field,
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_intersects(self):
    left_field = 'a'
    right_value = 1
    right_field = 'b'
    left_value = 2
    max_error = 3
    expect = make_expression_graph({
        'arguments': {
            'leftField': {'constantValue': left_field},
            'rightValue': {'constantValue': right_value},
            'rightField': {'constantValue': right_field},
            'leftValue': {'constantValue': left_value},
            'maxError': max_error_expression(max_error),
        },
        'functionName': 'Filter.intersects',
    })
    expression = le.Filter.intersects(
        left_field, right_value, right_field, left_value, max_error
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Filter.intersects(
        leftValue=left_value,
        rightValue=right_value,
        leftField=left_field,
        rightField=right_field,
        maxError=max_error,
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_is_contained(self):
    left_field = 'a'
    right_value = 1
    right_field = 'b'
    left_value = 2
    max_error = 3
    expect = make_expression_graph({
        'arguments': {
            'leftField': {'constantValue': left_field},
            'rightValue': {'constantValue': right_value},
            'rightField': {'constantValue': right_field},
            'leftValue': {'constantValue': left_value},
            'maxError': max_error_expression(max_error),
        },
        'functionName': 'Filter.isContained',
    })
    expression = le.Filter.isContained(
        left_field, right_value, right_field, left_value, max_error
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Filter.isContained(
        leftValue=left_value,
        rightValue=right_value,
        leftField=left_field,
        rightField=right_field,
        maxError=max_error,
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_less_than(self):
    left_field = 'a'
    right_value = 1
    right_field = 'b'
    left_value = 2
    expect = make_expression_graph({
        'arguments': {
            'leftField': {'constantValue': left_field},
            'rightValue': {'constantValue': right_value},
            'rightField': {'constantValue': right_field},
            'leftValue': {'constantValue': left_value},
        },
        'functionName': 'Filter.lessThan',
    })
    expression = le.Filter.lessThan(
        left_field, right_value, right_field, left_value
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Filter.lessThan(
        leftValue=left_value,
        rightValue=right_value,
        leftField=left_field,
        rightField=right_field,
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_less_than_or_equals(self):
    left_field = 'a'
    right_value = 1
    right_field = 'b'
    left_value = 2
    expect = make_expression_graph({
        'arguments': {
            'leftField': {'constantValue': left_field},
            'rightValue': {'constantValue': right_value},
            'rightField': {'constantValue': right_field},
            'leftValue': {'constantValue': left_value},
        },
        'functionName': 'Filter.lessThanOrEquals',
    })
    expression = le.Filter.lessThanOrEquals(
        left_field, right_value, right_field, left_value
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Filter.lessThanOrEquals(
        leftValue=left_value,
        rightValue=right_value,
        leftField=left_field,
        rightField=right_field,
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_list_contains(self):
    left_field = 'a'
    right_value = 1
    right_field = 'b'
    left_value = 2
    expect = make_expression_graph({
        'arguments': {
            'leftField': {'constantValue': left_field},
            'rightValue': {'constantValue': right_value},
            'rightField': {'constantValue': right_field},
            'leftValue': {'constantValue': left_value},
        },
        'functionName': 'Filter.listContains',
    })
    expression = le.Filter.listContains(
        left_field, right_value, right_field, left_value
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Filter.listContains(
        leftValue=left_value,
        rightValue=right_value,
        leftField=left_field,
        rightField=right_field,
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_lt(self):
    # Note: not Filter.lt.
    name = 'a'
    value = 1
    expect = make_expression_graph({
        'arguments': {
            'leftField': {'constantValue': name},
            'rightValue': {'constantValue': value},
        },
        'functionName': 'Filter.lessThan',
    })
    expression = le.Filter.lt(name, value)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Filter.lt(name=name, value=value)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_lte(self):
    # Note: not Filter.lte.
    name = 'a'
    value = 1
    expect = make_expression_graph({
        'functionName': 'Filter.not',
        'arguments': {
            'filter': {
                'functionInvocationValue': {
                    'functionName': 'Filter.greaterThan',
                    'arguments': {
                        'leftField': {'constantValue': name},
                        'rightValue': {'constantValue': value},
                    },
                }
            }
        },
    })
    expression = le.Filter.lte(name, value)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Filter.lte(name=name, value=value)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_max_difference(self):
    difference = 1
    left_field = 'a'
    right_value = 2
    right_field = 'b'
    left_value = 3
    expect = make_expression_graph({
        'arguments': {
            'difference': {'constantValue': difference},
            'leftField': {'constantValue': left_field},
            'rightValue': {'constantValue': right_value},
            'rightField': {'constantValue': right_field},
            'leftValue': {'constantValue': left_value},
        },
        'functionName': 'Filter.maxDifference',
    })
    expression = le.Filter.maxDifference(
        difference, left_field, right_value, right_field, left_value
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Filter.maxDifference(
        difference=difference,
        leftField=left_field,
        rightValue=right_value,
        rightField=right_field,
        leftValue=left_value,
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_neq(self):
    # Note: Filter.not paired with a Filter.equals.
    name = 'a'
    value = 1
    expect = make_expression_graph({
        'functionName': 'Filter.not',
        'arguments': {
            'filter': {
                'functionInvocationValue': {
                    'functionName': 'Filter.equals',
                    'arguments': {
                        'leftField': {'constantValue': 'a'},
                        'rightValue': {'constantValue': 1},
                    },
                }
            }
        },
    })
    expression = le.Filter.neq(name, value)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Filter.neq(name=name, value=value)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_not(self):
    name = 'air_temp'
    value = 2
    gt_filter = le.Filter.gt(name, value)
    expect = make_expression_graph({
        'functionName': 'Filter.not',
        'arguments': {
            'filter': {
                'functionInvocationValue': {
                    'functionName': 'Filter.greaterThan',
                    'arguments': {
                        'leftField': {'constantValue': name},
                        'rightValue': {'constantValue': value},
                    },
                }
            }
        },
    })
    expression = le.Filter.Not(gt_filter)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = gt_filter.Not()
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_not_equals(self):
    left_field = 'a'
    right_value = 1
    right_field = 'b'
    left_value = 2
    expect = make_expression_graph({
        'arguments': {
            'leftField': {'constantValue': left_field},
            'rightValue': {'constantValue': right_value},
            'rightField': {'constantValue': right_field},
            'leftValue': {'constantValue': left_value},
        },
        'functionName': 'Filter.notEquals',
    })
    expression = le.Filter.notEquals(
        left_field, right_value, right_field, left_value
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Filter.notEquals(
        leftValue=left_value,
        rightValue=right_value,
        leftField=left_field,
        rightField=right_field,
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_not_null(self):
    properties = ['a', 'b']
    expect = make_expression_graph({
        'arguments': {'properties': {'constantValue': properties}},
        'functionName': 'Filter.notNull',
    })
    expression = le.Filter.notNull(properties)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Filter.notNull(properties=properties)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_or_empty(self):
    expect = make_expression_graph({
        'arguments': {
            'filters': {'constantValue': []},
        },
        'functionName': 'Filter.or',
    })
    expression = le.Filter.Or()
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_or(self):
    name = 'air_temp'
    value = 2
    gt_filter = le.Filter.gt(name, value)
    expect = make_expression_graph({
        'functionName': 'Filter.or',
        'arguments': {
            'filters': {
                'arrayValue': {
                    'values': [{
                        'functionInvocationValue': {
                            'functionName': 'Filter.greaterThan',
                            'arguments': {
                                'leftField': {'constantValue': name},
                                'rightValue': {'constantValue': value},
                            },
                        }
                    }]
                }
            }
        },
    })

    expression = le.Filter.Or(gt_filter)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_range_contains(self):
    field = 'a'
    min_value = 1
    max_value = 2
    expect = make_expression_graph({
        'arguments': {
            'field': {'constantValue': field},
            'minValue': {'constantValue': min_value},
            'maxValue': {'constantValue': max_value},
        },
        'functionName': 'Filter.rangeContains',
    })
    expression = le.Filter.rangeContains(field, min_value, max_value)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Filter.rangeContains(
        field=field, minValue=min_value, maxValue=max_value
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_string_contains(self):
    left_field = 'a'
    right_value = 'b'
    right_field = 'c'
    left_value = 'd'
    expect = make_expression_graph({
        'arguments': {
            'leftField': {'constantValue': left_field},
            'rightValue': {'constantValue': right_value},
            'rightField': {'constantValue': right_field},
            'leftValue': {'constantValue': left_value},
        },
        'functionName': 'Filter.stringContains',
    })
    expression = le.Filter.stringContains(
        left_field, right_value, right_field, left_value
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Filter.stringContains(
        leftValue=left_value,
        rightValue=right_value,
        leftField=left_field,
        rightField=right_field,
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_string_ends_with(self):
    left_field = 'a'
    right_value = 'b'
    right_field = 'c'
    left_value = 'd'
    expect = make_expression_graph({
        'arguments': {
            'leftField': {'constantValue': left_field},
            'rightValue': {'constantValue': right_value},
            'rightField': {'constantValue': right_field},
            'leftValue': {'constantValue': left_value},
        },
        'functionName': 'Filter.stringEndsWith',
    })
    expression = le.Filter.stringEndsWith(
        left_field, right_value, right_field, left_value
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Filter.stringEndsWith(
        leftValue=left_value,
        rightValue=right_value,
        leftField=left_field,
        rightField=right_field,
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_string_starts_with(self):
    left_field = 'a'
    right_value = 'b'
    right_field = 'c'
    left_value = 'd'
    expect = make_expression_graph({
        'arguments': {
            'leftField': {'constantValue': left_field},
            'rightValue': {'constantValue': right_value},
            'rightField': {'constantValue': right_field},
            'leftValue': {'constantValue': left_value},
        },
        'functionName': 'Filter.stringStartsWith',
    })
    expression = le.Filter.stringStartsWith(
        left_field, right_value, right_field, left_value
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Filter.stringStartsWith(
        leftValue=left_value,
        rightValue=right_value,
        leftField=left_field,
        rightField=right_field,
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_within_distance(self):
    distance = 1
    left_field = 'a'
    right_value = 2
    right_field = 'b'
    left_value = 3
    max_error = 4
    expect = make_expression_graph({
        'arguments': {
            'distance': {'constantValue': distance},
            'leftField': {'constantValue': left_field},
            'rightValue': {'constantValue': right_value},
            'rightField': {'constantValue': right_field},
            'leftValue': {'constantValue': left_value},
            'maxError': max_error_expression(max_error),
        },
        'functionName': 'Filter.withinDistance',
    })
    expression = le.Filter.withinDistance(
        distance, left_field, right_value, right_field, left_value, max_error
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Filter.withinDistance(
        distance=distance,
        leftValue=left_value,
        rightValue=right_value,
        leftField=left_field,
        rightField=right_field,
        maxError=max_error,
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)


if __name__ == '__main__':
  unittest.main()

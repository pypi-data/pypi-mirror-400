#!/usr/bin/env python3
"""Test for the ee.feature module."""

import json
from typing import Any, Dict
from unittest import mock

import unittest
import le
from le import apitestcase


EPSG_4326 = 'EPSG:4326'

MAX_ERROR_GRAPH = {
    'functionInvocationValue': {
        'functionName': 'ErrorMargin',
        'arguments': {'value': {'constantValue': 10}},
    }
}
PROJ_GRAPH = {
    'functionInvocationValue': {
        'functionName': 'Projection',
        'arguments': {'crs': {'constantValue': EPSG_4326}},
    }
}
# ee.Feature(None).serialize())['values']['0']
FEATURE_NONE_GRAPH = {
    'functionInvocationValue': {
        'functionName': 'Feature',
        'arguments': {},
    }
}
# ee.Feature(None, {'a': 'b'}).serialize())['values']['0']
FEATURE_A_GRAPH = {
    'functionInvocationValue': {
        'functionName': 'Feature',
        'arguments': {'metadata': {'constantValue': {'a': 'b'}}},
    }
}


def right_maxerror_proj(function_name: str) -> Dict[str, Any]:
  return {
      'result': '0',
      'values': {
          '1': FEATURE_NONE_GRAPH,
          '0': {
              'functionInvocationValue': {
                  'arguments': {
                      'left': {'valueReference': '1'},
                      'right': {'valueReference': '1'},
                      'maxError': MAX_ERROR_GRAPH,
                      'proj': PROJ_GRAPH,
                  },
                  'functionName': 'Feature.' + function_name,
              }
          },
      },
  }


def make_expression_graph(
    function_invocation_value: Dict[str, Any],
) -> Dict[str, Any]:
  return {
      'result': '0',
      'values': {'0': {'functionInvocationValue': function_invocation_value}},
  }


class FeatureTest(apitestcase.ApiTestCase):

  def testConstructors(self):
    """Verifies that constructors understand valid parameters."""
    point = le.Geometry.Point(1, 2)
    from_geometry = le.Feature(point)
    self.assertEqual(le.ApiFunction('Feature'), from_geometry.func)
    self.assertEqual({'geometry': point, 'metadata': None}, from_geometry.args)

    from_null_geometry = le.Feature(None, {'x': 2})
    self.assertEqual(le.ApiFunction('Feature'), from_null_geometry.func)
    self.assertEqual({
        'geometry': None,
        'metadata': {
            'x': 2
        }
    }, from_null_geometry.args)

    computed_geometry = le.Geometry(le.ComputedObject(le.Function(), {'a': 1}))
    computed_properties = le.ComputedObject(le.Function(), {'b': 2})
    from_computed_one = le.Feature(computed_geometry)
    from_computed_both = le.Feature(computed_geometry, computed_properties)
    self.assertEqual(le.ApiFunction('Feature'), from_computed_one.func)
    self.assertEqual({
        'geometry': computed_geometry,
        'metadata': None
    }, from_computed_one.args)
    self.assertEqual(le.ApiFunction('Feature'), from_computed_both.func)
    self.assertEqual({
        'geometry': computed_geometry,
        'metadata': computed_properties
    }, from_computed_both.args)

    from_variable = le.Feature(le.CustomFunction.variable(None, 'foo'))
    self.assertIsInstance(from_variable, le.Feature)

    result = from_variable.encode(None)
    self.assertEqual({'type': 'ArgumentRef', 'value': 'foo'}, result)

    from_geo_json_feature = le.Feature({
        'type': 'Feature',
        'id': 'bar',
        'geometry': point.toGeoJSON(),
        'properties': {'foo': 42}
    })
    self.assertEqual(le.ApiFunction('Feature'), from_geo_json_feature.func)
    self.assertEqual(point, from_geo_json_feature.args['geometry'])
    self.assertEqual({
        'foo': 42,
        'system:index': 'bar'
    }, from_geo_json_feature.args['metadata'])

  def testGetMap(self):
    """Verifies that getMap() uses Collection.draw to rasterize Features."""
    feature = le.Feature(None)
    mapid = feature.getMapId({'color': 'ABCDEF'})
    manual = le.ApiFunction.apply_('Collection.draw', {
        'collection': le.FeatureCollection([feature]),
        'color': 'ABCDEF'})

    self.assertEqual('fakeMapId', mapid['mapid'])
    self.assertEqual(manual.serialize(), mapid['image'].serialize())

  def testInitOptParams(self):
    result = le.Feature(
        geom=le.Geometry.Point(1, 2), opt_properties=dict(prop='a')
    ).serialize()
    self.assertIn('"metadata": {"constantValue": {"prop": "a"}}', result)

  def test_area(self):
    expect = make_expression_graph({
        'arguments': {
            'feature': FEATURE_NONE_GRAPH,
            'maxError': MAX_ERROR_GRAPH,
            'proj': PROJ_GRAPH,
        },
        'functionName': 'Feature.area',
    })
    expression = le.Feature(None).area(10, EPSG_4326)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Feature(None).area(maxError=10, proj=EPSG_4326)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_aside(self):
    mock_function = mock.Mock(return_value=None)
    feature = le.Feature(None)
    self.assertIs(feature, feature.aside(mock_function))
    mock_function.assert_called_once_with(feature)

  def test_bounds(self):
    expect = make_expression_graph({
        'arguments': {
            'feature': FEATURE_NONE_GRAPH,
            'maxError': MAX_ERROR_GRAPH,
            'proj': PROJ_GRAPH,
        },
        'functionName': 'Feature.bounds',
    })
    expression = le.Feature(None).bounds(10, EPSG_4326)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Feature(None).bounds(maxError=10, proj=EPSG_4326)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_buffer(self):
    expect = make_expression_graph({
        'arguments': {
            'feature': FEATURE_NONE_GRAPH,
            'distance': {'constantValue': 42},
            'maxError': MAX_ERROR_GRAPH,
            'proj': PROJ_GRAPH,
        },
        'functionName': 'Feature.buffer',
    })
    expression = le.Feature(None).buffer(42, 10, EPSG_4326)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Feature(None).buffer(
        distance=42, maxError=10, proj=EPSG_4326
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_centroid(self):
    expect = make_expression_graph({
        'arguments': {
            'feature': FEATURE_NONE_GRAPH,
            'maxError': MAX_ERROR_GRAPH,
            'proj': PROJ_GRAPH,
        },
        'functionName': 'Feature.centroid',
    })
    expression = le.Feature(None).centroid(10, EPSG_4326)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Feature(None).centroid(maxError=10, proj=EPSG_4326)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_closest_point(self):
    right = le.Feature(None, {'a': 'b'})
    max_error = 10
    proj = EPSG_4326
    expect = make_expression_graph({
        'arguments': {
            'left': FEATURE_NONE_GRAPH,
            'right': FEATURE_A_GRAPH,
            'maxError': MAX_ERROR_GRAPH,
            'proj': PROJ_GRAPH,
        },
        'functionName': 'Feature.closestPoint',
    })
    expression = le.Feature(None).closestPoint(right, max_error, proj)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Feature(None).closestPoint(
        right=right, maxError=max_error, proj=proj
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_closest_points(self):
    right = le.Feature(None, {'a': 'b'})
    max_error = 10
    proj = EPSG_4326
    expect = make_expression_graph({
        'arguments': {
            'left': FEATURE_NONE_GRAPH,
            'right': FEATURE_A_GRAPH,
            'maxError': MAX_ERROR_GRAPH,
            'proj': PROJ_GRAPH,
        },
        'functionName': 'Feature.closestPoints',
    })
    expression = le.Feature(None).closestPoints(right, max_error, proj)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Feature(None).closestPoints(
        right=right, maxError=max_error, proj=proj
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_contained_in(self):
    expect = right_maxerror_proj('containedIn')

    expression = le.Feature(None).containedIn(le.Feature(None), 10, EPSG_4326)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Feature(None).containedIn(
        right=le.Feature(None), maxError=10, proj=EPSG_4326
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_contains(self):
    expect = right_maxerror_proj('contains')

    expression = le.Feature(None).contains(le.Feature(None), 10, EPSG_4326)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Feature(None).contains(
        right=le.Feature(None), maxError=10, proj=EPSG_4326
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_convex_hull(self):
    expect = make_expression_graph({
        'arguments': {
            'feature': FEATURE_NONE_GRAPH,
            'maxError': MAX_ERROR_GRAPH,
            'proj': PROJ_GRAPH,
        },
        'functionName': 'Feature.convexHull',
    })
    expression = le.Feature(None).convexHull(10, EPSG_4326)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Feature(None).convexHull(maxError=10, proj=EPSG_4326)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_copy_properties(self):
    source = le.Feature(None, {'a': 'b'})
    properties = ['c', 'd']
    exclude = ['e', 'f']
    expect = make_expression_graph({
        'arguments': {
            'destination': FEATURE_NONE_GRAPH,
            'source': FEATURE_A_GRAPH,
            'properties': {'constantValue': properties},
            'exclude': {'constantValue': exclude},
        },
        # Note this is Element rather than Feature
        'functionName': 'Element.copyProperties',
    })
    expression = le.Feature(None).copyProperties(source, properties, exclude)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Feature(None).copyProperties(
        source=source, properties=properties, exclude=exclude
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_cutLines(self):
    expect = make_expression_graph({
        'arguments': {
            'feature': FEATURE_NONE_GRAPH,
            'distances': {'constantValue': [1, 2]},
            'maxError': MAX_ERROR_GRAPH,
            'proj': PROJ_GRAPH,
        },
        'functionName': 'Feature.cutLines',
    })
    expression = le.Feature(None).cutLines([1, 2], 10, EPSG_4326)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Feature(None).cutLines(
        distances=[1, 2], maxError=10, proj=EPSG_4326
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_difference(self):
    expect = right_maxerror_proj('difference')

    expression = le.Feature(None).difference(le.Feature(None), 10, EPSG_4326)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Feature(None).difference(
        right=le.Feature(None), maxError=10, proj=EPSG_4326
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_disjoint(self):
    expect = right_maxerror_proj('disjoint')

    expression = le.Feature(None).disjoint(le.Feature(None), 10, EPSG_4326)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Feature(None).disjoint(
        right=le.Feature(None), maxError=10, proj=EPSG_4326
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_dissolve(self):
    expect = make_expression_graph({
        'arguments': {
            'feature': FEATURE_NONE_GRAPH,
            'maxError': MAX_ERROR_GRAPH,
            'proj': PROJ_GRAPH,
        },
        'functionName': 'Feature.dissolve',
    })
    expression = le.Feature(None).dissolve(10, EPSG_4326)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Feature(None).dissolve(maxError=10, proj=EPSG_4326)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_distance(self):
    max_error = 10
    spherical = True
    expect = right_maxerror_proj('distance')
    argugments = expect['values']['0']['functionInvocationValue']['arguments']
    argugments['spherical'] = {'constantValue': spherical}

    expression = le.Feature(None).distance(
        le.Feature(None), max_error, EPSG_4326, spherical
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Feature(None).distance(
        right=le.Feature(None),
        maxError=max_error,
        proj=EPSG_4326,
        spherical=spherical,
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_geometry(self):
    expect = make_expression_graph({
        'arguments': {
            'feature': FEATURE_NONE_GRAPH,
            'maxError': MAX_ERROR_GRAPH,
            'proj': PROJ_GRAPH,
            'geodesics': {'constantValue': True},
        },
        'functionName': 'Feature.geometry',
    })
    expression = le.Feature(None).geometry(10, EPSG_4326, True)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Feature(None).geometry(
        maxError=10, proj=EPSG_4326, geodesics=True
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_hers_descriptor(self):
    expect = make_expression_graph({
        'arguments': {
            'element': FEATURE_NONE_GRAPH,
            'selectors': {'constantValue': ['a', 'b']},
            'buckets': {'constantValue': 2},
            'peakWidthScale': {'constantValue': 3},
        },
        'functionName': 'Feature.hersDescriptor',
    })
    expression = le.Feature(None).hersDescriptor(['a', 'b'], 2, 3)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Feature(None).hersDescriptor(
        selectors=['a', 'b'], buckets=2, peakWidthScale=3
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_id(self):
    expect = make_expression_graph({
        'arguments': {
            'element': FEATURE_NONE_GRAPH,
        },
        'functionName': 'Feature.id',
    })
    expression = le.Feature(None).id()
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_intersection(self):
    expect = right_maxerror_proj('intersection')

    expression = le.Feature(None).intersection(le.Feature(None), 10, EPSG_4326)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Feature(None).intersection(
        right=le.Feature(None), maxError=10, proj=EPSG_4326
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_intersects(self):
    expect = right_maxerror_proj('intersects')

    expression = le.Feature(None).intersects(le.Feature(None), 10, EPSG_4326)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Feature(None).intersects(
        right=le.Feature(None), maxError=10, proj=EPSG_4326
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_length(self):
    expect = make_expression_graph({
        'arguments': {
            'feature': FEATURE_NONE_GRAPH,
            'maxError': MAX_ERROR_GRAPH,
            'proj': PROJ_GRAPH,
        },
        'functionName': 'Feature.length',
    })
    expression = le.Feature(None).length(10, EPSG_4326)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Feature(None).length(maxError=10, proj=EPSG_4326)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_perimeter(self):
    expect = make_expression_graph({
        'arguments': {
            'feature': FEATURE_NONE_GRAPH,
            'maxError': MAX_ERROR_GRAPH,
            'proj': PROJ_GRAPH,
        },
        'functionName': 'Feature.perimeter',
    })
    expression = le.Feature(None).perimeter(10, EPSG_4326)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Feature(None).perimeter(maxError=10, proj=EPSG_4326)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_select(self):
    expect = make_expression_graph({
        'arguments': {
            'input': FEATURE_NONE_GRAPH,
            'propertySelectors': {'constantValue': ['a', 'b']},
            'newProperties': {'constantValue': ['c', 'd']},
            'retainGeometry': {'constantValue': True},
        },
        'functionName': 'Feature.select',
    })
    expression = le.Feature(None).select(['a', 'b'], ['c', 'd'], True)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Feature(None).select(
        propertySelectors=['a', 'b'],
        newProperties=['c', 'd'],
        retainGeometry=True,
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_setGeometry(self):
    expect = make_expression_graph({
        'arguments': {
            'feature': FEATURE_NONE_GRAPH,
            'geometry': {
                'functionInvocationValue': {
                    'functionName': 'GeometryConstructors.Point',
                    'arguments': {'coordinates': {'constantValue': [1, 2]}},
                }
            },
        },
        'functionName': 'Feature.setGeometry',
    })
    geojson_geom = {'type': 'Point', 'coordinates': [1, 2]}
    expression = le.Feature(None).setGeometry(geojson_geom)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Feature(None).setGeometry(geometry=geojson_geom)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_simplify(self):
    expect = make_expression_graph({
        'arguments': {
            'feature': FEATURE_NONE_GRAPH,
            'maxError': MAX_ERROR_GRAPH,
            'proj': PROJ_GRAPH,
        },
        'functionName': 'Feature.simplify',
    })
    expression = le.Feature(None).simplify(10, EPSG_4326)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Feature(None).simplify(maxError=10, proj=EPSG_4326)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_symmetric_difference(self):
    expect = right_maxerror_proj('symmetricDifference')

    expression = le.Feature(None).symmetricDifference(
        le.Feature(None), 10, EPSG_4326
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Feature(None).symmetricDifference(
        right=le.Feature(None), maxError=10, proj=EPSG_4326
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_to_array(self):
    expect = make_expression_graph({
        'arguments': {
            'feature': FEATURE_NONE_GRAPH,
            'properties': {'constantValue': ['a', 'b']},
        },
        'functionName': 'Feature.toArray',
    })
    expression = le.Feature(None).toArray(['a', 'b'])
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Feature(None).toArray(properties=['a', 'b'])
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_transform(self):
    expect = make_expression_graph({
        'arguments': {
            'feature': FEATURE_NONE_GRAPH,
            'maxError': MAX_ERROR_GRAPH,
            'proj': PROJ_GRAPH,
        },
        'functionName': 'Feature.transform',
    })
    expression = le.Feature(None).transform(EPSG_4326, maxError=10)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Feature(None).transform(proj=EPSG_4326, maxError=10)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_union(self):
    expect = right_maxerror_proj('union')

    expression = le.Feature(None).union(le.Feature(None), 10, EPSG_4326)
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Feature(None).union(
        right=le.Feature(None), maxError=10, proj=EPSG_4326
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

  def test_withinDistance(self):
    expect = {
        'result': '0',
        'values': {
            '1': {
                'functionInvocationValue': {
                    'functionName': 'Feature',
                    'arguments': {},
                }
            },
            '0': {
                'functionInvocationValue': {
                    'arguments': {
                        'left': {'valueReference': '1'},
                        'right': {'valueReference': '1'},
                        'distance': {'constantValue': 42},
                        'maxError': MAX_ERROR_GRAPH,
                        'proj': PROJ_GRAPH,
                    },
                    'functionName': 'Feature.withinDistance',
                }
            },
        },
    }

    expression = le.Feature(None).withinDistance(
        le.Feature(None), 42, 10, EPSG_4326
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)

    expression = le.Feature(None).withinDistance(
        right=le.Feature(None), distance=42, maxError=10, proj=EPSG_4326
    )
    result = json.loads(expression.serialize())
    self.assertEqual(expect, result)


if __name__ == '__main__':
  unittest.main()

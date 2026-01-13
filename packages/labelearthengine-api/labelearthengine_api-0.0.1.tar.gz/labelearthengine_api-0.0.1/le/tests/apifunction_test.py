#!/usr/bin/env python3
"""Test for the ee.apifunction module."""

import types

import unittest
import le
from le import apitestcase


class ApiFunctionTest(apitestcase.ApiTestCase):

  def testAddFunctions(self):
    """Verifies that addition of static and instance API functions."""

    # Check instance vs static functions, and trampling of
    # existing functions.
    class TestClass:

      def pre_addBands(self):  # pylint: disable=g-bad-name
        pass

    self.assertFalse(hasattr(TestClass, 'pre_load'))
    self.assertFalse(hasattr(TestClass, 'select'))
    self.assertFalse(hasattr(TestClass, 'pre_select'))
    self.assertTrue(hasattr(TestClass, 'pre_addBands'))
    self.assertFalse(hasattr(TestClass, '_pre_addBands'))

    le.ApiFunction.importApi(TestClass, 'Image', 'Image', 'pre_')
    # pytype: disable=attribute-error
    self.assertNotIsInstance(TestClass.pre_load, types.MethodType)
    # pytype: enable=attribute-error
    self.assertFalse(hasattr(TestClass, 'select'))
    # Unbound methods are just functions in Python 3. Check both to maintain
    # backward compatibility.
    # pytype: disable=attribute-error
    self.assertIsInstance(TestClass.pre_select,
                          (types.FunctionType, types.MethodType))
    # pytype: enable=attribute-error
    self.assertIsInstance(TestClass.pre_addBands,
                          (types.FunctionType, types.MethodType))
    self.assertFalse(hasattr(TestClass, '_pre_addBands'))

    le.ApiFunction.clearApi(TestClass)
    self.assertFalse(hasattr(TestClass, 'pre_load'))
    self.assertFalse(hasattr(TestClass, 'select'))
    self.assertFalse(hasattr(TestClass, 'pre_select'))
    self.assertTrue(hasattr(TestClass, 'pre_addBands'))
    self.assertFalse(hasattr(TestClass, '_pre_addBands'))

  def testAddFunctions_Inherited(self):
    """Verifies that inherited non-client functions can be overridden."""

    class Base:

      def ClientOverride(self):
        pass

    class Child(Base):
      pass

    le.ApiFunction.importApi(Base, 'Image', 'Image')
    le.ApiFunction.importApi(Child, 'Image', 'Image')
    self.assertEqual(Base.ClientOverride, Child.ClientOverride)
    # pytype: disable=attribute-error
    self.assertNotEqual(Base.addBands, Child.addBands)
    # pytype: enable=attribute-error

  def testEq(self):
    a_signature = {'hello': 'world', 'args': []}
    b_signature = {
        'hello': 'world',
        'args': [{'name': 'foo', 'type': 'number'}],
    }

    # Identical.
    self.assertEqual(
        le.ApiFunction(name='test', signature=a_signature),
        le.ApiFunction(name='test', signature=a_signature),
    )
    # Different name.
    self.assertNotEqual(
        le.ApiFunction(name='test-1', signature=a_signature),
        le.ApiFunction(name='test-2', signature=a_signature),
    )
    # Different signature.
    self.assertNotEqual(
        le.ApiFunction(name='test', signature=a_signature),
        le.ApiFunction(name='test', signature=b_signature),
    )
    # Different type.
    self.assertNotEqual(
        le.ApiFunction(name='test', signature=a_signature), a_signature
    )

  def testInitOptParams(self):
    signature = {'hello': 'world', 'args': []}
    self.assertEqual(
        le.ApiFunction(name='test', signature=signature),
        le.ApiFunction(name='test', opt_signature=signature),
    )

  def testImportApiOptParams(self):
    args = dict(
        target=le.Dictionary, prefix='Dictionary', type_name='Dictionary'
    )
    le.ApiFunction.importApi(**args, prepend='test1_')
    self.assertTrue(hasattr(le.Dictionary, 'test1_getNumber'))
    le.ApiFunction.importApi(**args, opt_prepend='test2_')
    self.assertTrue(hasattr(le.Dictionary, 'test2_getNumber'))


if __name__ == '__main__':
  unittest.main()

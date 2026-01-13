#!/usr/bin/env python3
"""Test for ee._helpers.

When the function in question is defined in ee/_helpers.py but exported for
public use by ee/__init__.py, the test is located here but uses the ee.-prefixed
name since that is the name we want to ensure works.
"""

import io
import unittest

import unittest
import le
from le import apifunction
from le import apitestcase
from le import computedobject
from le import ee_exception


class ProfilingTest(apitestcase.ApiTestCase):

  def MockValue(self, value):
    """Overridden to check for profiling-related data."""
    hooked = le.data._thread_locals.profile_hook is not None
    is_get_profiles = isinstance(
        value, computedobject.ComputedObject
    ) and value.func == apifunction.ApiFunction.lookup('Profile.getProfiles')
    return 'hooked=%s getProfiles=%s' % (hooked, is_get_profiles)

  def testProfilePrinting(self):
    le.data.computeValue = self.MockValue
    out = io.StringIO()
    with le.profilePrinting(destination=out):
      self.assertEqual('hooked=True getProfiles=False', le.Number(1).getInfo())
    self.assertEqual('hooked=False getProfiles=True', out.getvalue())

  def testProfilePrintingDefaultSmoke(self):
    # This will print to sys.stderr, so we can't make any assertions about the
    # output. But we can check that it doesn't fail.
    le.data.computeValue = self.MockValue
    with le.profilePrinting():
      self.assertEqual('hooked=True getProfiles=False', le.Number(1).getInfo())

  def testProfilePrintingErrorGettingProfiles(self):
    le.data.computeValue = self.MockValue
    mock = unittest.mock.Mock()
    mock.call.side_effect = ee_exception.EEException('test')
    apifunction.ApiFunction._api['Profile.getProfiles'] = mock

    with self.assertRaises(ee_exception.EEException):
      with le.profilePrinting():
        le.Number(1).getInfo()
    self.assertEqual(5, mock.call.call_count)


if __name__ == '__main__':
  unittest.main()

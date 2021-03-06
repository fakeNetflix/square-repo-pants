# coding=utf-8
# Copyright 2014 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import (nested_scopes, generators, division, absolute_import, with_statement,
                        print_function, unicode_literals)

import os
import subprocess

from pants.base.build_environment import get_buildroot
from pants_test.pants_run_integration_test import PantsRunIntegrationTest


class WireIntegrationTest(PantsRunIntegrationTest):

  def test_good(self):
    # wire example should compile without warnings with correct wire files.
    cmd = ['goal',
           'compile',
           'examples/src/java/com/pants/examples/wire/temperature']
    pants_run = self.run_pants(cmd)
    self.assert_success(pants_run)

    expected_outputs = [
      'Compiling proto source file',
      'Created output directory',
      'Writing generated code',
      '/gen/wire/gen-java/com/pants/examples/temperature/Temperature.java',
    ]
    for expected_output in expected_outputs:
      self.assertTrue(expected_output in pants_run.stdout_data)

  def test_bundle_wire_normal(self):
    pants_run = self.run_pants(
      ['goal', 'bundle', 'examples/src/java/com/pants/examples/wire/temperature',
       '--bundle-deployjar', '--print-exception-stacktrace',])
    self.assertEquals(pants_run.returncode, self.PANTS_SUCCESS_CODE,
                      "goal bundle run expected success, got {0}\n"
                      "got stderr:\n{1}\n"
                      "got stdout:\n{2}\n".format(pants_run.returncode,
                                                  pants_run.stderr_data,
                                                  pants_run.stdout_data))
    out_path = os.path.join(get_buildroot(), 'dist', 'wire-temperature-example-bundle')

    java_run = subprocess.Popen(['java', '-cp', 'wire-temperature-example.jar',
                                 'com.pants.examples.wire.temperature.WireTemperatureExample'],
                                stdout=subprocess.PIPE,
                                cwd=out_path)
    java_retcode = java_run.wait()
    java_out = java_run.stdout.read()
    self.assertEquals(java_retcode, 0)
    self.assertTrue('19 degrees celsius' in java_out)

  def test_bundle_wire_dependent_targets(self):
    pants_run = self.run_pants(
      ['goal', 'bundle', 'examples/src/java/com/pants/examples/wire/element',
       '--bundle-deployjar', '--print-exception-stacktrace',])
    self.assertEquals(pants_run.returncode, self.PANTS_SUCCESS_CODE,
                      "goal bundle run expected success, got {0}\n"
                      "got stderr:\n{1}\n"
                      "got stdout:\n{2}\n".format(pants_run.returncode,
                                                  pants_run.stderr_data,
                                                  pants_run.stdout_data))
    out_path = os.path.join(get_buildroot(), 'dist', 'wire-element-example-bundle')

    java_run = subprocess.Popen(['java', '-cp', 'wire-element-example.jar',
                                 'com.pants.examples.wire.element.WireElementExample'],
                                stdout=subprocess.PIPE,
                                cwd=out_path)
    java_retcode = java_run.wait()
    java_out = java_run.stdout.read()
    self.assertEquals(java_retcode, 0)
    self.assertTrue('Element{symbol=Hg, name=Mercury, atomic_number=80, '
                    'melting_point=Temperature{unit=celsius, number=-39}, '
                    'boiling_point=Temperature{unit=celsius, number=357}}' in java_out)

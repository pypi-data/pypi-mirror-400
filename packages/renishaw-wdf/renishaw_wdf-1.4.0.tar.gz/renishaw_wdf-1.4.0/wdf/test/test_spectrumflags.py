# Copyright (c) 2022 Renishaw plc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import unittest
from ..wdfenums import WdfSpectrumFlags


class TestSpectrumFlags(unittest.TestCase):

    def test_saturated_flag(self):
        """Check the saturated flag is reconstructed from integer input"""
        f = WdfSpectrumFlags(1)
        self.assertEqual(f, WdfSpectrumFlags.Saturated)

    def test_error_flag(self):
        """Check the error flag is reconstructed from integer input"""
        f = WdfSpectrumFlags(2)
        self.assertEqual(f, WdfSpectrumFlags.Error)

    def test_saturated_and_error_flag(self):
        """Check that two flags are reconstructed from integer input"""
        f = WdfSpectrumFlags(3)
        self.assertEqual(f, WdfSpectrumFlags.Error | WdfSpectrumFlags.Saturated)

    def test_masked_flag(self):
        """Check the masked flag is reconstructed from integer input"""
        f = WdfSpectrumFlags(1 << 48)
        self.assertEqual(f, WdfSpectrumFlags.Masked)

    def test_masked_and_saturated(self):
        """Check masked and saturated flags are reconstructed from integer input"""
        f = WdfSpectrumFlags(0x0001_0000_0000_0001)
        self.assertEqual(f, WdfSpectrumFlags.Saturated | WdfSpectrumFlags.Masked)

    def test_invalid_flag(self):
        """Check an invalid flag has no name but is accepted"""
        f = WdfSpectrumFlags(1 << 15)
        self.assertEqual(f.value, 32768)
        self.assertIsNone(f.name)

    def test_custom_mask_flag(self):
        """Check an user-defined mask flag is accepted"""
        f = WdfSpectrumFlags(1 << 49)
        self.assertEqual(f.name, None)
        self.assertEqual(f.value, 0x2_0000_0000_0000)


if __name__ == '__main__':
    unittest.main()

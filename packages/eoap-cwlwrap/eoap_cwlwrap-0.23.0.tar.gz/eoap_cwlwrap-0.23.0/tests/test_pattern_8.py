# Copyright 2025 Terradue
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from tests.helpers import TestCWL

class TestPattern8(TestCWL):

    def setUp(self):
        super().setUp()
        self.entrypoint = "pattern-8"

    def tearDown(self):
        super().tearDown()

    def test_pattern_wrapped_cwl(self):
        self._wrapped_cwl_validation()

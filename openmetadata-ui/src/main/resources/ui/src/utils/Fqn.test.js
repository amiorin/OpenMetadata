/*
 *  Copyright 2021 Collate
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *  http://www.apache.org/licenses/LICENSE-2.0
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 */

import Fqn from './Fqn';

describe('Test FQN', () => {
  it('should split and build', () => {
    let fqn = "foo.bar"
    let xs = Fqn.split(fqn);
    expect(xs).toStrictEqual(["foo", "bar"]);
    expect(Fqn.build(...xs)).toStrictEqual(fqn);
  });

  it('should quote and unquote', () => {
    let xs = ['foo"bar', 'foo.bar']
    expect(Fqn.split(Fqn.build(...xs))).toStrictEqual(xs);
  });
});
# Copyright 2011 The SCGrab Developers
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
#
"""
Author: Guido van Rossum

Taken from: http://www.python.org/doc/essays/ppt/sd99east/sld054.htm

Modified by: Lonnie Mendez

"""
import os, errno, time


class LockException(Exception):
    pass

class LockAcquired(LockException):
    pass

class LockCreateFailed(LockException):
    pass


class Lock:

    def __init__(self, dirname):
        self.dirname = dirname
        self.locked = 0

    def lock(self):
        assert not self.locked
        while True:
            try:
                os.mkdir(self.dirname)
                self.locked = 1
                return        # or break
            except OSError, e:
                if e.errno == errno.ENOENT:
                    raise LockCreateFailed(
                    "failed to create lock folder '%s'" % self.dirname)
                if e.errno != errno.EEXIST:
                    raise
                raise LockAcquired(
                    "'%s' already acquired" % self.dirname)

    def unlock(self):
        assert self.locked
        self.locked = 0
        os.rmdir(self.dirname)

    # auto-unlock when lock object is deleted
    def __del__(self):
        if self.locked:
            self.unlock()

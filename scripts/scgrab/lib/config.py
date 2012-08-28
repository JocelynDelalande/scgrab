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

""" globals - some of these values are built in main """
__version__ = "0.1.3"
script_dir = ''
cache_dir = "cache"
cache_flush_locks = False
cache_flush = False
auth_dir = "auth"
key_dir = "keys"
auth_cred = ''
auth_key = ''
auth_key_type = 'rsa'
auth_auto_keylookup = False
active_plugins = []
output_marker = [ "@=@=@=@", "=======" ]
debug = False
threshold = 240
ssh_hostname = ''
ssh_timeout = 10
ssh_port = 22
use_plugin = ''
use_query = ''
log_handle = None


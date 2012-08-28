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
from glob import glob
import config as config
import sys, os


""" begin main helper functions """

def logger(msg):
    from time import gmtime, strftime
    from os import getpid
    
    if not config.log_handle:
        config.log_handle = open(config.script_dir + os.sep + "log" + os.sep +
            "dbglog-%s.txt" % os.getpid(), 'a')
    
    config.log_handle.write("%s - %s: %s" % (strftime("%Y-%m-%d %H:%M:%S",
                                    gmtime()), getpid(), msg))
    
    return
    
def errMsg(msg, showCon=False):
    if config.debug or showCon:
        print msg

    logger(msg + '\n')
    
    return

def flush_cache():
    import os
    cache_files = "%s%s%s%s*.dat" % \
        (config.script_dir, os.sep, config.cache_dir, os.sep)

    for file in glob(cache_files):
        os.remove(file)

    return

def flush_locks():
    import os
    lock_dirs = "%s%s%s%s*.lock" % \
        (config.script_dir, os.sep, config.cache_dir, os.sep)

    for dir in glob(lock_dirs):
        os.rmdir(dir)

    return

""" end main helper functions """

""" begin plugin helper functions """

def mcastatus_get_param(data, query):
    found = False

    for line in data['params']:
        name, value = line.split('=')
        if query == name:
            found = True
            break

    if found:
        return True, value

    return False, False

# search the station list and find the item for the given index (wlan mac)
# one level deep: item='signal', two levels deep: item='stats.rx_bytes'
def wstalist_get_param(data, item, index):
    staEntry = None
    found = False
    idx = 0
    
    for id in data:
        if index == str(id.keys()[0]):
            staEntry = data[idx][index]
            break
        idx = idx + 1
    
    # an invalid query will trigger exception
    if staEntry:
        try:
            if item.count('.') == 1:
                keys = item.split('.')
                value = str(staEntry[keys[0]][keys[1]])
            else:
                value = str(staEntry[item])

            found = True
        except:
            pass
        
    if found:
        return True, value
        
    return False, False

""" end plugin helper functions """

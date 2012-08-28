#!/usr/bin/env python
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
scgrab.py:
This program will cache and recall data obtained via an ssh session for a
specified period of time using pre-defined methods for storing, processing,
and accessing said data.  It is meant to be used when buffering queries from
a poller to a device.

Author: Lonnie Mendez <dignome AT gmail.com>

last revision: 2011-02-21
release 0.1.3 (2011-02-21):
    -replaced filelock with basic lock class
    -many syntax changes (tabs -> spaces, wrap lines)
    -implemented cacti script indexing for ubnt-wstalist plugin
    -changed to binary pickle format using cPickle module
        -cache lookup latency improved by 1% typical
    -implemented basic error logging
    -enabled plugin ubnt-cputop by default
    -added plugin ubnt-ram (default disabled)
    -added multi-output support for several queries
    -added several new queries

release 0.1.2 (2011-02-02):
    -relicensed source under the apache license, version 2.0
    -improved handling of host connection details (removed ipv4 dependency)
    -made cache filenames valid/safe for underlying filesystem (base64 encoded)
    -added plugin system along with new plugins; ubnt_mcastatus, ubnt_cpustats,
     and ubnt_wstalist (stub)
        -improved cache response time 58% by rearranging imports
    -added fix for parallel writers scenario (filelock)
    -added a means to flush cache locks (--flushlocks)
    -added a means to flush cache files (--flushcache)
    -added more exception handling
    -added timeout field to ssh connect
    -added ability to specify ssh port

This is the libssh2 version of this script.

Guide on how to use libssh2 python wrapper:
http://www.no-ack.org/2010/11/python-bindings-for-libssh2.html

This is experimental code - while it seems to work for me I don't
guarantee anything.  It is not as portable as paramiko, but it could
be with some more work.

No time to further develop this version of the script - maybe someone
will take this up.
"""
from base64 import urlsafe_b64encode
from datetime import datetime, timedelta
from getopt import gnu_getopt, GetoptError
import cPickle as pickle
import sys, os
import lib.config as config
import lib.plugins as plug
from lib.utils import errMsg


""" begin helper functions """

""" connect to device and retrieve data for cache """
# returns True if cache file was successfully updated,
# otherwise False
def generate_cache(cacheFile, authCredFile, authKeyFile):
    import socket
    import libssh2

    username = None
    password = None
    hostKey = None

    if len(authCredFile):
        try:
            fd = open(authCredFile, 'r')
        except:
            errMsg("generate_cache: failed to open auth credentials file")
            return False
        
        for line in fd.readlines():
            name, value = line.strip().split(':')
            if name == "username":
                username = value
            elif name == "password":
                password = value
        
        fd.close()
        
    if len(authKeyFile) and not os.path.exists(authKeyFile):
        errMsg("generate_cache: key file specified does not exist")
        return False
    elif len(authKeyFile):
        try:
            if config.auth_key_type == 'dsa':
                #hostKey = paramiko.DSSKey(filename=authKeyFile, password=password)
                pass
            else:
                #hostKey = paramiko.RSAKey(filename=authKeyFile, password=password)
                pass
        except Exception, e:
            msg = str(e)
            if msg.count("encrypt"):
                errMsg("generate_cache: key specified is encrypted " +
                    "(use --authcred): %s" % msg)
            elif msg.count("RSA private"):
                errMsg("generate_cache: key specified is type DSA " +
                "(use --authkeydsa): %s" % msg)
            else:
                errMsg(msg)

            return False
        
    # if no auth credentials are specified default to root for username
    if len(username) == 0:
        username = "root"
    
    # connect to remote host
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((config.ssh_hostname, config.ssh_port))

    session = libssh2.Session()
    session.startup(sock)
    session.set_password(username, password)

    channel = session.channel()

    # build the command to execute remotely
    cmd_list = []
    output_marker_end = "%s-end-%s" % \
        (config.output_marker[1], config.output_marker[0])
    for plugin in config.active_plugins:
        if not len(cmd_list) == 0:
            cmd_list.append(" && ")

        cmd_list.append("echo '%s%s%s' && %s && echo '%s'" %
            (config.output_marker[0], plugin.shortname,
             config.output_marker[1], plugin.command, output_marker_end))

    command = ''.join(cmd_list)

    # abstract this code into a general read function / add proper checking
    channel.execute(command)

    stdout = []
    stderr = []

    while not channel.eof():
        data = channel.read(1024, 0)
        if data:
            stdout.append(data)

        data = channel.read(1024, 1)
        if data:
            stderr.append(data)

    # check if the returned data has the right amount of elements
    rawData = ''.join(stdout)

    if not rawData.count(config.output_marker[0]) == len(config.active_plugins) * 2:
        errMsg("generate_cache: partial result - perhaps connection is having problems")
        return False

    # pass the data to the appropriate plugin for processing
    current_plugin = None
    packData = {}
    dataList = []

    for line in rawData.splitlines(True):
        if line[:len(config.output_marker[0])] == config.output_marker[0]:
            for plugin in config.active_plugins:
                # check signature and assign plugin for processing data
                pluginSignature = config.output_marker[0] + plugin.shortname + \
                                    config.output_marker[1]
                if line.rstrip('\n') == pluginSignature:
                    current_plugin = plugin
                    if config.debug:
                        print "generate_cache: found data for plugin" + \
                                current_plugin.name
        # processing the data-set has completed for the plugin - reset for next plugin
        elif line.rstrip('\n') == output_marker_end:
            packData[current_plugin.shortname] = current_plugin.dataPack(''.join(dataList))
            current_plugin = None
            del dataList[:]
        # construct the data-set for the current plugin
        elif not current_plugin == None:
            dataList.append(line)

    # finally write the cache file
    try:
        fd = open(cacheFile, 'wb')
    except:
        errMsg("generate_cache: failed to open cache file for writing")
        return False
    
    pickle.dump(packData, fd, pickle.HIGHEST_PROTOCOL);
    fd.close();
    
    return True
    
def usage():
    print "\n%s\n\tversion:" % sys.argv[0], config.__version__,
    print "- Copyright 2011 The SCGrab Developers \n"
    print "Valid arguments are:\n"
    print "-h, --help                 Prints this help menu"
    print "-v                         Enables verbose debugging"
    print "--version                  Print script version and exit"
    print "--host=xxx.xxx.xxx.xxx     Specify target host by ip address or host name"
    print "--port=xxxx                Specify the port of the target ssh server"
    print "--timeout=xxx              Specify the timeout for connecting to the ssh server"
    print "--plugin=xxx               Specify plugin to use for query"
    print "--query=xxx                Specify query to use for plugin"
    print "--scriptdir=xxx            Specify directory where this script resides"
    print "                           This value is an absolute path"
    print "--cachedir=xxx             Specify directory to store cached data (%s)" % \
                                                        str(config.cache_dir)
    print "                           This value is relative to scriptdir"
    print "--flushcache               This will remove all cache files"
    print "--flushlocks               This will remove all cache file locks"
    print "--authdir=xxx              Specify directory to store auth data (%s)" % \
                                                        str(config.auth_dir)
    print "                           This value is relative to scriptdir"
    print "--authcred=xxx             Specify the auth file containing user/pass"
    print "\tFile Format:"
    print "\t\tusername:myuser"
    print "\t\tpassword:mypass"
    print "--authkey=xxx              Specify the name of the private key for ssh"
    print "                           session.  If key uses password protection then"
    print "                           you must also specify --authcred"
    print "--authkeydsa               Specified key is DSA - default RSA"
    print "--autokeylookup            Enables searching for private keys"
    print "--threshold=xxx            Specify seconds until data is recached (%s)" % \
                                                        str(config.threshold)
    print "\nExample usage:\n"
    print "\t%s \\\n\t --host=10.9.3.25 --authcred=userpass.txt" % sys.argv[0] + \
            " \\\n\t --plugin=ubnt-mcastatus --query=signal"

def handle_args():
    try:
        opts, args = gnu_getopt(sys.argv[1:], ":hv", ["help", "version", "host=",
            "port=", "timeout=", "plugin=", "query=", "scriptdir=", "cachedir=",
            "flushcache", "flushlocks", "authdir=", "authcred=", "authkey=",
            "authkeydsa", "autokeylookup", "threshold="])
    except GetoptError, err:
        # print help information and exit:
        print "handle_args:", str(err)
        usage()
        sys.exit(1)

    for o, a in opts:
        if o == "-v":
            config.debug = True
        elif o in ("-h", "--help"):
            usage()
            sys.exit(1)
        elif o in ("--version"):
            print "%s - %s" % (sys.argv[0], config.__version__)
            sys.exit(1)
        elif o in ("--host"):
            if len(a) == 0:
                usage()
                sys.exit(1)			

            config.ssh_hostname = a
        elif o in ("--port"):
            if len(a) == 0:
                usage()
                sys.exit(1)

            config.ssh_port = int(a)
        elif o in ("--timeout"):
            if len(a) == 0:
                usage()
                sys.exit(1)

            config.ssh_timeout = int(a)
        elif o in ("--plugin"):
            if len(a) == 0:
                usage()
                sys.exit(1)

            config.use_plugin = a
        elif o in ("--query"):
            if len(a) == 0:
                usage()
                sys.exit(1)
                
            config.use_query = a
        elif o in ("--scriptdir"):
            if len(a) == 0:
                usage()
                sys.exit(1)
            
            config.script_dir = a
        elif o in ("--cachedir"):
            if len(a) == 0:
                usage()
                sys.exit(1)
            
            config.cache_dir = a
        elif o in ("--flushcache"):
            config.cache_flush = True
        elif o in ("--flushlocks"):
            config.cache_flush_locks = True
        elif o in ("--authdir"):
            if len(a) == 0:
                usage()
                sys.exit(1)
            
            config.auth_dir = a
        elif o in ("--authcred"):
            if len(a) == 0:
                usage()
                sys.exit(1)
            
            config.auth_cred = a
        elif o in ("--authkey"):
            if len(a) == 0:
                usage()
                sys.exit(1)
            
            config.auth_key = a
        elif o in ("--authkeydsa"):
            config.auth_key_type = 'dsa'
        elif o in ("--autokeylookup"):
            config.auth_auto_keylookup = True
        elif o in ("--threshold"):
            if len(a) == 0:
                usage()
                sys.exit(1)
            
            config.threshold = a
        else:
            assert False, "unhandled option"
            
""" end helper functions """

if __name__ == '__main__':
    # handle input paramaters
    handle_args()

    # set up script path
    if not len(config.script_dir):
            config.script_dir = os.path.dirname(os.path.realpath(__file__))
    elif not os.path.exists(config.script_dir):
        errMsg("main: given script directory does not exist")
        sys.exit(1)

    # flag any flush requests
    perform_flush = False

    if config.cache_flush_locks or config.cache_flush:
        perform_flush = True

    # load enabled plugins
    for plugin in plug.plugins_available:
        if plugin.enabled:
            loadObject = plugin()
            config.active_plugins.append(loadObject)

    # need at least one plugin to do something useful
    if len(config.active_plugins) == 0:
        errMsg("main: There must be at least one plugin enabled.")
        sys.exit(1)

    # verify plugin is enabled
    validPlugin = False
    for plugin in config.active_plugins:
        if config.use_plugin == plugin.shortname:
            validPlugin = True
            break

    # check vital arguments
    if perform_flush:
        pass
    elif (len(sys.argv) == 1 or not validPlugin or len(config.use_query) == 0 or
        len(config.ssh_hostname) == 0):
        usage()
        if not validPlugin:
            errMsg("\nmain: invalid plugin %s - plugins available:" % config.use_plugin, True)
            for plugin in config.active_plugins:
                errMsg("\t%s - %s" % (plugin.shortname, plugin.name), True)
        sys.exit(1)

    # build up variables
    if len(config.auth_cred):
        authCredFile = "%s%s%s%s%s" % \
            (config.script_dir, os.sep, config.auth_dir, os.sep, config.auth_cred)
    else:
        authCredFile = ''
        
    if len(config.auth_key):
        authKeyFile = "%s%s%s%s%s%s%s" % \
            (config.script_dir, os.sep, config.auth_dir, os.sep,
                config.key_dir, os.sep, config.auth_key)
    else:
        authKeyFile = ''

    cacheFile = "%s%s%s%s%s.dat" % \
        (config.script_dir, os.sep, config.cache_dir, os.sep,
            urlsafe_b64encode(config.ssh_hostname))

    if perform_flush:
        from lib.utils import flush_cache, flush_locks

        if config.cache_flush:
            errMsg("main: flushing cache files")
            flush_cache()
        
        if config.cache_flush_locks:
            errMsg("main: flushing cache locks")
            flush_locks()

        sys.exit(1)

    # if there is no suitable auth method then exit
    if len(authCredFile) == 0 and len(authKeyFile) == 0:
        errMsg("main: no suitable authorization method has been given")
        sys.exit(1)
    
    # compute threshold delta based on file modification date
    threshold_time = datetime.today() - timedelta(seconds=int(config.threshold))
    
    if os.path.exists(cacheFile):
        modify_time = datetime.fromtimestamp(os.path.getmtime(cacheFile))
    else:
        modify_time = 0
    
    # determine whether to use cached data or retrieve fresh data
    result = False

    if not os.path.exists(cacheFile) or (modify_time < threshold_time):
        from time import time, sleep
        from lib.lock import Lock, LockAcquired
        import stat

        lockFileName = "%s.lock" % cacheFile
        lock = Lock(lockFileName)

        # the first writer will acquire the lock - other processes will trigger exception
        try:
            lock.lock()
            result = generate_cache(cacheFile, authCredFile, authKeyFile)
            try:
                lock.unlock()
            except Exception, e:
                errMsg("could not remove lock: %s" % str(e))
        except LockAcquired: # occurs when lock is held
            start_time = time()
            while os.path.isdir(lockFileName):  # not the lock owner - wait for lock to be released
                if (time() - start_time) > 15: # waited too long - exit
                    errMsg("main: time exceeded waiting for lock removal (use --flushlocks?)")
                    break
                sleep(0.1)
            
            # lock has been released (data now available)
            if not os.path.isdir(lockFileName):
                result = True
        except Exception, e:
            errMsg("main: lock error: %s" % str(e))
    else:
        # valid data already exists in cache within the threshold time
        result = True

    # if problem encountered then exit
    if not result:
        errMsg("main: data not available - exiting")
        sys.exit(1)

    # success - open the cache file and return data based on user query
    try:
        fd = open(cacheFile, 'rb')
    except:
        errMsg("main: failed to open cache file for reading")
        sys.exit(1)

    dataSet = pickle.load(fd);
    fd.close();

    if config.debug:
        print "Target Host: %s" % str(config.ssh_hostname)
        print "Target Port: %s" % str(config.ssh_port)
        print "Connection timeout: %s seconds" % str(config.ssh_timeout)
        print "Query: %s" % str(config.use_query)
        print "Threshold: %s seconds" % str(config.threshold)
        print "cache file: %s" % str(cacheFile)
        print "auth credentials: %s" % str(authCredFile)
        print "auth key: %s" % str(authKeyFile)
        print "loaded plugins: "
        for plugin in config.active_plugins:
            print "\t%s - %s" % (plugin.shortname, plugin.name)
        print ''
    
    # find the specific query the user has requested for the given plugin
    found = False

    for plugin in config.active_plugins:
        if plugin.shortname == config.use_plugin:
            found, value = plugin.queryHandler(config.use_query, dataSet[plugin.shortname])
            break

    if found:
        if value:
            if config.debug: print "query return value: ",
            sys.stdout.write(value)
            if config.debug: print ''
        sys.exit(0)
    else:
        errMsg("main: value not found for given query")
    
    sys.exit(1)

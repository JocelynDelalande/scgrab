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
import config as config
import utils as utils
import sys, os

""" begin plugin definitions """
# dataPack method formats data received when executing its command and
#  returns data as a tuple for storing in the pickle file
# queryHandler method returns true along with a value if query is a match,
#  otherwise it should return False, None

# A few plugins for working with UBNT devices:

# plugin ubnt-mcastatus - handles information from mca-status
class plugin_UBNT_MCAStatus:
    shortname = str("ubnt-mcastatus")
    name = str("UBNT MCA Status")
    command = str("mca-status")
    enabled = True

    def dataPack(self, data):
        if config.debug:
            print "UBNT_MCAStatus.dataPack invoked with data:"
            sys.stdout.write(data)
            print "========================="

        devinfo = []
        params = []

        for line in data.splitlines(True):
            # grab device info into seperate object
            if len(line.strip().split('=')) > 1 and len(line.strip().split(',')) > 1:
                for item in line.strip().split(','):
                    devinfo.append(item)
                continue
            # everything else
            if line.strip() != '':
                params.append(line.strip())

        return { 'devinfo' : devinfo, 'params' : params }

    def queryHandler(self, query, data):
        found = False

        if config.debug:
            print "UBNT_MCAStatus.queryHandler invoked with query:", query

        # device information query
        for line in data['devinfo']:
            name, value = line.split('=')
            if query == name:
                found = True
                break

        # param query
        if not found:
            found, value = utils.mcastatus_get_param(data, query)

        # custom query (calculations and/or multiple dataset return)
        if not found:
            if query == "wlanFadeMarginCustom":
                ret, noiseVal = utils.mcastatus_get_param(data, "noise")
                ret, signalVal = utils.mcastatus_get_param(data, "signal")
                value = str(int(noiseVal) - int(signalVal))
                found = True
            elif query == "wlanSignalAllCustom":
                ret, noiseVal = utils.mcastatus_get_param(data, "noise")
                ret, signalVal = utils.mcastatus_get_param(data, "signal")
                fadeVal = str(int(noiseVal) - int(signalVal))
                
                value = "signal:" + signalVal + ' ' + \
                            "noise:" + noiseVal + ' ' + \
                            "fade:" + fadeVal
                found = True
            elif query == "wlanAirmaxCustom":
                ret, wlanPollingQuality = utils.mcastatus_get_param(data, "wlanPollingQuality")
                ret, wlanPollingCapacity = utils.mcastatus_get_param(data, "wlanPollingCapacity")
                ret, wlanPollingPriority = utils.mcastatus_get_param(data, "wlanPollingPriority")
                
                value =  "amQuality:" + wlanPollingQuality + ' ' + \
                            "amCapacity:" + wlanPollingCapacity + ' ' + \
                            "amPriority:" + wlanPollingPriority
                found = True
            elif query == "lanSpeedCustom":
                ret, lanSpeedVal = utils.mcastatus_get_param(data, "lanSpeed")
                if lanSpeedVal == "10Mbps-Half":
                    value = '1'
                elif lanSpeedVal == "10Mbps-Full":
                    value = '2'
                elif lanSpeedVal == "100Mbps-Half":
                    value = '3'
                elif lanSpeedVal == "100Mbps-Full":
                    value = '4'
                else:
                    value = '0'
                found = True
            elif query == "wlanRxErrAllCustom":
                ret, wlanRxErrNwid = utils.mcastatus_get_param(data, "wlanRxErrNwid")
                ret, wlanRxErrCrypt = utils.mcastatus_get_param(data, "wlanRxErrCrypt")
                ret, wlanRxErrFrag = utils.mcastatus_get_param(data, "wlanRxErrFrag")
                ret, wlanRxErrRetries = utils.mcastatus_get_param(data, "wlanRxErrRetries")
                ret, wlanRxErrBmiss = utils.mcastatus_get_param(data, "wlanRxErrBmiss")
                ret, wlanRxErrOther = utils.mcastatus_get_param(data, "wlanRxErrOther")
                
                value = "wlanRxErrNwid:" + wlanRxErrNwid + ' ' + \
                            "wlanRxErrCrypt:" + wlanRxErrCrypt + ' ' + \
                            "wlanRxErrFrag:" + wlanRxErrFrag + ' ' + \
                            "wlanRxErrRetries:" + wlanRxErrRetries + ' ' + \
                            "wlanRxErrBmiss:" + wlanRxErrBmiss + ' ' + \
                            "wlanRxErrOther:" + wlanRxErrOther
                found = True
            elif query == "wlanRatesAllCustom":
                ret, wlanRxRate = utils.mcastatus_get_param(data, "wlanRxRate")
                ret, wlanTxRate = utils.mcastatus_get_param(data, "wlanTxRate")
                
                value = "wlanRxRate:" + wlanRxRate + ' ' + \
                            "wlanTxRate:" + wlanTxRate
                found = True
            elif query == "mem-all":
                ret, memTotal = utils.mcastatus_get_param(data, "memTotal")
                ret, memFree = utils.mcastatus_get_param(data, "memFree")
                ret, memBuffers = utils.mcastatus_get_param(data, "memBuffers")
                ret, memCached = utils.mcastatus_get_param(data, "memCached")
                
                value = "memTotal:" + memTotal + ' ' + \
                            "memFree:" + memFree + ' ' + \
                            "memBuffers:" + memBuffers + ' ' + \
                            "memCached:" + memCached
                found = True
                

        if found:
            return True, value

        return False, None

# plugin wstalist - handles information from wstalist
class plugin_UBNT_WStaList:
    shortname = str("ubnt-wstalist")
    name = str("UBNT Wireless Station List")
    command = str("wstalist")
    enabled = True

    def dataPack(self, data):
        from json import loads

        if config.debug:
            print "UBNT_WStaList.dataPack invoked with data:"
            sys.stdout.write(data)
            print "========================="

        rawSet = loads(data)

        # find mac for this station for use as index id
        staArray = []
        macIndex = ''

        for sEntry in rawSet:
            for pItem in sEntry:
                if pItem == "mac":
                    macIndex = sEntry[pItem]
            staArray.append( { macIndex : sEntry } )

        return staArray

    def queryHandler(self, query, data):
        import re
        output_delimiter = '!'
        found = False
        
        if config.debug:
            print "UBNT_WStaList.queryHandler invoked with query:", query
        
        # break up raw arguments into list
        rawArgList = [ a for a in query.split(',') if re.search('^.+=.+', a, re.I) ]
        
        params = {}
        
        # build the parameter list
        if len(rawArgList):
            for arg in rawArgList:
                name, value = arg.split('=')
                params[name] = value

        if params['mode'] == "arg-index":
            if params['format'] == "xm5_cacti-0.8":
                # process index, query, or get
                # indexes - mac address
                if sys.argv[-1] == "index":
                    for id in data:
                        sys.stdout.write(id.keys()[0] + '\n')
                    return True, None
                # perform query - in cacti this is the defined 'input' type
                elif sys.argv[-2] == "query":
                    for id in data:
                        sys.stdout.write(id.keys()[0] + output_delimiter + str(id[id.keys()[0]][sys.argv[-1]]) + '\n')
                    return True, None
                elif sys.argv[-3] == "get":
                    # custom query
                    if str(sys.argv[-2]) == "fadeMarginCustom":
                        ret, noiseVal = utils.wstalist_get_param(data, "noisefloor", str(sys.argv[-1]))
                        ret, signalVal = utils.wstalist_get_param(data, "signal", str(sys.argv[-1]))
                        value = str(int(noiseVal) - int(signalVal))
                        found = True
                    else:
                        found, value = utils.wstalist_get_param(data, str(sys.argv[-2]), str(sys.argv[-1]))
        elif params['mode'] == "get-index":
            if config.debug: print "mode not implemented"
        elif params['mode'] == "list-index":
            if config.debug: print "mode not implemented"
        elif config.debug:
            print "UBNT_WstaList.queryHandler: error - invalid mode %s" % params['mode']
            
        if found:
            return True, value

        return False, None

# plugin ram - handles information from /proc/meminfo
# the ssh query to the device impacts the memfree value quite heavily
# it provides more information, but is not as accurate as using snmp service
# also, mca-status provides basic memory use information
class plugin_UBNT_RAM:
    shortname = str("ubnt-ram")
    name = str("UBNT RAM")
    command = str("cat /proc/meminfo")
    enabled = False
    
    def dataPack(self, data):
        if config.debug:
            print "UBNT_RAM.dataPack invoked with data:"
            sys.stdout.write(data)
            print "========================="
            
        retArr = []
        for row in data.split('\n'):
            if len(row):
                name, value = "".join(row.split()).rstrip('kB').lower().split(':')
                retArr.append({ name : value })

        return retArr
        
    def queryHandler(self, query, data):
        found = False

        if config.debug:
            print "UBNT_RAM.queryHandler invoked with query:", query

        for item in data:
            if query.lower() == "ram-" + item.keys()[0]:
                value = item[item.keys()[0]]
                found = True
                break

        if found:
            return True, value

        return False, None

# plugin cputop - handles information from top
# The first instance is filtered out because it contains the load from the program call.
# perhaps there is a better (faster) way to obtain this information - currently adds
# >1 sec to polling.
class plugin_UBNT_CPUTop:
    shortname = str("ubnt-cputop")
    name = str("UBNT CPU Top")
    command = str("top -b -n2 -d1 | grep '^CPU:' | tail -n1")
    enabled = True

    def dataPack(self, data):
        if config.debug:
            print "UBNT_CPUTop.dataPack invoked with data:"
            sys.stdout.write(data)
            print "========================="

        dataSet = "".join([ chr for chr in data if chr not in ('%') ]).split()

        return {
            "user" : dataSet[1],
            "system" : dataSet[3],
            "nice" : dataSet[5],
            "idle" : dataSet[7],
            "io" : dataSet[9],
            "irq" : dataSet[11],
            "softirq" : dataSet[13]
        }

    def queryHandler(self, query, data):
        found = False

        if config.debug:
            print "UBNT_CPUTop.queryHandler invoked with query:", query

        if query == "cpu-all":
            value = "cpu-idle:" + data["idle"] + ' ' + \
                        "cpu-io:" + data["io"] + ' ' + \
                        "cpu-irq:" + data["irq"] + ' ' + \
                        "cpu-nice:" + data["nice"] + ' ' + \
                        "cpu-softirq:" + data["softirq"] + ' ' + \
                        "cpu-system:" + data["system"] + ' ' + \
                        "cpu-user:" + data["user"]
            found = True
        else:
            for item in data.keys():
                if query == "cpu-" + item:
                    value = data[item]
                    found = True
                    break

        if found:
            return True, value

        return False, None

plugins_available = [
    plugin_UBNT_MCAStatus,
    plugin_UBNT_WStaList,
    plugin_UBNT_RAM,
    plugin_UBNT_CPUTop
]

""" end plugin definitions """

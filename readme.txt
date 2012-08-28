scgrab.py
        version: 0.1.3 - Copyright 2011 The SCGrab Developers

Valid arguments are:

-h, --help                 Prints this help menu
-v                         Enables verbose debugging
--version                  Print script version and exit
--host=xxx.xxx.xxx.xxx     Specify target host by ip address or host name
--port=xxxx                Specify the port of the target ssh server
--timeout=xxx              Specify the timeout for connecting to the ssh server
--plugin=xxx               Specify plugin to use for query
--query=xxx                Specify query to use for plugin
--scriptdir=xxx            Specify directory where this script resides
                           This value is an absolute path
--cachedir=xxx             Specify directory to store cached data (cache)
                           This value is relative to scriptdir
--flushcache               This will remove all cache files
--flushlocks               This will remove all cache file locks
--authdir=xxx              Specify directory to store auth data (auth)
                           This value is relative to scriptdir
--authcred=xxx             Specify the auth file containing user/pass
        File Format:
                username:myuser
                password:mypass
--authkey=xxx              Specify the name of the private key for ssh
                           session.  If key uses password protection then
                           you must also specify --authcred
--authkeydsa               Specified key is DSA - default RSA
--autokeylookup            Enables searching for private keys
--threshold=xxx            Specify seconds until data is recached (240)

Example usage:

        scgrab.py \
         --host=10.9.3.25 --authcred=userpass.txt \
         --plugin=ubnt-mcastatus --query=signal


Current plugins:

        ubnt-mcastatus - UBNT MCA Status
	ubnt-wstalist - UBNT Wireless Station List
	ubnt-ram - UBNT RAM (disabled)
        ubnt-cputop - UBNT CPU Top

Example script usage for user/pass authentication:

python <path_cacti>/scripts/scgrab/scgrab.py 
	--authcred=userpass.txt 
	--host=<host> 
	--plugin=ubnt-mcastatus 
	--query=wlanTxRate

Example script usage for private key:

python <path_cacti>/scripts/scgrab/scgrab.py 
	--authcred=monitor-privatekeypass.txt 
	--authkey=private.key 
	--host=<host> 
	--plugin=ubnt-mcastatus
	--query=wlanFadeMarginCustom

Some notes on security:
-Please make sure your web server has anonymous access disabled for the
cacti scripts/scgrab/ directory or is using some other means of locking this down.
For apache, there is a sample .htaccess file for your review.
-The script can be placed in any directory and should be able to auto-detect the
script directory without using --scriptdir.  It does not have to be web accessible.

Some notes on SSH key authentication:
-Paramiko addon for python will need patching when using an AES-128-CBC cipher:
     http://www.mail-archive.com/paramiko@lag.net/msg00479.html
-Script was tested using keys generated with ssh-keygen.
     puttygen may also work, but note that the radio will want a single line format during import.
-SSH Keys are stored in auth/keys/ - the script may also work with found private keys via --autokeylookup, but this is untested.
-Password field must be present in auth file specified by --authcred if private key is password protected.
-You must add the public key to the radio(s) you want to poll when using --authkey.
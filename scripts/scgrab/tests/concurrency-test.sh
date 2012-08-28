#!/bin/sh

HOSTNAME="10.4.1.2"
echo "starting test"
python scgrab.py --scriptdir=/root/ubnt-dev/scgrab-auth --flushcache
sleep 3
date
python scgrab.py --scriptdir=/root/ubnt-dev/scgrab-auth --host=$HOSTNAME --threshold=15 --authcred=userpass.txt --plugin=ubnt-cputop --query=cpu-idle &
python scgrab.py --scriptdir=/root/ubnt-dev/scgrab-auth --host=$HOSTNAME --threshold=15 --authcred=userpass.txt --plugin=ubnt-cputop --query=cpu-system &
python scgrab.py --scriptdir=/root/ubnt-dev/scgrab-auth --host=$HOSTNAME --threshold=15 --authcred=userpass.txt --plugin=ubnt-cputop --query=cpu-io &
python scgrab.py --scriptdir=/root/ubnt-dev/scgrab-auth --host=$HOSTNAME --threshold=15 --authcred=userpass.txt --plugin=ubnt-cputop --query=cpu-user &
python scgrab.py --scriptdir=/root/ubnt-dev/scgrab-auth --host=$HOSTNAME --threshold=15 --authcred=userpass.txt --plugin=ubnt-cputop --query=cpu-softirq &
python scgrab.py --scriptdir=/root/ubnt-dev/scgrab-auth --host=$HOSTNAME --threshold=15 --authcred=userpass.txt --plugin=ubnt-cputop --query=cpu-irq &
python scgrab.py --scriptdir=/root/ubnt-dev/scgrab-auth --host=$HOSTNAME --threshold=15 --authcred=userpass.txt --plugin=ubnt-mcastatus --query=wlanTxRate &
python scgrab.py --scriptdir=/root/ubnt-dev/scgrab-auth --host=$HOSTNAME --threshold=15 --authcred=userpass.txt --plugin=ubnt-mcastatus --query=wlanRxRate &
python scgrab.py --scriptdir=/root/ubnt-dev/scgrab-auth --host=$HOSTNAME --threshold=15 --authcred=userpass.txt --plugin=ubnt-mcastatus --query=signal &
python scgrab.py --scriptdir=/root/ubnt-dev/scgrab-auth --host=$HOSTNAME --threshold=15 --authcred=userpass.txt --plugin=ubnt-mcastatus --query=noise &
python scgrab.py --scriptdir=/root/ubnt-dev/scgrab-auth --host=$HOSTNAME --threshold=15 --authcred=userpass.txt --plugin=ubnt-mcastatus --query=wlanFadeMarginCustom &
python scgrab.py --scriptdir=/root/ubnt-dev/scgrab-auth --host=$HOSTNAME --threshold=15 --authcred=userpass.txt --plugin=ubnt-mcastatus --query=lanSpeed &
python scgrab.py --scriptdir=/root/ubnt-dev/scgrab-auth --host=$HOSTNAME --threshold=15 --authcred=userpass.txt --plugin=ubnt-mcastatus --query=lanSpeedCustom &


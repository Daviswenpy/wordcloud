#
# Regular cron jobs for the itpserver package
#
0 4	* * *	root	[ -x /usr/bin/itpserver_maintenance ] && /usr/bin/itpserver_maintenance

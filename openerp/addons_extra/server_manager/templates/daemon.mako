#!/bin/sh

### BEGIN INIT INFO
# Provides:             openerp-server
# Required-Start:       $remote_fs $syslog
# Required-Stop:        $remote_fs $syslog
# Should-Start:         $network
# Should-Stop:          $network
# Default-Start:        2 3 4 5
# Default-Stop:         0 1 6
# Short-Description:    Enterprise Resource Management software
# Description:          Open ERP is a complete ERP and CRM software.
### END INIT INFO

PATH=/bin:/sbin:/usr/bin
DAEMON=/etc/openerp/server/openerp-server
NAME=${NAME}
DESC=${DESC}

# Specify the user name (Default: openerp).
USER=${USER}

# Specify an alternate config file (Default: /etc/openerp-server.conf).
CONFIGFILE="${CONFIGFILE}"
# pidfile
PIDFILE=/var/run/$NAME.pid

# Additional options that are passed to the Daemon.
DAEMON_OPTS="-c $CONFIGFILE"

[ -x $DAEMON ] || exit 0
[ -f $CONFIGFILE ] || exit 0

checkpid() {
    [ -f $PIDFILE ] || return 1
    pid=`cat $PIDFILE`
    [ -d /proc/$pid ] && return 0
    return 1
}

case "${CASE}" in
        start)
                echo -n "Starting ${DESC1}: "

                start-stop-daemon --start --quiet --pidfile ${PIDFILE1} \
                        --chuid ${USER1} --background --make-pidfile \
                        --exec ${DAEMON1} -- ${DAEMON_OPTS1}

                echo "${NAME1}."
                ;;

        stop)
                echo -n "Stopping ${DESC1}: "

                start-stop-daemon --stop --quiet --pidfile ${PIDFILE1} \
                        --oknodo

                echo "${NAME1}."
                ;;

        restart|force-reload)
                echo -n "Restarting ${DESC1}: "

                start-stop-daemon --stop --quiet --pidfile ${PIDFILE1} \
                        --oknodo

                sleep 1

                start-stop-daemon --start --quiet --pidfile ${PIDFILE1} \
                        --chuid ${USER1} --background --make-pidfile \
                        --exec ${DAEMON1} -- ${DAEMON_OPTS1}

                echo "${NAME1}."
                ;;

        *)
                N=/etc/init.d/${NAME1}
                echo "Usage: ${NAME1} {start|stop|restart|force-reload}" >&2
                exit 1
                ;;
esac

exit 0
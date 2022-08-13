#!/usr/bin/env bash

[ -e "/root/functions" ] && . /root/functions
[ -e "/dev/shm/.env" ] && . /dev/shm/.env

if [[ "${DEBUG}" == "1" ]]; then
    env
fi


usage() {
    echo "-s : remove all limits"
}


function limitExists {
    if [[ -n $(tc qdisc show | grep "ingress .* ${EXT_IFACE}") ]]
    then
        return 0
    else
        return 1
    fi
}


function ifaceExists {
    if [[ -n $(ifconfig -a | sed 's/[ \t].*//;/^\(lo\|\)$/d' | grep ifb0) ]]
    then
        return 0
    else
        return 1
    fi
}


function ifaceIsUp {
    if [[ -n $(ifconfig | sed 's/[ \t].*//;/^\(lo\|\)$/d' | grep ifb0) ]]
    then
        return 0
    else
        return 1
    fi
}


function createLimit {
    # redirect ingress
    tc qdisc add dev ${EXT_IFACE} handle ffff: ingress
    tc filter add dev ${EXT_IFACE} parent ffff: protocol all u32 match u32 0 0 action mirred egress redirect dev ifb0
    tc filter add dev ${EXT_IFACE} parent ffff: protocol all u32 match u32 0 0 action mirred egress redirect dev ifb0

    # apply egress rules to external inteface(s)
    tc qdisc add dev ${EXT_IFACE} root handle 1: htb default 10
    tc class add dev ${EXT_IFACE} parent 1: classid 1:1 htb rate ${MAX_RATE}mbit
    tc class add dev ${EXT_IFACE} parent 1:1 classid 1:10 htb rate ${MAX_RATE}mbit

    # and same for our relaying virtual interfaces (to simulate ingress)
    tc qdisc add dev ifb0 root handle 1: htb default 10
    tc class add dev ifb0 parent 1: classid 1:1 htb rate ${MAX_RATE}mbit
    tc class add dev ifb0 parent 1:1 classid 1:10 htb rate ${MAX_RATE}mbit
}


function updateLimit {
    tc filter replace dev ${EXT_IFACE} parent ffff: protocol all u32 match u32 0 0 action mirred egress redirect dev ifb0
    tc filter replace dev ${EXT_IFACE} parent ffff: protocol all u32 match u32 0 0 action mirred egress redirect dev ifb0

    # apply egress rules to external inteface(s)
    tc class replace dev ${EXT_IFACE} parent 1: classid 1:1 htb rate ${MAX_RATE}mbit
    tc class replace dev ${EXT_IFACE} parent 1:1 classid 1:10 htb rate ${MAX_RATE}mbit

    # same for our relaying virtual interfaces (to simulate ingress)
    tc class replace dev ifb0 parent 1: classid 1:1 htb rate ${MAX_RATE}mbit
    tc class replace dev ifb0 parent 1:1 classid 1:10 htb rate ${MAX_RATE}mbit
}


function removeLimit {
    if limitExists ; then
        tc qdisc del dev ${EXT_IFACE} ingress
        tc qdisc del dev ${EXT_IFACE} root
        tc qdisc del dev ifb0 root
    fi

    if ifaceIsUp ; then
        ip link set dev ifb0 down
    fi
}


# main

while getopts ':h:s' option; do
    case "${option}" in
     s) STOP=1
        ;;
     h) usage
        exit
        ;;
    esac
done

if [[ $(whoami) != "root" ]]; then
    echo "script must be executed with root privileges"
    echo ${usage}
    exit 1
fi

if [[ ${STOP} -eq 1 ]]; then
    echo "removing ingress limit..."
    removeLimit
    echo "ingress limit removed"
    exit 0
fi

if [ "${MAX_RATE}" == "0" ]; then
    echo "no limit specified, exiting..."
    exit 0

elif [ "${MAX_RATE}" != "0" ]; then
    if ! ifaceExists ; then
        echo "creating ifb0..."
        modprobe ifb numifbs=1
        if ! ifaceExists ; then
            echo "failed to create ifb0"
            exit 2
        fi
    fi
    if ifaceIsUp ; then
        echo "ifb0 is already up"
    else
        echo "set ifb0 up"
        ip link set dev ifb0 up
        if ifaceIsUp ; then
            echo "ifb0 is up"
        else
            echo "failed to enable ifb0 by ip link"
            exit 3
        fi
    fi
    if limitExists ; then
        echo "updating limit..."
        updateLimit
    else
        echo "creating limit..."
        createLimit
    fi
    echo "limit created"
    exit 0

else
    usage
fi

#!/usr/bin/env bash

[ -e "/root/functions" ] && . /root/functions
[ -e "/dev/shm/.env" ] && . /dev/shm/.env

if [[ "${DEBUG}" == "1" ]]; then
    env
fi

statedir=${TEMPDIR}/openvpn

function bwlimit-enable() {
    ip=$1
    user=$2

    # Disable if already enabled.
    bwlimit-disable $ip

    # Find unique classid.
    if [ -f $statedir/$ip.classid ]; then
        # Reuse this IP's classid
        classid=`cat $statedir/$ip.classid`
    else
        if [ -f $statedir/last_classid ]; then
            classid=`cat $statedir/last_classid`
            classid=$((classid+1))
        else
            classid=1
        fi
        echo $classid > $statedir/last_classid
    fi

    downrate=${3}mbit
    uprate=${3}mbit

    proto=ip
    mask=32
    if [[ $(echo $ip | grep -P '[a-zA-Z0-9]{1,4}:+.*[a-zA-Z0-9]{1,4}+') ]]; then
        proto=ip6
        mask=128
    fi

    echo "limit dev=$dev ip=${ip} user=${user} classid=$classid downrate=$downrate uprate=$uprate proto=$proto mask=$mask"

    # Limit traffic from VPN server to client
    tc class add dev $dev parent 1: classid 1:$classid htb rate $downrate
    tc filter add dev $dev protocol all parent 1:0 prio 1 u32 match $proto dst $ip/$mask flowid 1:$classid

    # Limit traffic from client to VPN server
    tc filter add dev $dev parent ffff: protocol all prio 1 u32 match $proto src $ip/$mask police rate $uprate burst 80k drop flowid :$classid

    # Store classid and dev for further use.
    echo $classid > $statedir/$ip.classid
    echo $dev > $statedir/$ip.dev
}

function bwlimit-disable() {
    ip=$1

    if [ ! -f $statedir/$ip.classid ]; then
        return
    fi
    if [ ! -f $statedir/$ip.dev ]; then
        return
    fi

    classid=`cat $statedir/$ip.classid`
    dev=`cat $statedir/$ip.dev`

    proto=ip
    mask=32
    if [[ $(echo $ip | grep -P '[a-zA-Z0-9]{1,4}:+.*[a-zA-Z0-9]{1,4}+') ]]; then
        proto=ip6
        mask=128
    fi

    echo "unlimit dev=$dev ip=${ip} classid=$classid proto=$proto mask=$mask"

    tc filter del dev $dev protocol all parent 1:0 prio 1 u32 match $proto dst $ip/$mask
    tc class del dev $dev classid 1:$classid

    tc filter del dev $dev parent ffff: protocol all prio 1 u32 match $proto src $ip/$mask

    # Remove .dev but keep .classid so it can be reused.
    rm $statedir/$ip.dev
}

function get_max_client_bw() {
    # hack around resin.io missing RESIN_APP_ID in v1.8.0
    if [[ -z ${RESIN_APP_ID} ]]; then
       RESIN_APP_ID=101253
    fi

    max_dev_bw=$(curl ${CURL_OPTS} --connect-timeout ${CONN_TIMEOUT} --max-time $((${CONN_TIMEOUT}*2)) "${API_HOST}/api/v${API_VERSION}/device/${1}/env/MAX_BANDWDTH" -H 'Content-Type: application/json' -H "X-Auth-Token: ${API_SECRET}")
    if [ $? -gt 0 ]; then
        max_app_bw=$(curl ${CURL_OPTS} --connect-timeout ${CONN_TIMEOUT} --max-time $((${CONN_TIMEOUT}*2)) "${API_HOST}/api/v${API_VERSION}/app/${RESIN_APP_ID}/env/MAX_BANDWDTH" -H 'Content-Type: application/json' -H "X-Auth-Token: ${API_SECRET}")
        if [ $? -eq 0 ]; then
            echo ${max_app_bw}; return 0
        else
            echo ${MAX_BANDWDTH}; return 0
        fi
    else
        echo ${max_dev_bw}; return 0
    fi
}


# Make sure queueing discipline is enabled.
tc qdisc add dev $dev root handle 1: htb 2>/dev/null || /bin/true
tc qdisc add dev $dev handle ffff: ingress 2>/dev/null || /bin/true

case "$1" in
    add|update)
        max_bw=$(get_max_client_bw ${3})
        echo "get_max_client_bw=${max_bw}"
        if [[ ! "${max_bw}" == "0" ]]; then
            bwlimit-enable $2 $3 ${max_bw}
        else
            echo "no limit specified, exiting..."
        fi
        ;;
    delete)
        bwlimit-disable $2
        ;;
    *)
        echo "$0: unknown operation [$1]" >&2
        exit 1
        ;;
esac

exit 0

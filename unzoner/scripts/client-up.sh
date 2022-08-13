#!/usr/bin/env bash

[ -e "/root/functions" ] && . /root/functions
[ -e "/dev/shm/.env" ] && . /dev/shm/.env

if [[ "${DEBUG}" == "1" ]]; then
    env
fi

log "client-up: \$0=$0 \$1=$1 \$2=$2 \$3=$3 \$5=$4 \$5=$5 \$6=$6 \$7=$7 \$8=$8 \$9=$9"

log "disabling rp_filter iface=${1}..."
sysctl -w "net.ipv4.conf.${1}.rp_filter=0"

log 'adding ipv4 policy route...'
ip route add default dev ${1} table ${DNS_SUB_DOMAIN}

log 'setting client MTU...'
ip link set dev ${1} mtu ${LINK_MTU_CLIENT}

log 'adding ipv4 rules...'
for if in ${INT_IFACES}; do
    ipt_add_rule nat A "PREROUTING -i ${if} -p tcp --dport 53 -j DNAT --to 127.0.0.1"
    ipt_add_rule nat A "PREROUTING -i ${if} -p udp --dport 53 -j DNAT --to 127.0.0.1"

    if [[ "${LOCAL_DNS}" == "0" ]]; then
        for dns in ${DNS_SERVERS}; do
            ip route add ${dns}/32 dev ${1}
        done
    fi

    ipt_add_rule filter A "FORWARD -i ${EXT_IFACE} -o ${if} -m state --state RELATED,ESTABLISHED -j ACCEPT"
    ipt_add_rule filter A "FORWARD -i ${if} -o ${EXT_IFACE} -j ACCEPT"
    ipt_add_rule filter A "FORWARD -i ${1} -o ${if} -j ACCEPT"
    ipt_add_rule filter A "FORWARD -i ${if} -o ${1} -j ACCEPT"
done

ipt_add_rule nat A "POSTROUTING -o ${1} -j MASQUERADE"
ipt_add_rule nat A "POSTROUTING -o ${EXT_IFACE} -j MASQUERADE"

if [[ "${TUN_IPV6}" == "1" ]] && [[ $(ip6tables -t nat -L) ]]; then
    log 'adding ipv6 rules...'
    for if in ${INT_IFACES}; do
        ip6_add_rule nat A "PREROUTING -i ${if} -p tcp --dport 53 -j DNAT --to ::1"
        ip6_add_rule nat A "PREROUTING -i ${if} -p udp --dport 53 -j DNAT --to ::1"

        if [[ "${LOCAL_DNS}" == "0" ]]; then
            for dns in ${DNS_SERVERS}; do
                ip -6 route add ${dns}/128 dev ${1}
            done
        fi

        if [[ "${AF}" == "6" ]] && [[ $(ip6tables -t nat -L) ]]; then
            ip6t_add_rule filter A "FORWARD -i ${EXT_IFACE} -o ${if} -m state --state RELATED,ESTABLISHED -j ACCEPT"
            ip6t_add_rule filter A "FORWARD -i ${if} -o ${EXT_IFACE} -j ACCEPT"
        fi

        ip6t_add_rule filter A "FORWARD -i ${1} -o ${if} -j ACCEPT"
        ip6t_add_rule filter A "FORWARD -i ${if} -o ${1} -j ACCEPT"
    done

    ip6_add_rule nat A "POSTROUTING -o ${1} -j MASQUERADE"

    if [[ "${AF}" == "6" ]] && [[ $(ip6tables -t nat -L) ]]; then
        ip6_add_rule nat A "POSTROUTING -o ${EXT_IFACE} -j MASQUERADE"
    fi
fi

[ -f ${DATADIR}/docker4.rules ]\
  && log 'recovering Docker iptables chains...'\
  && iptables-restore -n < ${DATADIR}/docker4.rules || true

if [[ "${AF}" == "6" ]] && [[ $(ip6tables -t nat -L) ]]; then
    [ -f ${DATADIR}/docker4.rules ]\
    && log 'recovering Docker ip6tables chains...'\
    && ip6tables-restore -n < ${DATADIR}/docker6.rules || true
fi

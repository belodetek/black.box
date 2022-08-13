#!/usr/bin/env bash

[ -e "/root/functions" ] && . /root/functions
[ -e "/dev/shm/.env" ] && . /dev/shm/.env

if [[ "${DEBUG}" == "1" ]]; then
    env
fi

log "client-down: \$0=$0 \$1=$1 \$2=$2 \$3=$3 \$5=$4 \$5=$5 \$6=$6 \$7=$7 \$8=$8 \$9=$9"

log 'removing ipv4 policy route...'
ip route del default dev ${1} table ${DNS_SUB_DOMAIN}

log 'removing ipv6 policy route...'
if [[ "${TUN_IPV6}" == "1" ]]; then
    ip -6 route del default dev ${1} table ${DNS_SUB_DOMAIN}
fi

log 'cleaning-up routing table...'
for subnet in 0 64 128 192; do
    if [[ $(ip route | grep "${subnet}.0.0.0/2") ]]; then
        ip route del ${subnet}.0.0.0/2
    fi
done

log 'removing ipv4 rules...'
for if in ${INT_IFACES}; do
    if [[ "${if}" =~ tun? ]]; then
        while [[ "${subnet}" == '' ]]; do
            subnet=$(with_backoff get_tun_subnet ${if})
            sleep 1
        done
    else
        while [[ "${subnet}" == '' ]]; do
            subnet=$(with_backoff get_subnet ${if})
            sleep 1
        done
    fi

    log "if=${if} subnet=${subnet}"

    ipt_del_rule nat "PREROUTING -i ${if} -p tcp --dport 53 -j DNAT --to 127.0.0.1"
    ipt_del_rule nat "PREROUTING -i ${if} -p udp --dport 53 -j DNAT --to 127.0.0.1"

    if [[ "${LOCAL_DNS}" == "0" ]]; then
        for dns in ${DNS_SERVERS}; do
            ip route del ${dns}/32 dev ${1}
        done
    fi

    if [[ "${POLICY_ROUTING}" == "1" ]]; then
        ipt_del_rule mangle "PREROUTING -s 10/8,172.16/12,192.168/16,${subnet} -i ${if} -m set --match-set domain-filter-ipv4 dst -j MARK --set-mark 0x1"
    else
        ipt_del_rule mangle "PREROUTING -s 10/8,172.16/12,192.168/16,${subnet} -i ${if} -m set --match-set domain-filter-ipv4 dst -j MARK --set-mark 0x3"
        ipt_del_rule mangle "PREROUTING -s 10/8,172.16/12,192.168/16,${subnet} -i ${if} -m mark --mark 0x3 -j RETURN"
        ipt_del_rule mangle "PREROUTING -s 10/8,172.16/12,192.168/16,${subnet} -i ${if} -j MARK --set-mark 0x1"
    fi

    ipt_del_rule filter "FORWARD -i ${EXT_IFACE} -o ${if} -m state --state RELATED,ESTABLISHED -j ACCEPT"
    ipt_del_rule filter "FORWARD -i ${if} -o ${EXT_IFACE} -j ACCEPT"
    ipt_del_rule filter "FORWARD -i ${1} -o ${if} -j ACCEPT"
    ipt_del_rule filter "FORWARD -i ${if} -o ${1} -j ACCEPT"
done

ipt_del_rule nat "POSTROUTING -o ${1} -j MASQUERADE"
ipt_del_rule nat "POSTROUTING -o ${EXT_IFACE} -j MASQUERADE"

if [[ "${TUN_IPV6}" == "1" ]] && [[ $(ip6tables -t nat -L) ]]; then
    log 'removing ipv6 rules...'
    for if in ${INT_IFACES}; do
        if [[ "${if}" =~ tun? ]]; then
            while [[ "${subnet6}" == '' ]]; do
                subnet6=$(with_backoff get_tun_subnet6 ${if})
                sleep 1
            done
        else
            while [[ "${subnet6}" == '' ]]; do
                subnet6=$(with_backoff get_subnet6 ${if})
                sleep 1
            done
        fi

        log "if=${if} subnet=${subnet6}"

        ip6t_del_rule nat "PREROUTING -i ${if} -p tcp --dport 53 -j DNAT --to ::1"
        ip6t_del_rule nat "PREROUTING -i ${if} -p udp --dport 53 -j DNAT --to ::1"

        if [[ "${LOCAL_DNS}" == "0" ]]; then
            for dns in ${DNS_SERVERS}; do
                ip -6 route add ${dns}/128 dev ${1}
            done
        fi

        if [[ "${POLICY_ROUTING}" == "1" ]]; then
            ip6t_del_rule mangle "PREROUTING -s 10/8,172.16/12,192.168/16,${subnet6} -i ${if} -m set --match-set domain-filter-ipv4 dst -j MARK --set-mark 0x1"
        else
            ip6t_del_rule mangle "PREROUTING -s 10/8,172.16/12,192.168/16,${subnet6} -i ${if} -m set --match-set domain-filter-ipv4 dst -j MARK --set-mark 0x3"
            ip6t_del_rule mangle "PREROUTING -s 10/8,172.16/12,192.168/16,${subnet6} -i ${if} -m mark --mark 0x3 -j RETURN"
            ip6t_del_rule mangle "PREROUTING -s 10/8,172.16/12,192.168/16,${subnet6} -i ${if} -j MARK --set-mark 0x1"
        fi

        if [[ "${AF}" == "6" ]] && [[ $(ip6tables -t nat -L) ]]; then
            ip6t_del_rule filter "FORWARD -i ${EXT_IFACE} -o ${if} -m state --state RELATED,ESTABLISHED -j ACCEPT"
            ip6t_del_rule filter "FORWARD -i ${if} -o ${EXT_IFACE} -j ACCEPT"
        fi

        if [[ "${AF}" == "6" ]] && [[ $(ip6tables -t nat -L) ]]; then
            ip6t_del_rule filter "FORWARD -i ${EXT_IFACE} -o ${if} -m state --state RELATED,ESTABLISHED -j ACCEPT"
            ip6t_del_rule filter "FORWARD -i ${if} -o ${EXT_IFACE} -j ACCEPT"
        fi

        ip6t_del_rule filter "FORWARD -i ${1} -o ${if} -j ACCEPT"
        ip6t_del_rule filter "FORWARD -i ${if} -o ${1} -j ACCEPT"
    done

    ip6t_del_rule nat "POSTROUTING -o ${1} -j MASQUERADE"

    if [[ "${AF}" == "6" ]] && [[ $(ip6tables -t nat -L) ]]; then
        ip6t_del_rule nat "POSTROUTING -o ${EXT_IFACE} -j MASQUERADE"
    fi
fi

[ -f ${WORKDIR}/resolv.dnsmasq_default ] && cat ${WORKDIR}/resolv.dnsmasq_default > ${WORKDIR}/resolv.dnsmasq

[ -f ${DATADIR}/docker4.rules ]\
  && log 'recovering Docker iptables chains...'\
  && iptables-restore -n < ${DATADIR}/docker4.rules || true

if [[ "${AF}" == "6" ]] && [[ $(ip6tables -t nat -L) ]]; then
    [ -f ${DATADIR}/docker4.rules ]\
    && log 'recovering Docker ip6tables chains...'\
    && ip6tables-restore -n < ${DATADIR}/docker6.rules || true
fi

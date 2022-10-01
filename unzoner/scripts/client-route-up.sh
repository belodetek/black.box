#!/usr/bin/env bash
shopt -s expand_aliases

[ -e "/root/functions" ] && . /root/functions
[ -e "/dev/shm/.env" ] && . /dev/shm/.env

if [[ "${DEBUG}" == "1" ]]; then
    env
fi

# https://community.openvpn.net/openvpn/wiki/Openvpn23ManPage#lbAU
log "script=${script_type} dev=${dev} ifconfig_local=${ifconfig_local} ifconfig_remote=${ifconfig_remote} ifconfig_netmask=${ifconfig_netmask} ifconfig_ipv6_local=${ifconfig_ipv6_local} ifconfig_ipv6_remote=${ifconfig_ipv6_remote} ifconfig_ipv6_netbits=${ifconfig_ipv6_netbits} remote_1=${remote_1}"

if [[ "${DEVICE_TYPE}" == "5" ]]; then
    log "remote=${remote_1} country=$(with_backoff geoiplookup ${remote_1} | head -n 1 | awk -F', ' '{print $2}')"

    # http://svn.dd-wrt.com/ticket/5697
    cat ${WORKDIR}/resolv.dnsmasq > ${WORKDIR}/resolv.dnsmasq_default
    env | grep 'dhcp-option DNS' | awk '{ print "nameserver " $3 }' > ${WORKDIR}/resolv.dnsmasq 
    log "resolv.dnsmasq=$(cat ${WORKDIR}resolv.dnsmasq)"
    touch ${WORKDIR}/resolv.dnsmasq
fi

IPADDR=$(with_backoff get_ipaddr)
SUBNET=$(with_backoff get_tun_subnet ${dev})

if [[ "${AF}" == "6" ]]; then
    IPADDR6=$(with_backoff get_ip6addr)
    SUBNET6=$(with_backoff get_tun_subnet6 ${dev})
fi

log "ipaddr=${IPADDR} subnet=${SUBNET} ipaddr6=${IPADDR6} subnet6=${SUBNET6}"

if [[ "${TUN_IPV6}" == "1" ]]; then
    log 'adding ipv6 policy route...'
    ip -6 route add default via ${ifconfig_ipv6_remote} dev ${dev} table ${DNS_SUB_DOMAIN} || true
fi

for if in ${INT_IFACES}; do
    log 'adding ipv4 rules...'
    unset subnet
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

    if [[ "${POLICY_ROUTING}" == "1" ]]; then
        ipt_add_rule mangle A "PREROUTING -s 10/8,172.16/12,192.168/16,${subnet} -i ${if} -m set --match-set domain-filter-ipv4 dst -j MARK --set-mark 0x1"
    else
        ipt_add_rule mangle A "PREROUTING -s 10/8,172.16/12,192.168/16,${subnet} -i ${if} -m set --match-set domain-filter-ipv4 dst -j MARK --set-mark 0x3"
        ipt_add_rule mangle A "PREROUTING -s 10/8,172.16/12,192.168/16,${subnet} -i ${if} -m mark --mark 0x3 -j RETURN"
        ipt_add_rule mangle A "PREROUTING -s 10/8,172.16/12,192.168/16,${subnet} -i ${if} -j MARK --set-mark 0x1"
    fi

    if [[ "${TUN_IPV6}" == "1" ]] && [[ $(ip6tables -t nat -L) ]]; then
        log 'adding ipv6 rules...'
        unset subnet
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

        if [[ "${POLICY_ROUTING}" == "1" ]]; then
            ip6t_add_rule mangle A "PREROUTING -s 10/8,172.16/12,192.168/16,${subnet6} -i ${if} -m set --match-set domain-filter-ipv4 dst -j MARK --set-mark 0x1"
        else
            ip6t_add_rule mangle A "PREROUTING -s 10/8,172.16/12,192.168/16,${subnet6} -i ${if} -m set --match-set domain-filter-ipv4 dst -j MARK --set-mark 0x3"
            ip6t_add_rule mangle A "PREROUTING -s 10/8,172.16/12,192.168/16,${subnet6} -i ${if} -m mark --mark 0x3 -j RETURN"
            ip6t_add_rule mangle A "PREROUTING -s 10/8,172.16/12,192.168/16,${subnet6} -i ${if} -j MARK --set-mark 0x1"
        fi
    fi
done

get_ping_host || true

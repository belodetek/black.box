#!/usr/bin/env bash
shopt -s expand_aliases

[ -e "/root/functions" ] && . /root/functions
[ -e "/dev/shm/.env" ] && . /dev/shm/.env

if [[ "${DEBUG}" == "1" ]]; then
    env
fi

# https://community.openvpn.net/openvpn/wiki/Openvpn23ManPage#lbAU
log "script=${script_type} dev=${dev}\
  ifconfig_local=${ifconfig_local}\
  ifconfig_remote=${ifconfig_remote}\
  ifconfig_netmask=${ifconfig_netmask}\
  ifconfig_ipv6_local=${ifconfig_ipv6_local}\
  ifconfig_ipv6_remote=${ifconfig_ipv6_remote}\
  ifconfig_ipv6_netbits=${ifconfig_ipv6_netbits}"

IPADDR=$(with_backoff get_ipaddr)
SUBNET=$(with_backoff get_tun_subnet ${dev})

if [[ "${AF}" == "6" ]]; then
    IPADDR6=$(with_backoff get_ip6addr)
    SUBNET6=$(with_backoff get_tun_subnet6 ${dev})
fi

log "ipaddr=${IPADDR} subnet=${SUBNET}\
  ipaddr6=${IPADDR6} subnet6=${SUBNET6} DNATs=${OPENVPN_PORTS_EXTRA}"

if [[ -n ${OPENVPN_PORTS_EXTRA} ]]; then
    log 'removing extra iptables rules...'
    for proto in ${TUN_PROTO}; do
        with_backoff ipt_del_rule filter "INPUT -i ${EXT_IFACE}\
          -p ${proto} -m multiport\
          --dports $(echo ${OPENVPN_PORTS_EXTRA} | sed 's/ /,/g') -j ACCEPT"
        with_backoff ipt_del_rule nat "PREROUTING -i ${EXT_IFACE}\
          ! -s $(get_subnet ${EXT_IFACE}) -d ${IPADDR}/32 -p ${proto}\
          -m multiport --dports $(echo ${OPENVPN_PORTS_EXTRA} | sed 's/ /,/g')\
          -j DNAT --to-destination :${OPENVPN_PORT}"
        with_backoff ipt_del_rule nat "POSTROUTING -o ${EXT_IFACE}\
          ! -d $(get_subnet ${EXT_IFACE}) -s ${SUBNET} -p ${proto} -m multiport\
          --sports $(echo ${OPENVPN_PORTS_EXTRA} | sed 's/ /,/g')\
          -j SNAT --to-source ${IPADDR}"

        if [[ $(ip6tables -t nat -L) ]] && [[ "${AF}" == "6" ]]; then
            log 'adding extra ip6tables rules...'
            with_backoff ip6t_del_rule filter "INPUT -i ${EXT_IFACE}\
              -p ${proto} -m multiport\
              --dports $(echo ${OPENVPN_PORTS_EXTRA} | sed 's/ /,/g') -j ACCEPT"
            with_backoff ip6_del_rule nat "PREROUTING -i ${EXT_IFACE}\
              ! -s $(get_subnet6 ${EXT_IFACE}) -d ${IPADDR6}/128 -p ${proto}\
              -m multiport\
              --dports $(echo ${OPENVPN_PORTS_EXTRA} | sed 's/ /,/g')\
              -j DNAT --to-destination :${OPENVPN_PORT}"
            with_backoff ip6t_del_rule nat "POSTROUTING -o ${EXT_IFACE}\
              ! -d $(get_subnet6 ${EXT_IFACE}) -s ${SUBNET6} -p ${proto}\
              -m multiport\
              --sports $(echo ${OPENVPN_PORTS_EXTRA} | sed 's/ /,/g')\
              -j SNAT --to-source ${IPADDR6}"
        fi
    done
fi

#!/usr/bin/env bash
shopt -s expand_aliases

[ -e "/root/functions" ] && . /root/functions
[ -e "/dev/shm/.env" ] && . /dev/shm/.env

if [[ "${DEBUG}" == "1" ]]; then
    env

    alias
fi

log "server-down: \$0=$0 \$1=$1 \$2=$2 \$3=$3 \$5=$4 \$5=$5 \$6=$6 \$7=$7 \$8=$8 \$9=$9"

log 'removing ipv4 rules...'
with_backoff ip4tables --wait -P FORWARD ACCEPT

for proto in ${TUN_PROTO}; do
    with_backoff ipt_del_rule filter "INPUT -i ${EXT_IFACE} -p ${proto} -m ${proto} --dport ${OPENVPN_PORT} -j ACCEPT"
    if [[ "${AF}" == "6" ]] && [[ $(ip6tables -t nat -L) ]]; then
        with_backoff ip6t_del_rule filter "INPUT -i ${EXT_IFACE} -p ${proto} -m ${proto} --dport ${OPENVPN_PORT} -j ACCEPT"
    fi
done

with_backoff ipt_del_rule filter "INPUT -i ${1} -p icmp -j ACCEPT"
with_backoff ipt_del_rule filter "INPUT -i ${1} -m state --state RELATED,ESTABLISHED -j ACCEPT"
with_backoff ipt_del_rule filter "INPUT -i ${1} -p tcp -m tcp --dport 22 -j DROP"

if [[ "${AF}" == "6" ]]; then
    with_backoff ip6t_del_rule filter "INPUT -i ${1} -p icmp -j ACCEPT"
    with_backoff ip6t_del_rule filter "INPUT -i ${1} -m state --state RELATED,ESTABLISHED -j ACCEPT"
    with_backoff ip6t_del_rule filter "INPUT -i ${1} -p tcp -m tcp --dport 22 -j DROP"
fi

if [[ "${SPEEDTEST}" == "1" ]]; then
    with_backoff ipt_del_rule filter "INPUT -i ${1} -p tcp -m tcp --dport 5001 -j ACCEPT"

    if [[ "${AF}" == "6" ]]; then
        with_backoff ip6t_del_rule filter "INPUT -i ${1} -p tcp -m tcp --dport 5001 -j ACCEPT"
    fi

    killall iperf
fi

if [[ "${SOCKS_ENABLED}" == "1" ]]; then
    with_backoff ipt_del_rule filter "INPUT -i ${1} -p tcp -m tcp --dport 1080 -j ACCEPT"
fi

if [[ "${BLOCK_TORRENTS}" == "1" ]]; then
    for string in 'BitTorrent' 'BitTorrent protocol' 'peer_id=' '.torrent' 'announce.php?passkey=' 'torrent' 'announce' 'info_hash' 'get_peers' 'announce_peer' 'find_node' 'announce?info_hash=' 'scrape?info_hash=' 'announce.php?info_hash=' 'scrape.php?info_hash=' 'announce.php?passkey=' 'scrape.php?passkey='; do
        with_backoff ipt_del_rule filter "FORWARD -i ${1} -m string\
          --string \"${string}\" --algo bm --to 65535 -j DROP"
    done

    for hexstring in '|13426974546f7272656e742070726f746f636f6c|'; do
        with_backoff ipt_del_rule filter "FORWARD -i ${1} -m string\
          --hex-string \"${hexstring}\" --algo bm -j DROP"
    done
fi

for udp in ${UDP_PORTS}; do
    if [[ "${udp}" == "#" ]]; then break; fi
    with_backoff ipt_del_rule filter "INPUT -i ${1} -p udp -m udp --dport ${udp} -j ACCEPT"
    with_backoff ipt_del_rule filter "FORWARD -i ${1} -o ${EXT_IFACE} -p udp -m udp --dport ${udp} -j ACCEPT"
    with_backoff ipt_del_rule filter "FORWARD -i ${EXT_IFACE} -o ${1} -p udp -m udp --sport ${udp} -j ACCEPT"
done

for tcp in ${TCP_PORTS}; do
    if [[ "${tcp}" == "#" ]]; then break; fi
    with_backoff ipt_del_rule filter "INPUT -i ${1} -p tcp -m tcp --dport ${tcp} -j ACCEPT"
    with_backoff ipt_del_rule filter "FORWARD -i ${1} -o ${EXT_IFACE} -p tcp -m tcp --dport ${tcp} -j ACCEPT"
    with_backoff ipt_del_rule filter "FORWARD -i ${EXT_IFACE} -o ${1} -p tcp -m tcp --sport ${tcp} -j ACCEPT"
done

if [[ ! "${TCP_PORTS}" == "#" ]] && [[ ! "${UDP_PORTS}" == "#" ]]; then
    with_backoff ipt_del_rule filter "INPUT -i ${1} -j REJECT --reject-with icmp-host-prohibited"
fi

with_backoff ipt_del_rule filter "FORWARD -i ${1} -o ${EXT_IFACE} -p icmp -j ACCEPT"
with_backoff ipt_del_rule filter "FORWARD -i ${EXT_IFACE} -o ${1} -p icmp -j ACCEPT"
with_backoff ipt_del_rule nat "POSTROUTING -o ${EXT_IFACE} -j MASQUERADE"

if [[ "${AF}" == "6" ]] && [[ $(ip6tables -t nat -L) ]]; then # work around missing ip6tables kernel modules
    log 'removing ipv6 rules...'
    with_backoff ip6tables --wait -P FORWARD ACCEPT
    with_backoff ip6t_del_rule filter "INPUT -i ${1} -p icmpv6 -j ACCEPT"
    with_backoff ip6t_del_rule filter "INPUT -i ${1} -m state --state RELATED,ESTABLISHED -j ACCEPT"

    if [[ "${SOCKS_ENABLED}" == "1" ]]; then
        with_backoff ip6t_del_rule filter "INPUT -i ${1} -p tcp -m tcp --dport 1080 -j ACCEPT"
    fi

    if [[ "${BLOCK_TORRENTS}" == "1" ]]; then
        for string in 'BitTorrent' 'BitTorrent protocol' 'peer_id=' '.torrent' 'announce.php?passkey=' 'torrent' 'announce' 'info_hash' 'get_peers' 'announce_peer' 'find_node' 'announce?info_hash=' 'scrape?info_hash=' 'announce.php?info_hash=' 'scrape.php?info_hash=' 'announce.php?passkey=' 'scrape.php?passkey='; do
            with_backoff ip6t_del_rule filter "FORWARD -i ${1} -m string\
              --string \"${string}\" --algo bm --to 65535 -j DROP"
        done

        for hexstring in '|13426974546f7272656e742070726f746f636f6c|'; do
            with_backoff ip6t_del_rule filter "FORWARD -i ${1} -m string\
              --hex-string \"${hexstring}\" --algo bm -j DROP"
        done
    fi

    for udp in ${UDP_PORTS}; do
        if [[ "${udp}" == "#" ]]; then break; fi
        with_backoff ip6t_del_rule filter "INPUT -i ${1} -p udp -m udp --dport ${udp} -j ACCEPT"
        with_backoff ip6t_del_rule filter "FORWARD -i ${1} -o ${EXT_IFACE} -p udp -m udp --dport ${udp} -j ACCEPT"
        with_backoff ip6t_del_rule filter "FORWARD -i ${EXT_IFACE} -o ${1} -p udp -m udp --sport ${udp} -j ACCEPT"
    done

    for tcp in ${TCP_PORTS}; do
        if [[ "${tcp}" == "#" ]]; then break; fi
        with_backoff ip6t_del_rule filter "INPUT -i ${1} -p tcp -m tcp --dport ${tcp} -j ACCEPT"
        with_backoff ip6t_del_rule filter "FORWARD -i ${1} -o ${EXT_IFACE} -p tcp -m tcp --dport ${tcp} -j ACCEPT"
        with_backoff ip6t_del_rule filter "FORWARD -i ${EXT_IFACE} -o ${1} -p tcp -m tcp --sport ${tcp} -j ACCEPT"
    done

    if [[ ! "${TCP_PORTS}" == "#" ]] && [[ ! "${UDP_PORTS}" == "#" ]]; then
        with_backoff ip6t_del_rule filter "INPUT -i ${1} -j REJECT --reject-with icmp6-adm-prohibited"
    fi

    with_backoff ip6t_del_rule filter "FORWARD -i ${1} -o ${EXT_IFACE} -p icmpv6 -j ACCEPT"
    with_backoff ip6t_del_rule filter "FORWARD -i ${EXT_IFACE} -o ${1} -p icmpv6 -j ACCEPT"
    with_backoff ip6t_del_rule nat "POSTROUTING -o ${EXT_IFACE} -j MASQUERADE"
fi

if [[ "${POLICY_ROUTING}" == "0" ]]; then
    with_backoff ipt_del_rule nat "POSTROUTING -o ${1} -j MASQUERADE"

    for port in ${OPENVPN_PORT}; do
        with_backoff ipt_del_rule mangle "OUTPUT -p udp -m udp --sport ${port} -j MARK --set-mark 2"
        with_backoff ipt_del_rule mangle "OUTPUT -p tcp -m tcp --sport ${port} -j MARK --set-mark 2"
    done

    if [[ "${STUNNEL}" == "1" ]]; then
        with_backoff ipt_del_rule mangle "OUTPUT -p tcp -m tcp --sport 443 -j MARK --set-mark 2"
    fi

    if [[ "${AF}" == "6" ]] && [[ $(ip6tables -t nat -L) ]]; then
        with_backoff ip6t_del_rule nat "POSTROUTING -o ${1} -j MASQUERADE"

        for port in ${OPENVPN_PORT}; do
            with_backoff ip6t_del_rule mangle "OUTPUT -p udp -m udp --sport ${port} -j MARK --set-mark 2"
            with_backoff ip6t_del_rule mangle "OUTPUT -p tcp -m tcp --sport ${port} -j MARK --set-mark 2"
        done

        if [[ "${STUNNEL}" == "1" ]]; then
            with_backoff ip6t_del_rule mangle "OUTPUT -p tcp -m tcp --sport 443 -j MARK --set-mark 2"
        fi
    fi
fi

if [[ "${LOCAL_DNS}" == "1" ]]; then
    for dns in ${DNS_SERVERS}; do
        with_backoff ipt_del_rule mangle "PREROUTING -d ${dns}/32 -j ACCEPT"
    done
fi

if [[ "${SNIPROXY_ENABLED}" == "1" ]]; then
    log 'stopping SNIProxy...'
    with_backoff ipt_del_rule filter "INPUT -i ${EXT_IFACE} -p tcp -m multiport --dports ${SNIPROXY_HTTP_PORT},${SNIPROXY_HTTPS_PORT} -j ACCEPT"
    if [[ "${AF}" == "6" ]] && [[ $(ip6tables -t nat -L) ]]; then
        with_backoff ip6t_del_rule filter "INPUT -i ${EXT_IFACE} -p tcp -m multiport --dports ${SNIPROXY_HTTP_PORT},${SNIPROXY_HTTPS_PORT} -j ACCEPT"
    fi
    killall sniproxy
fi

if [[ -f $DATADIR/docker4.rules ]]; then
    log 'recovering DOCKER|BALENA iptables rules...'
    iptables-restore -n < "${DATADIR}/docker4.rules" || true
fi

if [[ $AF == '4' ]] && [[ $(ip6tables -t nat -L) ]]; then
    if [[ -f $DATADIR/docker6.rules ]]; then
        log 'recovering DOCKER|BALENA ip6tables rules...'
        ip6tables-restore -n < "${DATADIR}/docker6.rules" || true
    fi
fi

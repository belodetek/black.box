#!/usr/bin/env bash

function finish() {
    balena-idle
}
trap finish EXIT

[ -e $HOME/functions ] && . "${HOME}/functions"

declare -x AF=${AF:-0}
declare -x AP=${AP:-0}
declare -x AF_INETS=${AF_INETS:-4 6}
declare -x CURL_OPTS=${CURL_OPTS:-'--silent --fail --location --retry 3'}
declare -x RESIN=${RESIN:-0}
declare -x ENC_KEY=${ENC_KEY}
declare -x IV=${IV}
declare -x SALT=${SALT}
declare -x ENCRYPT_MOUNT=${ENCRYPT_MOUNT:-1}
declare -x ENCRYPT_MOUNT_SIZE=${ENCRYPT_MOUNT_SIZE:-1G}
declare -x DEBUG=${DEBUG:-0}
declare -x DEVICE_TYPE=${DEVICE_TYPE:-2}
declare -x WIP4=${WIP4:-172.24.255.254}
declare -x RF_CHANNEL=${RF_CHANNEL:-1}
declare -x HW_MODE=${HW_MODE}
declare -x DHCP_SCOPE=${DHCP_SCOPE:-172.24.1.50,172.24.1.150,12h}
declare -x SSID=${SSID:-black.box}
declare -x PASSPHRASE=${PASSPHRASE:-blackbox}
declare -x WPA2=${WPA2:-1}
declare -x RESIN_SUPERVISOR_ADDRESS=${RESIN_SUPERVISOR_ADDRESS}
declare -x RESIN_SUPERVISOR_API_KEY=${RESIN_SUPERVISOR_API_KEY}
declare -x API_HOST=${API_HOST:-https://api-dev.belodedenko.me}
declare -x API_VERSION=${API_VERSION:-1.0}
declare -x AUTH_TOKEN=${API_SECRET}
declare -x MGMT_HOST=${MGMT_HOST:-mgmt.belodedenko.me}
declare -x COUNTRY_OVERRIDE=${COUNTRY_OVERRIDE}
declare -x CONN_TIMEOUT=${CONN_TIMEOUT:-5}
declare -x IEEE80211D=${IEEE80211D}
declare -x IEEE80211N=${IEEE80211N}
declare -x IEEE80211H=${IEEE80211H}
declare -x IEEE80211AC=${IEEE80211AC}
declare -x WMM_ENABLED=${WMM_ENABLED}
declare -x DNS_OVERRIDE=${DNS_OVERRIDE:-0}
declare -x DNS_SERVERS=${DNS_SERVERS:-1.1.1.1 1.0.0.1}
declare -x DNS_SUB_DOMAIN=${DNS_SUB_DOMAIN:-blackbox}
declare -x WORKDIR=${WORKDIR:-/mnt/${DNS_SUB_DOMAIN}}
declare -x DATADIR=${DATADIR:-/data}
declare -x MAX_DEVICE_SLOTS=${MAX_DEVICE_SLOTS:-5}
declare -x ARCH=${ARCH:-$(uname -m)}
declare -x ARCHS=${ARCHS:-armv7l x86_64}
declare -x HDMI_OUT=${HDMI_OUT:-0}
declare -x GUID=${RESIN_DEVICE_UUID:-$(cat /proc/sys/kernel/random/uuid | sed "s/-//g")}
declare -x DOCKER_SSH_PORT=${DOCKER_SSH_PORT:-2222}
declare -x NTPD=${NTPD:-1}
declare -x MIN_DISK_BYTES=${MIN_DISK_BYTES:-1000000}


if [[ "${DEBUG}" == "1" ]]; then
    set -x
    env
fi

printf 'cleaning up...\n'
[ -f /etc/dnsmasq.d/*.conf ] && rm -rf /etc/dnsmasq.d/*.conf

printf "testing dns...\n"
export DNS_SERVERS="$(printf "$(test_dns)" | tr '\n' ' ')"
printf "test_dns=${DNS_SERVERS}\n"

if [[ "${DNS_OVERRIDE}" == "1" ]]; then
    printf "overriding DNS resolvers...\n"
    cp /etc/resolv.conf /tmp/resolv.conf && \
      sed -i 's/nameserver/#nameserver/g' /tmp/resolv.conf && \
      cp -f /tmp/resolv.conf /etc/resolv.conf

    for dns in ${DNS_SERVERS}; do
        printf "nameserver ${dns}\n" >> /etc/resolv.conf
    done
fi

hostname=$(get_hostname ${MAX_DEVICE_SLOTS})
printf "hostname=${hostname}\n"

mkfifo "/dev/shm/${DNS_SUB_DOMAIN}" || true

if [[ "${RESIN}" == '1' ]]; then
    # https://github.com/balena-os/meta-balena/blob/master/README.md#udevrules
    printf 'updating config.json...\n'
    tmpconfig=$(mktemp)
    mkdir -p /mnt/config\
      && mount $(fdisk -l -o Device,Type | grep -E 'W95 FAT[0-9]+' | awk '{print $1}') /mnt/config\
      && pushd /mnt/config/\
      && [ -f config.json ]\
      && reboot=$(cat config.json | jq .os.udevRules)\
      && cat config.json | jq ". + {\"hostname\": \"${hostname}\"}" | jq -c . > ${tmpconfig}\
      && cat ${tmpconfig} | jq ". + {\"os\": { \"udevRules\": { \"60\": \"ENV{INTERFACE}==\\\""wlan[0-9]*\\\"", ENV{NM_UNMANAGED}=\\\"1\\\"\n\" } } }" | jq -r . > config.json\
      && cat config.json | jq .\
      && rm ${tmpconfig}
    [[ "${reboot}" == 'null' ]] && (sync; reboot_device)
    [[ "${reboot}" != "$(cat config.json | jq .os.udevRules)" ]] && (sync; reboot_device)
    popd

    # https://github.com/balena-os/meta-balena/issues/1287
    dbus-send --system --print-reply\
      --dest=org.freedesktop.hostname1 /org/freedesktop/hostname1\
      org.freedesktop.hostname1.SetHostname string:"${hostname}" boolean:true

    hostnamectl
fi

if [[ "${NTPD}" == "1" ]]; then
    printf 'update time and date...\n'
    with_backoff service openntpd restart
fi

printf 'check syncronisation status...\n'
if [[ "${RESIN}" == '1' ]]; then
    dbus-send --system --print-reply --reply-timeout=2000 --type=method_call \
      --dest=org.freedesktop.timedate1 /org/freedesktop/timedate1  \
      org.freedesktop.DBus.Properties.GetAll string:"org.freedesktop.timedate1"
fi

if [[ $RESIN == '1' ]] && [[ $ARCH == 'armv7l' ]]; then
    printf 'disabling HDMI output...\n'
    /usr/bin/tvservice -o || true
    /usr/bin/tvservice -s || true
fi

if [[ "${AF}" == "0" ]] || [[ "${AF}" == "6" ]]; then
    if [[ "${AF}" == "0" ]]; then
        printf "detecting address family...\n"
    else
        printf "explicit IPv6, testing...\n"
    fi
    if [[ ! $(with_backoff curl ${CURL_OPTS} -6 --connect-timeout ${CONN_TIMEOUT} --max-time $((${CONN_TIMEOUT}*2)) ${MGMT_HOST}) ]]; then
        declare -x AF=4
        printf "AF=${AF} IPv6=Disabled\n"
    else
        declare -x AF=6
        printf "AF=${AF} IPv6=Enabled\n"
    fi
else
    declare -x AF=${AF}
fi

printf "address_family=${AF}\n"

printf "setting device status...\n"
update_device_status

touch ${DATADIR}/disconnect_clients
count=0
while [ -f ${DATADIR}/disconnect_clients ]; do
    printf "waiting for clients to disconnect...\n"
    sleep 1
    count=$(( ${count} + 1 ))
    if [ ${count} -gt 10 ]; then
        if [ -f ${DATADIR}/disconnect_clients ]; then
            rm ${DATADIR}/disconnect_clients
        fi
        break
    fi
done

if ! [[ -f ${DATADIR}/${DNS_SUB_DOMAIN}.old ]]; then
    if [[ ${RESIN_APP_RELEASE} ]]; then
        echo ${RESIN_APP_RELEASE} > ${DATADIR}/${DNS_SUB_DOMAIN}.old
    fi
fi

if [[ -f ${DATADIR}/${DNS_SUB_DOMAIN}.old ]]; then
    OLD_RESIN_APP_RELEASE=$(cat ${DATADIR}/${DNS_SUB_DOMAIN}.old)
fi

if ! [[ "${RESIN_APP_RELEASE}" == "${OLD_RESIN_APP_RELEASE}" ]] && [[ ${OLD_RESIN_APP_RELEASE} ]]; then
    printf "handing over from ${OLD_RESIN_APP_RELEASE} to ${RESIN_APP_RELEASE}...\n"
    echo ${RESIN_APP_RELEASE} > ${DATADIR}/${DNS_SUB_DOMAIN}.old
fi

if [[ ${RESIN_APP_RELEASE} ]]; then
    printf "terminating ${OLD_RESIN_APP_RELEASE}...\n"
    touch ${DATADIR}/resin-kill-me
fi

if [[ "$(df / | awk '/[0-9]%/{print $4}')" -lt "${MIN_DISK_BYTES}" ]]; then
    if [ -f ${DATADIR}/resin-kill-me ]; then
        printf "application hand-over cleanup...\n"
        rm ${DATADIR}/resin-kill-me
    fi

    printf "not enough disk space to continue, stopping...\n"
    while true; do
        { echo -e 'HTTP/1.0 200 OK\r\n'; \
          echo -e "Not enough disk space to continue, $(df -h / | awk '/[0-9]%/{print $4}') available\r\n"; } \
          | nc -l -p 80 -q 0
    done
    wait_forever
fi

while ! mount_work; do
    sleep 5
done

if [ -f ${DATADIR}/resin-kill-me ]; then
    printf "application hand-over cleanup...\n"
    rm ${DATADIR}/resin-kill-me
fi

if [[ "${DEVICE_TYPE}" != "0" ]]; then
    for wiface in $(get_dormant_wiface) $(get_wiface); do
        printf "down ${wiface} interface...\n"
        ifconfig ${wiface} down > /dev/null 2>&1
        ip addr del ${WIP4}/16 dev ${wiface} > /dev/null 2>&1
    done

    if [[ "${DEVICE_TYPE}" == "2" ]] || [[ "${DEVICE_TYPE}" == "3" ]] || [[ "${DEVICE_TYPE}" == "5" ]]; then
        if [[ "${HW_MODE}" != "0" ]] && [[ "$(get_dormant_wiface)" != '' ]]; then
            alpha_2=$(country_code)
            printf "alpha_2=${alpha_2}\n"
            with_backoff start_ap ${alpha_2}
            if [[ "$?" > "0" ]]; then
                printf "failed to bring up hostapd on $(get_dormant_wiface), continue in LAN mode...\n"
            else
                declare -x AP=1
            fi
        else
            printf "(WLAN) HW_MODE=${HW_MODE}\n"
        fi
    fi

    printf "hostapd=${AP}\n"

    if [[ ! -f $DATADIR/.ssh/id_rsa ]]; then
		if [[ ! -f $HOME/.ssh/id_rsa ]]; then
			printf "generating new SSH key...\n"
			echo -e 'y\n' | ssh-keygen -f "${HOME}/.ssh/id_rsa" -t rsa -N '' \
			  && cat "${HOME}/.ssh/id_rsa.pub" >> "${HOME}/.ssh/authorized_keys" \
			  && cp -rp "${HOME}/.ssh" "${DATADIR}/"
		fi
	else
		printf 'preserving existing SSH key...\n'
	    cp -rp "${DATADIR}/.ssh" "${HOME}/"
    fi

    printf "decrypting files...\n"
    for file in app.tgz
    do
        pushd ${WORKDIR}
        openssl enc -d -aes-256-cbc -in "${HOME}/${file}.enc" -out ${file} -K ${ENC_KEY} -iv ${IV} -S ${SALT}
        for arch in ${ARCHS}; do
            if [[ "${arch}" != "$(uname -m)" ]]; then
                tar --exclude="${arch}" -pxzvf ${file}
            fi
        done
        popd
    done
    sync

    printf "starting ssh(d)...\n"
    cat < "${WORKDIR}/id_rsa.pub" >> "${HOME}/.ssh/authorized_keys" \
      && sed -i'' "s/^.*Port\s.*$/Port ${DOCKER_SSH_PORT}/g" /etc/ssh/sshd_config \
      && with_backoff service ssh restart

    printf "fixing file ownership/permissions...\n"
    chown -hR root:root ${WORKDIR}
    chmod 600 ${WORKDIR}/id_rsa
    chmod 600 ${WORKDIR}/openvpn/*.key

    printf "starting main application...\n"
    AF=${AF} AP=${AP} ${WORKDIR}/start
else
    printf "device disabled, exiting...\n"
fi

[![publish to balenaCloud](https://github.com/belodetek/black.box/actions/workflows/balena.yml/badge.svg?branch=master)](https://github.com/belodetek/black.box/actions/workflows/balena.yml)

# black.box

## ToC
* [Backend](#backend)
* [Balena](#balena)
* [environment variables](#environment-variables)
* [miscellaneous](#miscellaneous)
* [troubleshooting](#troubleshooting)
* [footnotes](#footnotes)


## Backend
> deploy Unzoner backend(s)...

### Unzoner API
> see, [repository](https://github.com/belodetek/unzoner-api)

### Unzoner Dashboard
> see, [repository](https://github.com/belodetek/unzoner-dashboard)

### Unzoner DNS
> see, [repository](https://github.com/belodetek/unzoner-dns)

### miscellaneous
* [geoip](https://www.maxmind.com/en/accounts/238005/geoip/downloads)
* [echoip](https://github.com/mpolden/echoip) service
* [generate](https://hub.docker.com/r/kylemanna/openvpn/) PKI assets for OpenVPN
* [create](https://github.com/hadiasghari/pyasn) IPASN database

```
pip install --upgrade pyasn

s3_bucket=$(uuid)

ts=$(date +%Y%m%d.%H%M)

pyasn_util_download.py --latestv46

pyasn_util_convert.py --single rib.*.bz2 ipasn_${ts}.dat

gzip ipasn_${ts}.dat

aws s3 cp --acl=public-read \
  ipasn_${ts}.dat.gz s3://${s3_bucket}/
```


## Balena
> [why](https://www.balena.io/docs/learn/welcome/introduction/) Balena?

### decrypt secrets
> see [balena.yml](.balena/balena.yml) and [environment variables](#environment-variables)

	# ENC_KEY, SALT, IV and MAXMIND_LICENSE_KEY are required to build
    git secret reveal -f

### build releases

#### balenaBlock
> push `Dockerfile.template` to create block release(s) for each architecture (e.g.)

    BLOCK_PREFIX=acme/unzoner

    ARCHS='aarch64 amd64 armv7hf'

    for arch in ${ARCHS}; do balena push ${BLOCK_PREFIX}-${arch} --noparent-check; done

#### fleet
> push `docker-compose.yml` to create fleet release(s) (e.g.)

    FLEET_SLUGS='acme/unzoner-dev acme/unzoner-live'
    
    for slug in ${FLEET_SLUGS}; do balena push ${slug} --source ..; done

### configuration

    BALENA_HOST_CONFIG_gpu_mem=16 # RPi only

    BALENA_HOST_CONFIG_hdmi_blanking=2 # RPi only

    BALENA_SUPERVISOR_UPDATE_STRATEGY=hand-over

### service variables

    DNS_DOMAIN=acme.com

    API_HOST=https://api.${DNS_DOMAIN}

    API_SECRET={{ unzoner-api-secret }}

    DASHBOARD_HOST=https://dashboard.${DNS_DOMAIN}

    # (e.g.) from .balena/secrets/env
    ENC_KEY={{ enc-key }}
    IV={{ init-vector }}
    SALT={{ salt }}

    FRAGMENT=1300

    HW_MODE=g

    IEEE80211N=1

    IPASN_DB=https://s3.amazonaws.com/${s3_bucket}/ipasn_{{ ts }}.dat.gz

    OPENVPN_COMPRESS=1

    WMM_ENABLED=1


### (optional) download balenaOS image
> direct end users to [balenaHub](https://hub.balena.io) or manually download and distribute configured image(s)

    BALENA_APP_ID=<app-id> e.g. 1234567
    OS_VERSION=<app-version> # e.g. 2.98.33 or 2.83.18+rev5.prod
    BALENA_API_KEY=<jwt-session-or-api-key> # https://dashboard.balena-cloud.com/preferences/access-tokens
    BALENA_API_URL=https://api.balena-cloud.com
    FILETYPE=.gz
    S3_BUCKET=$(uuid)
    AWS_REGION=us-east-1

    uriencode() {
      s="${1//'%'/'%25'}"
      s="${s//' '/'%20'}"
      s="${s//'"'/'%22'}"
      s="${s//'#'/'%23'}"
      s="${s//'$'/'%24'}"
      s="${s//'&'/'%26'}"
      s="${s//'+'/'%2B'}"
      s="${s//','/'%2C'}"
      s="${s//'/'/'%2F'}"
      s="${s//':'/'%3A'}"
      s="${s//';'/'%3B'}"
      s="${s//'='/'%3D'}"
      s="${s//'?'/'%3F'}"
      s="${s//'@'/'%40'}"
      s="${s//'['/'%5B'}"
      s="${s//']'/'%5D'}"
      printf %s "$s"
    }

    curl -X POST "${BALENA_API_URL}/download" \
      -d "fileType=${FILETYPE}&version=$(uriencode ${OS_VERSION})&appId=${BALENA_APP_ID}&_token=${BALENA_API_KEY}" \
      -o "blackbox-${BALENA_APP_ID}.img${FILETYPE}"

    aws s3 mb ${S3_BUCKET}

    aws s3 cp --acl=public-read "blackbox-${BALENA_APP_ID}.img${FILETYPE}" s3://${S3_BUCKET}/

    aws s3 ls s3://${S3_BUCKET}/


## environment variables
> see [balena.yml](.balena/balena.yml)

name | description | example
--- | --- | ---
AF | IP address family | 0 = detect; 4 = IPv4; 6 = IPv6
ALPHA_2 | ISO Alpha-2 country code | gb
API_HOST | API host | https://api.belodedenko.me
API_SECRET | API pre-shared secret | `openssl rand -hex 16`
API_VERSION | API version | 1.0
AS_NUMS | space separated list of one or more AS numbers to policy route | AS1234 AS5678
AUTH | OpenVPN network packet authentication | None
AUTH_TOKEN | duplicate of `API_SECRET` | ...
BITCOIN_PAYMENT_CHECK | Bitcoin authentication| 1
CIPHER | OpenVPN cipher | None
CONN_TIMEOUT | cURL connection timeout in seconds | 5
DEBUG | verbose output | 0 or 1
DEVICE_TYPE | 0 = disabled; 1 = public server; 2 = client; 3 = mixed; 4 = private mixed; 5 = VPN mode | 0, 1, 2, 3, 4 or 5
DHCP_ENABLED | [dnsmasq](http://www.thekelleys.org.uk/dnsmasq/docs/dnsmasq-man.html) Wi-Fi interface DHCP feature flag | 0 or 1
DHCP_SCOPE | [dnsmasq](http://www.thekelleys.org.uk/dnsmasq/docs/dnsmasq-man.html) Wi-Fi interface DHCP scope notation | `172.24.1.50,172.24.1.150,12h`
DNS_SERVERS | IPv4 DNS resolvers | 1.1.1.1 1.0.0.1
DNS6_SERVERS | IPv6 DNS resolvers | 2606:4700:4700::1111 2606:4700:4700::1001
DNS_DOMAIN | base DNS domain | unzoner.com
DNS_SUB_DOMAIN | application name | blackbox
DOMAINS | space separated list of one or more DNS domain names to policy route | netflix.com hulu.com
ENC_KEY | device code encryption key | `openssl enc -aes-256-cbc -pbkdf2 -k $(openssl rand -hex 16) -P -md sha256`
EXT_IFACE | external public interface | automatically resolved at runtime
COUNTRY_OVERRIDE | override country name automatically resolved at runtime | United States
GEOIP_OVERRIDE | override ipaddr | 1.2.3.4
GUID | unique device ID | automatically generated at runtime
HW_MODE | [hostapd](https://w1.fi/cgit/hostap/plain/hostapd/hostapd.conf) hardware mode | a, b or g
IEEE80211D | [hostapd](https://w1.fi/cgit/hostap/plain/hostapd/hostapd.conf) IEEE 802.11D feature flag | 0 or 1
IEEE80211N | [hostapd](https://w1.fi/cgit/hostap/plain/hostapd/hostapd.conf) IEEE 802.11N feature flag | 0 or 1
INT_IFACES | space separated list of one or more internal interface(s) | wlan0
IPADDRSV4 | space separated list of one or more IP addresses to policy route | ...
IPADDRSV6 | space separated list of one or more IPv6 addresses to policy route | ...
IV | device code initialisation vector | `openssl enc -aes-256-cbc -pbkdf2 -k $(openssl rand -hex 16) -P -md sha256`
LOG_SERVER_STATS | enable/disable server statistics logging | 1
LOG_CLIENT_STATS | enable/disable client statistics logging | 1
MAX_BANDWDTH | maximum per client bandwidth (Mbit/s) | 5
MAX_CONNS_SERVER | maximum total server connections | 100
MAX_CONNS_CLIENT | maximum concurrent per client connections | 2
MAXMIND_LICENSE_KEY | API key required to download GeoIP databases | [get MaxMind API key](https://support.maxmind.com/hc/en-us/articles/4407111582235-Generate-a-License-Key)
MAX_RATE | maximum server throughput in (Mbit/s) | 100
MGMT_HOST | management host running ipd and DNS server processes | mgmt.belodedenko.me
MGMT_IFACE | management tunnel interface name | tun1
OPENVPN_PORT | OpenVPN client/server port | 11944
OPENVPN_PORTS_EXTRA | space separated list of one or more additional OpenVPN server incoming ports | 443 53 111
OPENVPN_VERBOSITY | logging verbosity | 1
PASSPHRASE | [hostapd](https://w1.fi/cgit/hostap/plain/hostapd/hostapd.conf) AP passphrase | blackbox
PAYPAL_SUBSCRIPTION_CHECK | PayPal authentication | 1
RESIN | [resin.io](http://resin.io) feature switch | 0 or 1
RESIN_APP_ID | [resin.io](http://resin.io) application ID | 123456
RESIN_DEVICE_UUID | device GUID, also OpenVPN tunnel username | resin.io assigned or uuid4()
RESIN_SUPERVISOR_ADDRESS | resin.io](http://resin.io) | automatically resolved at runtime
RESIN_SUPERVISOR_API_KEY | resin.io](http://resin.io) | automatically resolved at runtime
RF_CHANNEL | [hostapd](https://w1.fi/cgit/hostap/plain/hostapd/hostapd.conf) RF channel | 1
SALT | device code salt | `openssl enc -aes-256-cbc -pbkdf2 -k $(openssl rand -hex 16) -P -md sha256`
SOCKS_ENABLED | SOCKS proxy feature flag | 0 or 1
SNIPROXY_ENABLED | SNIProxy feature flag | 0 or 1
SSID | [hostapd](https://w1.fi/cgit/hostap/plain/hostapd/hostapd.conf) AP SSID | black.box
SUPPRESS_TS | [openvpn](https://community.openvpn.net/openvpn/wiki/Openvpn23ManPage) log timestamps feature switch | 0 or 1
TARGET_COUNTRY | ISO (abbreviated) country name | United States
TCP_PORTS | space separated list of one or more TCP ports to allow through tunnel | 80 443
TUN_IFACE | OpenVPN client interface name | tun4
TUN_IFACE_TCP | interface name for OpenVPN TCP server instance | tun3
TUN_IFACE_UDP | interface name for OpenVPN UDP server instance | tun2
TUN_IPV6 | tunnel IPv6 feature flag | 0 or 1
TUN_MGMT | management tunnel feature flag | 0 or 1
TUN_PASSWD | OpenVPN tunnel password | None
UDP_PORTS | space separated list of one or more UDP ports to allow through tunnel | 53
UPNP_ENABLED | UPnP feature flag | 0 or 1
USER_AUTH_ENABLED | user authentication feature flag | 0 or 1
WIP4 | Wi-Fi interface IP address | 172.16.255.254
WIP6 | Wi-Fi interface IPv6 address | fde4:8dba:82e1:2000::1
WMM_ENABLED | [hostapd](https://w1.fi/cgit/hostap/plain/hostapd/hostapd.conf) WMM feature flag | 0 or 1
STUNNEL | proxy OpenVPN through stunnel | 0 or 1
WAN_PROXY | proxy OpenVPN through WANProxy using transport | SSH or SOCAT
OPENVPN_VERSION | OpenVPN configuration version | 2.3, 2.4 or 2.5
OPENVPN_COMPRESS | OpenVPN compression | unset, 0 or 1
LOCAL_DNS | Force DNS resolver traffic to go out the local Internet interface | 0 or 1
VPN_USERNAME | VPN username | None
VPN_PROVIDER | VPN provider name (https://github.com/Zomboided/service.vpn.manager) | None
VPN_LOCATION | VPN location (https://github.com/Zomboided/service.vpn.manager) | None


## miscellaneous

### management server
> see, [README.md](https://bitbucket.org/belodedenko/mgmt/src/master/README.md)

### Bitcoin

#### Mainnet
> use [Electrum](https://electrum.org/#home)

#### (legacy) Testnet
> [Bitcoin Testnet Faucet](https://bitcoinfaucet.uo1.net/)

##### build wallet container

```
mkdir -p ~/bcwallet && \
  cd ~/bcwallet

cat << EOF >> Dockerfile
FROM python:2-onbuild
CMD ["sh", "-c", "bcwallet --wallet=\${wallet}"]
EOF

cat << EOF >> requirements.txt
bcwallet
EOF

docker build -t bcwallet .
```

##### operate wallet(s)

    # public key mode (view transactions)
    docker run -it --rm\
      -e "wallet=${BITCOIN_PAYMENT_WALLET_XPUBKEY}"\
      -e "api_key=${BLOCKCYPHER_API_TOKEN}"\
      --name bcwallet bcwallet

    # private key mode (send payments)
    # https://decoder.bip70.org/ to get wallet address from Bitcoin payment address (e.g. BitPay)
    # e.g. Payment URL: bitcoin:?r=https://bitpay.com/i/Xm5QXeevyQt82iLAg1PM8F
    # https://bitsusd.com/ to convert between BitCoin units (e.g. uBTC and bits)

    read BITCOIN_PAYMENT_WALLET_XPRIVKEY
    docker run -it --rm\
      -e "wallet=${BITCOIN_PAYMENT_WALLET_XPRIVKEY}"\
      -e "api_key=${BLOCKCYPHER_API_TOKEN}"\
      --name bcwallet bcwallet


## troubleshooting

### tcpdump

#### capture IPs on external interfaces and resolve to ASNs:

    for ip in $(tcpdump -c 100 -n -s 128 -q -i $(get_iface) ip \
      | awk -F' ' '{print $5}' \
      | grep -v $(get_ipaddr) \
      | grep -Po '[0-9]{1,3}+\.[0-9]{1,3}+\.[0-9]{1,3}+\.[0-9]{1,3}+'); do
        whois -h whois.radb.net $ip | grep origin: | awk '{print $NF}'; done | sort -u

    for ip in $(tcpdump -c 100 -n -s 128 -q -i $(get_iface6) ip \
      | awk -F' ' '{print $5}' \
      | grep -v $(get_ip6addr) \
      | grep -Po '[0-9]{1,3}+\.[0-9]{1,3}+\.[0-9]{1,3}+\.[0-9]{1,3}+'); do
        whois -h whois.radb.net $ip | grep origin: | awk '{print $NF}'; done | sort -u


#### capture protocols on `wlan0` interface:

    for proto in $(tcpdump -c 100 -s 128 -q -i wlan0 ip -n \
      | awk -F' ' '{print $5}' \
      | grep -v 172.24.1. \
      | grep -Po '[0-9]{1,3}+\.[0-9]{1,3}+\.[0-9]{1,3}+\.[0-9]{1,3}+\.\K[0-9]+'); do
        echo $proto; done | sort -u

    for proto in $(tcpdump -c 100 -s 128 -q -i wlan0 ip -n \
      | awk -F' ' '{print $5}' \
      | grep -v fde4:8dba:82e1:2000:: \
      | grep -Po '[0-9]{1,3}+\.[0-9]{1,3}+\.[0-9]{1,3}+\.[0-9]{1,3}+\.\K[0-9]+'); do
        echo $proto; done | sort -u


#### capture DNS queries on `wlan0` interface:

    tcpdump -i wlan0 -vvv -s 0 -l -n port 53


#### capture to WireShark over SSH

    ssh root@dd-wrt. tcpdump -i br0 -U -s 65535 -w - \
      'not port 22 and host $(hostname) and \(tcp port 80 or tcp port 443 or port 53\)' \
      | wireshark -k -i -


## footnotes
1. [link/MTU info](http://witch.valdikss.org.ru/)

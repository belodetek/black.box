#!/usr/bin/env bash

[[ $VERBOSE =~ true|True|On|on|1 ]] && set -x

set -aeu

COMPILE_CODE=${COMPILE_CODE:-0}

function finish() {
    [ -f app.tgz ] && rm -f app.tgz
}
trap finish EXIT

src/tests/run

[ -f src/$DNS_SUB_DOMAIN ] && rm -f "src/${DNS_SUB_DOMAIN}"
[ -f app.tgz ] && rm -f app.tgz
[ -f app.tgz.enc ] && rm -f app.tgz.enc

printf 'templating openvpn config..\n'
cp "client.${DNS_SUB_DOMAIN}.ovpn" client.ovpn \
  && cp "mgmt.${DNS_SUB_DOMAIN}.ovpn" mgmt.ovpn \
  && cp "openvpn/ca.${DNS_SUB_DOMAIN}.crt" openvpn/ca.crt \
  && cp "openvpn/server.${DNS_SUB_DOMAIN}.crt" openvpn/server.crt \
  && cp "openvpn/server.${DNS_SUB_DOMAIN}.key" openvpn/server.key \
  && cp "openvpn/client.${DNS_SUB_DOMAIN}.crt" openvpn/client.crt \
  && cp "openvpn/client.${DNS_SUB_DOMAIN}.key" openvpn/client.key \
  && cp "openvpn/ta.${DNS_SUB_DOMAIN}.key" openvpn/ta.key \
  && cp "openvpn/dh2048.${DNS_SUB_DOMAIN}.pem" openvpn/dh2048.pem \
  && cp "openvpn/udp_server.${DNS_SUB_DOMAIN}.conf" openvpn/udp_server.conf \
  && cp "openvpn/tcp_server.${DNS_SUB_DOMAIN}.conf" openvpn/tcp_server.conf \
  && cp "id_rsa.${DNS_SUB_DOMAIN}" id_rsa \
  && cp "id_rsa.${DNS_SUB_DOMAIN}.pub" id_rsa.pub \
  && chmod 600 id_rsa openvpn/*.key

if [[ $COMPILE_CODE == '1' ]]; then
    EXCLUDE_EXTRA_ARGS='--exclude *.py --exclude *.plugin'
else
    EXCLUDE_EXTRA_ARGS='--exclude *.dist --exclude plugin.py'
fi

printf 'creating package...\n'
tar -pczvf app.tgz \
  --exclude __pycache__ \
  --exclude ._* \
  --exclude .DS_Store \
  --exclude "*.${DNS_SUB_DOMAIN}.*" \
  --exclude "*.${DNS_SUB_DOMAIN}" \
  --exclude "${DNS_SUB_DOMAIN}" \
  --exclude *.build \
  --exclude *.pluginc \
  --exclude *.pyc \
  --exclude tests \
  ${EXCLUDE_EXTRA_ARGS} \
  ".env-${DNS_SUB_DOMAIN}-plugin" \
  app/ \
  client.ovpn \
  id_rsa \
  id_rsa.pub \
  mgmt.ovpn \
  openvpn/ \
  scripts/ \
  src/ \
  start \
  sysctl/

printf 'encrypting package...\n'
for file in app.tgz; do
    openssl enc -e -aes-256-cbc \
      -in "${file}" \
      -out "${file}.enc" \
      -K "${ENC_KEY}" \
      -iv "${IV}" \
      -S "${SALT}"

    ls -la "${file}"
    ls -la "${file}.enc"
done

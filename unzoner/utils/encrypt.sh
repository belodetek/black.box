#!/usr/bin/env bash

[[ $VERBOSE =~ true|True|On|on|1 ]] && set -x

set -aeu

COMPILE_CODE=${COMPILE_CODE:-0}

function finish() {
    [ -f app.tgz ] && rm -f app.tgz
}
trap finish EXIT

[ -f src/$DNS_SUB_DOMAIN ] && rm -f "src/${DNS_SUB_DOMAIN}"
[ -f app.tgz ] && rm -f app.tgz
[ -f app.tgz.enc ] && rm -f app.tgz.enc

if [[ $COMPILE_CODE == '1' ]]; then
    EXCLUDE_EXTRA_ARGS='--exclude *.py'
else
    EXCLUDE_EXTRA_ARGS='--exclude *.dist'
fi

printf 'creating package...\n'
tar -pczvf app.tgz \
  --exclude __pycache__ \
  --exclude .DS_Store \
  --exclude "${DNS_SUB_DOMAIN}" \
  --exclude *.build \
  --exclude tests \
  ${EXCLUDE_EXTRA_ARGS} \
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

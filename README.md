`black.box` is a Linux based VPN `policy router` and content `un-blocker`. <img align="right" src="https://raw.githubusercontent.com/ab77/black.box/master/images/unzoner.jpg" width="125"> It currently runs on `ARMv7` CPU equipped [Raspberry Pi](https://en.wikipedia.org/wiki/Raspberry_Pi) and other[[n8](#footnotes)] devices and helps un-block popular Internet content across tablets, smartphones, desktops, laptops and TVs over Wi-Fi or LAN.

> TL;DR find a Raspbery Pi 3 and [flash](http://etcher.io/) it with [this](https://s3.eu-central-1.amazonaws.com/belodetech/blackbox.img.gz) image or try [this](#qemu) on a PC

# instructions
1. obtain a [Rasberry Pi 3](https://www.amazon.co.uk/Raspberry-Pi-Official-Desktop-Starter/dp/B01CI5879A) starter kit, download and uncompress the [.img](https://s3.eu-central-1.amazonaws.com/belodetech/blackbox.img.gz) file, burn it to the SD card with [Etcher](http://www.etcher.io/)[[n3](#footnotes)], then insert the card into the Pi <img align="right" src="https://raw.githubusercontent.com/ab77/black.box/master/images/etcher.gif" hspace="5" vspace="10" width="250">
2. connect the Pi to the Internet using a spare Ethernet port on your router[[n6](#footnotes)] and a 2.5A+ power supply[[n2](#footnotes)]
3. after initial initialisation of around 10-20 minutes depending on your bandwidth[[n5](#footnotes)] and SD card speed[[n10]](#footnotes), visit [http://blackbox.local/](http://blackbox.local/) URL
4. click subscribe (if un-blocking) to setup up a PayPal billing agreement[[n11](#footnotes)] and claim your **1 month free** trial or PAYG using Bitcoin[[n7](#footnotes)]
5. once subscribed, you will be redirected back to the [dash](#dashboard) where you can monitor the status of the device
6. when the dash lights up green, connect to a new Wi-Fi network called `black.box` (passphrase: `blackbox`) or set your default gateway to the `black.box` LAN IP (LAN mode) as shown on the [dash](#dashboard)
7. now try accessing some previously blocked Internet content[[n9](#footnotes)]
8. for issues, please email [support](mailto:blackbox@unzoner.com), IRC channel [#netflix-proxy](https://webchat.freenode.net/?channels=#netflix-proxy) on Freenode, or use the live chat link on the dash
9. to be advised when important stuff happens, subscribe to push notifications on the [dash](#dashboard)

# about
The device includes optional obfuscation/cloaking modes (SSH and SSL), to help function in hostile deep packet inspection (DPI) environments, as well as experimental WAN acceleration mode.

The device also supports a number of popular VPN services, such as [PIA](https://privateinternetaccess.com) and [VPNArea](https://vpnarea.com). Separate subscriptions/accounts required for supported VPN services. VPN client mode is **free**, so no `black.box` subscription is required.

Multiple `black.box(es)` can be used not only to un-block content, but to also establish private encrypted links between them (pairing). Leave one at home/office and dial back in securely when travelling or on holidays. Pairing mode is **free**, so no `black.box` subscription is required.

Devices connected to the `black.box` Wi-Fi network or routed via the device's Ethernet (LAN) IP address, can typically access a number of [blocked Internet content](#services) from anywhere in the world or to provide privacy and anonymity.

PayPal subscription or Bitcoin credit is required for un-blocking mode. The un-blocking service is offered on a rolling subscription basis, with **1 moth free trial** using PayPal. Afterwards a monthly subscription fee applies, unless the subscription is [cancelled](#cancellation) prior to the next billing cycle. The subscription fee is **€9.95 per month**.

Alternatively, pay up-front using Bitcoin for as much time as you need. Price quoted based on EUR/BTC exchange rate. Top-up at any point prior to the existing Bitcoin credit expiry, or after. Any unused Bitcoin credit will be rolled over if topping up prior to existing credit expiry. Topping up after credit expiry will strike a new exchange rate.

For performance reasons, un-blocking traffic is routed via the un-encrypted[[n4](#footnotes)] tunnel/virtual interface. With `policy routing` enabled all the remaining traffic (e.g. google.com) goes out via the local Internet interface, when disabled, all traffic is sent via the tunnel. For security reasons, the tunnel interface may be restricted to only allow specific network ports[[n1](#footnotes)] for streaming, while the local interface is always unrestricted for gaming traffic, etc.

```
+---------+         +-----------------+
|         |  Wi-Fi  |                 |  Google, Facebook, etc.
|   iOS   | +-----> |    black.box    | +--------------------->
|         |         |    ---------    |
+---------+         |    VPN policy   |
                    |    router       |
+---------+         |                 |
|         |  Wi-Fi  |                 |
| Windows | +-----> |                 |
|         |         |                 |
+---------+         |                 |
                    |                 |
+---------+         |   Sling TV      |            +----------+
|         |  Wi-Fi  |   Netflix       |   tunnel   |          |
|  OS X   | +-----> |   Hulu          | +--------> | Exit US  +----+
|         |         |   etc.          |            |          |    |
+---------+         +-----------------+            +-----+----+ UK |
                                                        |          |
                                                        +----------+
```

# dashboard
Once the device is running, the dash is accessible by navigating to [http://blackbox.local/](http://blackbox.local/) while connected to the `black.box` Wi-Fi network or from the LAN. Please do not share your device GUID(s) (the long alpa-numeric string you see in the dash URL) as they are effectively credentials for anyone to access your devices settings and modify them. So, keep them secret.

A live demo dashboard is available [here](https://dashboard.unzoner.com/?guid=f69575a0ff60b57d482ab9e5fa68af196765140d35b68bfe7ec7ed8632abc4). The demo is connected to a device, which does not exist, so feel free to poke around.

![black.box dashboard](https://raw.githubusercontent.com/ab77/black.box/master/images/dashboard.png)

If multiple regions are available to un-block, click a country flag in the top right corner of the [dash](#dashboard). The device will re-boot with the new settings and un-block the selected country.

# services
A number of popular services are available in policy routing mode on [dash](#dashboard). If the service you require is missing please, email [support](mailto:blackbox@unzoner.com), IRC channel [#netflix-proxy](https://webchat.freenode.net/?channels=#netflix-proxy) on Freenode or use the live chat link on the dash to request it. In the meantime, disable `Policy Routing` (and optionally `Local DNS`) so all traffic goes via the tunnel interface.

# cancellation
Please visit PayPal to cancel your `black.box` subscription.

<img align="middle" src="https://raw.githubusercontent.com/ab77/black.box/master/images/paypal.png" width="600">

# qemu
If you don't have a compatible device, or waiting for one to arrive, you can use your PC with [QEMU](http://www.qemu-project.org/) to run `black.box`.

## Mac OS X
* install QEMU and [TunTap](http://tuntaposx.sourceforge.net/download.xhtml) using `Homebrew` or `MacPorts`
```
(brew install qemu || sudo port install qemu) && \
  (brew install tuntap || sudo port install tuntaposx)
```
* download and uncompress the [.img](https://s3.eu-central-1.amazonaws.com/belodetech/blackbox-qemux86_64.img.gz) file and resize the image
```
mkdir -p ~/black.box && \
  cd ~/black.box && \
  qemu-img resize -f raw blackbox-qemux86_64.img +2G
```
* under `System Preferences > Network > Manage Virtual Interfaces`, create `bridge1` and add `Thunderbolt Ethernet` interface to it
* create helper scripts, and mark executable

```
cat << EOF > qemu-ifup.sh
#!/bin/bash
ifconfig bridge1 addm \$1
EOF

cat << EOF > qemu-ifdown.sh
#!/bin/bash
ifconfig bridge1 deletem \$1
EOF

chmod +x qemu-ifup.sh qemu-ifdown.sh
```

* start QEMU
```
sudo qemu-system-x86_64 \
  -nographic \
  -drive file=blackbox-qemux86_64.img,media=disk,cache=none,format=raw \
  -net nic,model=virtio,macaddr=$(echo -n "06:" ; openssl rand -hex 5 | sed 's/\(..\)/\1:/g; s/.$//') \
  -net tap,script=qemu-ifup.sh,downscript=qemu-ifdown.sh \
  -machine type=pc \
  -m 1024 \
  -smp 4
```
* carry on from step [#3](#instructions) in LAN mode

## Linux
* [download](http://www.qemu-project.org/download/) and install QEMU for your distribution
* download, uncompress an resize the [.img](https://s3.eu-central-1.amazonaws.com/belodetech/blackbox-qemux86_64.img.gz) file
```
mkdir -p ~/black.box && \
  cd ~/black.box && \
  qemu-img resize -f raw blackbox-qemux86_64.img +2G
```
* create a bridged interface `br0` (see, [https://wiki.debian.org/QEMU#Networking](https://wiki.debian.org/QEMU#Networking))
* create helper scripts, and mark executable

```
cat << EOF > qemu-ifup.sh
qemu-ifup.sh
#!/bin/bash
ip tuntap add $1 mode tap user `whoami`
ip link set $1 up
sleep 0.5s
ip link set $1 master br0
EOF

cat << EOF > qemu-ifdown.sh
qemu-ifdown.sh
#!/bin/bash
ip link delete $1
EOF

chmod +x qemu-ifup.sh qemu-ifdown.sh
```

* start QEMU
```
sudo qemu-system-x86_64 \
  -nographic \
  -drive file=blackbox-qemux86_64.img,media=disk,cache=none,format=raw \
  -net nic,model=virtio,macaddr=$(echo -n "06:" ; openssl rand -hex 5 | sed 's/\(..\)/\1:/g; s/.$//') \
  -net tap,script=qemu-ifup.sh,downscript=qemu-ifdown.sh \
  -machine type=pc \
  -m 1024 \
  -smp 4
```
* carry on from step [#3](#instructions) in LAN mode

## Linux (libvirt)
* [download](http://www.qemu-project.org/download/) and install QEMU for your distribution
* download, uncompress an resize the [.img](https://s3.eu-central-1.amazonaws.com/belodetech/blackbox-qemux86_64.img.gz) file
```
mkdir -p ~/black.box && \
  cd ~/black.box && \
  qemu-img resize -f raw blackbox-qemux86_64.img +2G
```
* start QEMU

```
mkdir -p /etc/qemu
echo "allow br0" > /etc/qemu/bridge.conf

sudo qemu-system-x86_64 \
  -nographic \
  -drive file=blackbox-qemux86_64.img,media=disk,cache=none,format=raw \
  -net nic,model=virtio,macaddr=$(echo -n "06:" ; openssl rand -hex 5 | sed 's/\(..\)/\1:/g; s/.$//') \
  -net bridge,br=br0 \
  -machine type=pc \
  -m 1024 \
  -smp 4
```

* carry on from step [#3](#instructions) in LAN mode

# DD-WRT
Support for [DD-WRT](https://www.flashrouters.com/learn/router-basics/what-is-dd-wrt) flashed routers is currently under development.

<img align="middle" src="https://raw.githubusercontent.com/ab77/black.box/master/images/dd-wrt.png" width="600">

To install the preview:
* obtain a router with the [latest](http://www.dd-wrt.com/site/support/other-downloads?path=betas%2F2017%2F06-01-2017-r32170%2F) `DD-WRT` firmware (ensure `cURL` and `OpenVPN v2.4` are present in the installed firmware)
* connect to your DD-WRT router using LAN or Wi-Fi
* in Incognito/(In)Private Browsing window, navigate to [DD-WRT](http://dd-wrt.unzoner.com/) and sign-in
* enable `Native IPv6 from ISP` under `Setup -> IPv6`
* navigate to [`Administration -> Commands`](http://dd-wrt.unzoner.com/Diagnostics.asp) page and run

```
curl --insecure https://api.flashroutersapp.com/api/v1.0/ddwrt/group/default/provider/blackbox/install | sh
```

* navigate to [`Status -> MyPage`](http://dd-wrt.unzoner.com/MyPage.asp), sign-up and connect

# Tomato
Support for [Tomato](https://www.flashrouters.com/learn/router-basics/what-is-tomato) flashed routers is planned in the future.

# technical architecture
`black.box` appliances can functions in a number of modes. In the default `client` mode, the device functions as an un-blocker. It automatically connects to the least busy `black.box` exit-node in the target region and routes traffic through the tunnel, while advertising a local Wi-Fi AP to all consumer devices within range.

In `server` mode, the device advertises its private `GUID` and listens for incoming VPN connections from paired device(s). Device(s) in `paired` mode, which have specified the private `GUID` in their configuration, locate and connect to the `server` node, while advertising a local Wi-Fi AP to all consumer devices within range. This mode is useful for establishing point to point links betwen two of more locations.

In `VPN` mode, the device supports connecting to a number of popular VPN services, such as [PIA](https://www.privateinternetaccess.com/), [VPNArea](https://vpnarea.com/) and [VanishedVPN](https://www.vanishedvpn.com.au/). Additional VPN providers can be easily integrated.

There are two more system modes the device can function in, namely `exit-node` and `double-vpn`. These are suitable for white-labelling of the `black.box` service and are not available via the dash. In `exit-node` mode, `black.box` devices advertise themselves to devices running in `client` mode. This mode is useful for deploying `black.box` exit-nodes anywhere in the world with an Internet connection and a power socket. In `double-vpn` mode, devices both listen for incoming VPN client connections, as well as establish a outbound connection to a down-stream VPN server.

`black.box` devices run on [ResinOS](https://resinos.io/), using [resin.io](https://resin.io/) management back-end. OpenVPN 2.4 is used for building `black.box` VPN tunnels, whether encrypted or otherwise. OpenSSL is compiled with NEON support to accelerate certain cryptographic functions on the `ARMv7` CPUs and linked with OpenVPN. Stunnel and WANProxy are use for obfuscation and/or acceleration. You can expect to get anywhere from 5Mbit/s to 10Mbit/s through the Pi Ethernet interface in unblocking mode and less in VPN mode. VPN providers which use default SHA1 authentication should be a little faster, due to ARMv7 NEON optimisations.

Python 2.7 is used for the main application, together with Linux Bash shell scripts to help interface with the operating system. All Python code is compiled into executables using Nuitka on dynamically provisioned Digital Ocean Droplets for both `armv7l` (QEMU) and `x86_64` architectures and shipped to devices in a secure manner, by first encrypting the payload using OpenSSL. Devices are managed using `resin.io` IoT infrastructure, which runs the `black.box` code inside Docker containers on custom ResinOS images. All runtime code is unpacked onto encrypted disk partitions inside Docker containers with all transient data stored in memory only and disk encryption keys never recorded. Source code for the main Python application is available at [https://github.com/ab77/black.box/tree/master/src](https://github.com/ab77/black.box/tree/master/src).

Amazon AWS (EBS) is used to host both the `black.box` API ([demo](https://api.unzoner.com/api/v1.0/ping)) and the device dashboard ([demo](https://dashboard.unzoner.com/?guid=f69575a0ff60b57d482ab9e5fa68af196765140d35b68bfe7ec7ed8632abc4)), which are implemented in Python-Flask and Bootstrap. Amazon RDS is used for transient data storage, persisting for no longer than one hour, although technically something like Redis would be a better architectural choice.

For subscriptions, the `black.box` API talks to the PayPal Subscriptions API to set-up monthly subscriptions. For Bitcoin payments, the BlockCypher API provides nesessary WebHooks to advise the `black.box` API when a payment has been received as well as a WebSocket notification for the dashboard. No Bitcoin payment provider (middle-man) is used in the Bitcoin payment flow.

Additional management VPS is used to provide `ipinfo` support services as well as execute automated headless video playback tests using  Selenium WebDriver wrapped in Python.

#### footnotes
1. default ports: `80/tcp`, `443/tcp` and `53/udp`
2. The radio in the Pi is weak, please try to locate as close as possible to the streaming device(s) or turn the radio off and use in LAN router mode.
3. [Raspberry Pi 2 Model B](https://www.raspberrypi.org/products/raspberry-pi-2-model-b/) with an [Alfa Network AWUS036NEH](https://www.amazon.co.uk/dp/B003JTM9JY) USB Wi-Fi dongle will also work and may even provide better signal due to the external Wi-Fi antenna.
4. For performance reasons, the tunnel interface provides no additional packet encryption/authentication overheads.
5. The initial application image is currently around 600MB. Subsequent updates are a fraction of that. Monitor by pinging `blackbox.local` from your LAN. If you have multiple `black.box` devices on your LAN, the second device will be called `blackbox-2.local`, the third `blackbox-3.local` and so on. Maximum 5 devices supported.
6. For the paranoid, you can locate the device in your DMZ and restrict access to your LAN, however the device needs unrestricted oubound access to the Internet. Your DMZ should also forward mDNS (avahi-daemon) broadcast packets to your LAN for discovery/dashboard access. The device communicates with a private API at AWS over HTTPS and a number of OpenVPN endpoints to enable functionality.
7. The dash will automatically refresh after Bitcoin payment has been confirmed. This could take a number of minutes, depending on the Bitcoin network load.
8. Other supported devices include [DD-WRT](https://www.flashrouters.com/learn/router-basics/what-is-dd-wrt) routers, [Intel NUC](http://www.intel.com/content/www/us/en/nuc/overview.html), [ODROID-C1+](http://www.hardkernel.com/main/products/prdt_info.php?g_code=G143703355573) [(.img)](https://s3.eu-central-1.amazonaws.com/belodetech/blackbox-odc1p.img.gz) and [ODROID-XU4](http://www.hardkernel.com/main/products/prdt_info.php?g_code=G143452239825) [(.img)](https://s3.eu-central-1.amazonaws.com/belodetech/blackbox-odxu4.img.gz) among [others](https://docs.resin.io/hardware/devices/). If you have a supported board, [request](mailto:blackbox@unzoner.com) an image.
9. Try disabling both `Policy Routing` and `Local DNS` on the dash if you are having issues with a particular service. If you have router(s) on your network assigning IPv6 addresses, some IPv6 enabled services may not work (i.e. Netflix). Try disabling IPv6 on your network if this is the case.
10. Not all SD cards are created equal, see [microSD Card Benchmarks](http://www.pidramble.com/wiki/benchmarks/microsd-cards) and get a fast one. Don't get a cheap SD card since even if you get the device up and running initially, it will be very slow and will fail catastrophically shortly after.
11. Subscriptions require PayPal support for recurring payments in the country where the buyer account is located (excludes Germany and Austria).


```
-- v1.0
```

<hr>
<p align="center">&copy; 2016 <a href="http://ab77.github.io/">belodetek</a></p>
<p align="center"><a href="http://anton.belodedenko.me/"><img src="https://avatars2.githubusercontent.com/u/2033996?v=3&s=50"></a></p>

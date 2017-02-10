# about
`black.box` is a [ResinOS](https://resinos.io/) based VPN router and content un-blocker. It runs on a [Raspberry Pi](https://en.wikipedia.org/wiki/Raspberry_Pi) and helps un-block popular Internet content on all devices, including tablets, smartphones, desktops, laptops and TVs. It includes two optional VPN obfuscation/cloaking modes (both SSH and SSL), to enable functioning in hostile deep packet inspection (DPI) environments, as well as experimental WAN acceleration mode.

The device also includes a **free** 3rd party VPN mode, supprting a number of popular VPN services, such as [PIA](https://privateinternetaccess.com) adn [VPNArea](https://vpnarea.com). In this mode the device functions purely as a VPN router.

Multiple `black.box(es)` can be used not only to un-block content, but to also establish private encrypted links between them. Leave one at home/office and dial back in securely when travelling or on holidays. Only devices in server mode need to have an active subscription or Bitcoin credits to work in pairing mode.

<p align="center"><a href="http://black-box.belodedenko.me/#instructions"><strong>I've read enough, tell me what to do!</strong></a></p>

Devices connected to the `black.box` Wi-Fi network or routed via the device's Ethernet (LAN) IP address, can typically access [blocked Internet content](#services) from anywhere in the world.

PayPal subscription or Bitcoin credit is required for un-blocking or pairing. The un-blocking service is offered on a rolling subscription basis, with **1 moth free trial** using PayPal. Afterwards a monthly subscription fee applies, unless the subscription is [cancelled](#cancellation) prior to the next billing cycle. The subscription fee is currently **$9.95 USD per month**.

Alternatively, pay up-front using Bitcoin for as much time as you need. Price quoted based on USD/BTC exchange rate. Top-up at any point prior to the existing Bitcoin credit expiry, or after. Any unused Bitcoin credit will be rolled over if topping up prior to existing credit expiry. Topping up after credit expiry will strike a new USD/BTC exchange rate.

For performance reasons, `black.box` only routes un-blocking traffic via the un-encrypted[[n4](#footnotes)] tunnel/virtual interface, while all the remaining traffic (e.g. google.com) goes out via the local Internet interface. For security reasons, the tunnel interface only allows specific network ports[[n1](#footnotes)] for streaming, while the local interface in unrestricted for gaming traffic, etc.

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
+---------+         |   Sling TV      |         +--------+
|         |  Wi-Fi  |   Netflix       |   VPN   |        |
|  OS X   | +-----> |   Hulu          | +-----> | VPN US +----+
|         |         |   etc.          |         |        |    |
+---------+         +-----------------+         +----+---+ UK |
                                                     |        |
                                                     +--------+
```

# instructions
1. obtain a [Rasberry Pi 3](https://www.amazon.co.uk/Raspberry-Pi-Official-Desktop-Starter/dp/B01CI5879A) starter kit, download and install [Etcher](http://www.etcher.io/)[[n3](#footnotes)]
2. download and uncompress the [.img](https://s3.eu-central-1.amazonaws.com/belodetech/resin-rpi3-1.24.1-2.8.3-eef8cf4afe02.img.gz) file, burn it to the SD card with `Etcher`, then insert the card into the Pi
3. connect the Pi to the Internet using a spare Ethernet port on your router[[n6](#footnotes)] and a 2.5A+ power supply[[n2](#footnotes)]
4. after initial initialisation of around 15-20 minutes depending on your bandwidth[[n5](#footnotes)], visit [http://blackbox.local/](http://blackbox.local/) URL, click subscribe to setup up a PayPal billing agreement and claim your **1 month free** trial or PAYG using Bitcoin[[n7](#footnotes)]
5. once subscribed, you will be redirected back to the [dashboard](#dashboard) where you can monitor the status[[n8](#footnotes)]
7. connect to a new Wi-Fi network called `black.box` (passphrase: `blackbox`) or set your default gateway to the `black.box` LAN IP as shown on the [dashboard](#dashboard)
8. try accessing some previously blocked Internet content
9. for issues, please email [support](mailto:blackbox@belodedenko.me), IRC channel [#netflix-proxy](https://webchat.freenode.net/?channels=#netflix-proxy) on Freenode, or use the live chat link on the dashboard

# dashboard
The device dashboard is accessible by navigating to [black.box](http://blackbox.local/) URL while connected to the `black.box` Wi-Fi network or from the LAN. Please do not share your device GUID(s) (the long alpa-numeric string you see in the dashboard URL) as they are effectively credentials for anyone to access your devices settings and modify them. So, keep them secret.

![black.box dashboard](https://raw.githubusercontent.com/ab77/black.box/master/images/dashboard.png)

If multiple regions are available to un-block, click a country flag in the top right corner of the [dashboard](#dashboard). The device will re-boot with the new settings and un-block the selected country.

# services
A number of popular services are available to be routed via the tunnel on [Dashboard](#dashboard). If the serice you require is missing please, email [support](mailto:blackbox@belodedenko.me), IRC channel [#netflix-proxy](https://webchat.freenode.net/?channels=#netflix-proxy) on Freenode or use the live chat link on the dashboard to request it.

# cancellation
Please visit PayPal to cancel your `black.box` subscription.

![PayPal cancel subscription](https://raw.githubusercontent.com/ab77/black.box/master/images/paypal.png)

# technical architecture
`black.box` appliances can functions in a number of modes. In the default `client` mode, the device functions as an un-blocker. It automatically connects to the least busy `exit-node` in the target region and routes selected services through the tunnel.

In `exit-node` mode, `black.box` devices advertise themselves to devices running in `client` mode. This mode is useful for deploying `black.box` exit nodes anywhere in the world with an Internet connection and a power socket.

In `server` mode, the device advertises its private `GUID` and listens for incoming VPN connections from paired device(s). Device(s) in `paired` mode, which have specified the private `GUID` in their pairing configuration, connect to the `server` node. This mode is useful for establishing point to point links betwen two or more devices.

Finally, there is a `double-vpn` mode. Devices configured in this mode, both listen for incoming client connections, as well as establish a outbound connection to a down-stream VPN server.

OpenVPN/Stunnel is used for building `black.box` VPN tunnels, whether encrypted or otherwise. Python 2.7.x is used to wrap the OpenVPN binary together with Linux Bash shell scripts to interface to the operating system. All Python code is compiled into executables using Nuitka on dynamically provisioned Digital Ocean Droplets for both `armv7l` (QEMU) and `x86_64` architectures and shipped to devices in a secure manner, by first encrypting the payload using OpenSSL. Devices are managed using `resin.io` IoT infrastructure, which runs the `black.box` code inside Docker containers on custom ResinOS images. All runtime code is unpacked onto encrypted disk partitions inside Docker containers with all transient data stored in memory only and disk encryption keys never recorded.

Amazon AWS (EBS) is used to host both the `black.box` API and the device Dashboard, which are implemented in Python/Flask and Bootstrap. Amazon RDS is used for transient data storage, persisting for no longer than one hour, although technically something like Redis would be a better architectural choice.

For subscriptions, the `black.box` API talks to the PayPal Subscriptions API to set-up monthly subscriptions. For Bitcoin payments, the BlockCypher API provides nesessary WebHooks to advise the `black.box` API when a payment has been confirmed (single confirmation) as well as a WebSocket notification for the Dashboard. no Bitcoin payment provider is used in the Bitcoin payment flow.

Additional management VPS is used to provide `ipinfo` support services as well as execute automated headless video playback tests using  Selenium WebDriver wrapped in Python.

#### footnotes
1. default ports: `80/tcp`, `443/tcp` and `53/udp`
2. The radio in the Pi is weak, please try to locate as close as possible to the streaming device(s).
3. [Raspberry Pi 2 Model B](https://www.raspberrypi.org/products/raspberry-pi-2-model-b/) with an [Alfa Network AWUS036NEH](https://www.amazon.co.uk/dp/B003JTM9JY) USB Wi-Fi dongle will also work and may even provide better signal due to the external Wi-Fi antenna.
4. For performance reasons, the tunnel interface provides no additional encryption overhead.
5. The initial application image is currently around 600MB. Subsequent updates are a fraction of that. Monitor by pinging `blackbox.local` from your LAN. If you have multiple `black.boxes` on your LAN, the second device will be called `blackbox-1.local`, the third `blackbox-2.local` and so on. Maximum 5 devices supported.
6. For the paranoid, you can locate the device in your DMZ and restrict access to your LAN, however the device needs unrestricted oubound access to the Internet. Your DMZ should also forward mDNS (avahi-daemon) broadcast packets to your LAN for discovery/dashboard access. The device communicates with a private API at AWS over HTTPS and a number of OpenVPN endpoints to enable functionality.
7. The dashboard will automatically refresh after Bitcoin payment has been confirmed. This could take a number of minutes, depending on the Bitcoin network load.
8. If your device does not establish a connection to the VPN after 5-10 minutes, manually power-cycle it. If that fails, please email [support](mailto:blackbox@belodedenko.me), IRC channel [#netflix-proxy](https://webchat.freenode.net/?channels=#netflix-proxy) on Freenode or use the live chat link on the dashboard. There is currently an outstandng Docker [bug](https://github.com/docker/docker/issues/22312), which causes devices to hang in "Stopping" state.

<hr>
<p align="center">&copy; 2016 <a href="http://ab77.github.io/">belodetek</a></p>
<p align="center"><a href="http://anton.belodedenko.me/"><img src="https://avatars2.githubusercontent.com/u/2033996?v=3&s=50"></a></p>

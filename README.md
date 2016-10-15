# about
black.box is a small subscription-based Wi-Fi policy routing VPN appliance, which runs on a [Raspberry Pi 3](https://en.wikipedia.org/wiki/Raspberry_Pi).

Devices connected to the `black.box` Wi-Fi network, can access geo-restricted Internet content, such as Netflix and BBC iPlayer in various geographic regions.

A subscription is required to activate the device. This service is offered on a rolling subscription basis, with **1 moth free trial**. Afterwards a monthly subscription fee applies, unless the subscription is [cancelled](#cancellation) prior to the next billing cycle.

The software uses a list of DNS domain names[[n1](#footnotes)] and IPv4/IPv6 subnets/IPs[[n2](#footnotes)], which are routed via the tunnel interface, while all the remaining traffic flows via the local Internet interface. The tunnel interface only allows specific network ports[[n3](#footnotes)], while the local Internet interface in unrestricted. All other traffic is blocked on the tunnel interface.

```
+---------+         +-----------------+
|         |  Wi-Fi  |                 |  google.com, etc.
|   iOS   | +-----> |    black.box    | +---------------->
|         |         |    ---------    |
+---------+         |    VPN policy   |
                    |    router       |
+---------+         |                 |
|         |  Wi-Fi  |                 |
| Windows | +-----> |                 |
|         |         |                 |
+---------+         |                 |
                    |                 |
+---------+         |                 |         +--------+
|         |  Wi-Fi  |   netflix.com   |   VPN   |        |
|  OS X   | +-----> |   nflxvideo.net | +-----> | VPN US +----+
|         |         |   hulu.com      |         |        |    |
+---------+         +-----------------+         +----+---+ UK |
                                                     |        |
                                                     +--------+
```

# instructions
1. obtain a Rasberry Pi 3 with a SD card (4GB+) and download and install [Etcher](http://www.etcher.io/)
2. download the [.img](#) file, burn it to the SD card, then insert the card into the RPi
3. connect the RPi to the Internet using a spare Ethernet port on your router (power using the recommended power adapter **do not** power off a USB port)
5. after a few minutes, connect to a new Wi-Fi network called `black.box` (passphrase: `blackbox`)
6. visit [http://blackbox/](http://blackbox/), click subscribe to setup up a PayPal billing agreement and claim your **1 month free** trial
7. once subscribed, you will be redirected back to the [dashboard](#dashboard)
8. after a few minutes, your device will finish updating and unblock the default region[[n4](#footnotes)]
9. for issues, please contact [support](mailto:blackbox@belodedenko.me)

# dashboard
The device dashboard is accessible by navigating to [black.box](http://blackbox/) while connected to the `black.box` Wi-Fi network.

![black.box dashboard](https://raw.githubusercontent.com/ab77/black.box/master/images/dashboard.png)

# other regions
`United States` and `United Kingdom` are currently suported regions.

To change the default region[[n4](#footnotes)], click the appropriate flag on the [dashboard](#dashboard). Please note, you may temporarily lose network connectivity while the device reboots with the new settings. To avoid this, change back to you normal network for a few minutes, before changing back to `black.box`.

# cancellation
Please visit PayPal to cancel your `black.box` subscription.

![PayPal cancel subscription](https://raw.githubusercontent.com/ab77/black.box/master/images/paypal.png)

#### footnotes
1. default domain list: `netflix.com`, `nflxvideo.net` and `hulu.com`
2. default ASNs: `AS2906`
3. default ports: `80/tcp`, `443/tcp` and `53/udp`
4. default region: `United States`

<hr>
<p align="center">&copy; 2016 <a href="http://ab77.github.io/">belodetek</a></p>
<p align="center"><a href="http://anton.belodedenko.me/"><img src="https://avatars2.githubusercontent.com/u/2033996?v=3&s=50"></a></p>

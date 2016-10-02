# about
black.box is a proprietary plug-and-play, peer-to-peer VPN policy routing sofware, which runs on a [Raspberry Pi 3](https://en.wikipedia.org/wiki/Raspberry_Pi) hardware device. This service is not designed for privacy and/or anonymity since it uses OpenVPN as the tunnel transport protocol, without encryption.

The software uses a list of DNS domain names[[n1](#footnotes)] and IPv4/IPv6 subnets/IPs[[n2](#footnotes)], which are routed via the tunnel interface, while all the remaining traffic flows via the local Internet interface. The tunnel interface only allows specific network ports[[n3](#footnotes)], while the local interface in unrestricted. All other traffic is blocked on the tunnel interface.

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

A [subscription](#subscription) is required to activate the device. This service is offered on a rolling subscription basis, with first month free. Afterwards a monthly subscription fee applies, unless the subscription is [cancelled](#cancellation) prior to the next billing cycle.

# instructions
* obtain a Rasberry Pi 3 and SD card (4GB+)
* download and install [Etcher](http://www.etcher.io/)
* download the [.img](#) file
* burn the `.img` file to the SD card, eject the freshly burnt card and insert into your device
* connect your device to the Internet using a spare Ethernet port on your router
* power the device using the recommended power adapter (**do not** power off a USB port)
* after a few minutes, connect to the new Wi-Fi network called `black.box`
* your `black.box` will automatically connect to a VPN server in the default region[[n4](#footnotes)]
* visit [black.box](http://blackbox/), subscribe via PayPal to get **1 month free** trial
* your device will automatically reboot with the activated subscription
* for issues, please contact [support](blackbox@belodedenko.me)

# cancellation
Please visit PayPal to cancel your `black.box` subscription.

#### footnotes
1. default domain list: `netflix.com`, `nflxvideo.net` and `hulu.com`
2. default ASNs: `AS2906`
3. default ports: `80/tcp`, `443/tcp` and `53/udp`
4. default region: `United States`

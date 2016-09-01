# about
black.box is a proprietary plug-and-play, peer-to-peer VPN policy routing sofware, which runs on a [Raspberry Pi 3](https://en.wikipedia.org/wiki/Raspberry_Pi) hardware device. This service is not designed for privacy and/or anonymity since it uses OpenVPN as the tunnel transport protocol, without encryption.

The software alows a configurable list of DNS domain names[[n1](#footnotes)] and IPv4/IPv6 subnets/IPs[[n2](#footnotes)] to be specified, which is routed via the tunnel interface, while the remaining traffic flows via the local Internet interface. The tunnel interface only allows specific network ports[[n3](#footnotes)]. All other traffic is blocked on the tunnel interface.

```
+---------+         +-----------------+
|         |  Wi-Fi  |                 |  google.com, etc.
|   iOS   | +-----> |    black.box    | +---------------->
|         |         |                 |
+---------+         |                 |
                    |                 |
+---------+         |                 |
|         |  Wi-Fi  |                 |
| Windows | +-----> |                 |
|         |         |                 |
+---------+         |                 |
                    |                 |
+---------+         |                 |         +--------+
|         |  Wi-Fi  |                 |   VPN   |        |
|  OS X   | +-----> |                 | +-----> | VPN US +----+
|         |         |                 |         |        |    |
+---------+         +-----------------+         +----+---+ UK |
                                                     |        |
                                                     +--------+
```

A [subscription](#subscription) is required to activate the device. This service is offered on a rolling subscription basis, with first month free. Afterwards a monthly subscription fee applies, unless the subscription is [cancelled](#cancellation) prior to the next billing cycle.

# instructions
* obtain a compatible device and SD card (4GB is enough)
* download and install [Etcher](http://www.etcher.io/)
* download the [.img](#) file
* burn the `.img` file to the SD card, eject the freshly burnt card and insert into your Rasberry Pi
* connect your Rasberry Pi to the Internet using a spare Ethernet port on your router
* power the Rasberry Pi using the recommended power adapter (**do not** just plug in into a spare USB port)
* after a few minutes, connect to the new Wi-Fi network called `black.box`
* your `black.box` will automatically connect to a VPN server in the default region[[n4](#footnotes)]
* visit the local API at [http://172.24.255.254/](http://172.24.255.254/)
* record and email your unique `guid` and **subscription** email address to [support](blackbox@belodedenko.me)
* for issues, please contact [support](blackbox@belodedenko.me)

# subscription
...

# cancellation
...

#### footnotes
[1] default domain list: `netflix.com`, `nflxvideo.net` and `hulu.com`.
[2] default ASNs: `AS2906`
[3] default ports: `80/tcp`, `443/tcp` and `53/udp`.
[4] default region: `United States`

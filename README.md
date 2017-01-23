# about
black.box is a small secondary Wi-Fi router, which runs on a [Raspberry Pi 3](https://en.wikipedia.org/wiki/Raspberry_Pi) and un-blocks popular Internet content on all devices, including tablets, smartphones, desktops, laptops and TVs. Includes optional VPN obfuscation/cloaking mode, to enable functioning in hostile deep packet inspection environments.

Devices connected to the `black.box` Wi-Fi network or routed via the device's Ethernet (LAN) IP address, can access blocked Internet content from anywhere in the world.

PayPal subscription or Bitcoin credit is required to activate the device. This service is offered on a rolling subscription basis, with **1 moth free trial** using PayPal. Afterwards a monthly subscription fee applies, unless the subscription is [cancelled](#cancellation) prior to the next billing cycle. The subscription fee is currently **$9.95 USD per month**.

Alternatively, pay up-front using Bitcoin for as much time as you need. Price quoted based on USD/BTC exchange rate. Top-up at any point prior to the existing Bitcoin credit expiry, or after. Any unused Bitcoin credit will be rolled over if topping up prior to existing credit expiry. Topping up after credit expiry will strike a new USD/BTC exchange rate.

The device routes specified traffic (e.g. netflix.com) via the un-encrypted[[n4](#footnotes)] tunnel/virtual interface, while all the remaining traffic (e.g. google.com) goes out via the local Internet interface. For security reasons, the tunnel interface only allows specific network ports[[n1](#footnotes)] for streaming, while the local interface in unrestricted for gaming traffic, etc.

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
1. obtain a [Rasberry Pi 3](https://www.amazon.co.uk/Raspberry-Pi-Official-Desktop-Starter/dp/B01CI5879A) starter kit, download and install [Etcher](http://www.etcher.io/)[[n3](#footnotes)]
2. download and uncompress the [.img](https://s3.eu-central-1.amazonaws.com/belodetech/resin-rpi3-1.24.1-2.8.3-eef8cf4afe02.img.gz) file, burn it to the SD card with `Etcher`, then insert the card into the Pi
3. connect the Pi to the Internet using a spare Ethernet port on your router (1A+ power supply, not USB port)[[n2](#footnotes)]
4. after initial initialisation (around 15-20 minutes)[[n5](#footnotes)] visit [http://blackbox.local/](http://blackbox.local/) URL, click subscribe to setup up a PayPal billing agreement and claim your **1 month free** trial or PAYG using Bitcoin
5. once subscribed, you will be redirected back to the [dashboard](#dashboard) where you can monitor the status
7. connect to a new Wi-Fi network called `black.box` (passphrase: `blackbox`) or set your default gateway to the `black.box` LAN IP as shown on the [dashboard](#dashboard)
8. try accessing some previously blocked Internet content
9. for issues, please contact [support](mailto:blackbox@belodedenko.me) or `#netflix-proxy` on Freenode IRC.

# dashboard
The device dashboard is accessible by navigating to [black.box](http://blackbox.local/) URL while connected to the `black.box` Wi-Fi network or from the LAN.

![black.box dashboard](https://raw.githubusercontent.com/ab77/black.box/master/images/dashboard.png)

If multiple regions are available to un-block, click a country flag in the top right corner of the [dashboard](#dashboard). The device will re-boot with the new settings and un-block the selected country.

# cancellation
Please visit PayPal to cancel your `black.box` subscription.

![PayPal cancel subscription](https://raw.githubusercontent.com/ab77/black.box/master/images/paypal.png)

#### footnotes
1. default ports: `80/tcp`, `443/tcp` and `53/udp`
2. The radio in the Pi is weak, please try to locate as close as possible to the streaming device(s).
3. [Raspberry Pi 2 Model B](https://www.raspberrypi.org/products/raspberry-pi-2-model-b/) with an [Alfa Network AWUS036NEH](https://www.amazon.co.uk/dp/B003JTM9JY) USB Wi-Fi dongle will also work and may even provide better signal due to the external Wi-Fi antenna.
4. For performance reasons, the tunnel interface provides no additional encryption overhead.
5. monitor by pinging `blackbox.local` from your LAN

<hr>
<p align="center">&copy; 2016 <a href="http://ab77.github.io/">belodetek</a></p>
<p align="center"><a href="http://anton.belodedenko.me/"><img src="https://avatars2.githubusercontent.com/u/2033996?v=3&s=50"></a></p>

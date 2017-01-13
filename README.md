# about
black.box is a small Wi-Fi router, which runs on a [Raspberry Pi 3](https://en.wikipedia.org/wiki/Raspberry_Pi) and un-blocks Netflix on all devices, including tablets, smartphones, desktops, laptops and TVs.

Devices connected to the `black.box` Wi-Fi network, can access content, such as Netflix and BBC iPlayer from anywhere in the world.

PayPal subscription or Bitcoin credit is required to activate the device. This service is offered on a rolling subscription basis, with **1 moth free trial** using PayPal. Afterwards a monthly subscription fee applies, unless the subscription is [cancelled](#cancellation) prior to the next billing cycle. The subscription fee is currently **$9.95 USD per month**.

Alternatively, pay up-front using Bitcoin for as much time as you need. Price quoted based on USD/BTC exchange rate. Top-up at any point prior to the existing Bitcoin credit expiry, or after. Any unused Bitcoin credit will be rolled over if topping up prior to existing credit expiry. Topping up after credit expiry will strike a new USD/BTC exchange rate.

The device routes specified traffic (e.g. netflix.com) via the un-encrypted[[n5](#footnotes)] tunnel/virtual interface, while all the remaining traffic (e.g. google.com) flows via the local Internet interface. The tunnel interface only allows specific network ports[[n1](#footnotes)] for streaming, while the local Internet interface in unrestricted for gaming, etc.

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
1. obtain a [Rasberry Pi 3](https://www.amazon.co.uk/Raspberry-Pi-Official-Desktop-Starter/dp/B01CI5879A) starter kit, download and install [Etcher](http://www.etcher.io/)[[n4](#footnotes)]
2. download and uncompress the [.img](https://s3.eu-central-1.amazonaws.com/belodetech/resin-rpi3-1.24.1-2.8.3-eef8cf4afe02.img.gz) file, burn it to the SD card with `Etcher`, then insert the card into the Pi
3. connect the Pi to the Internet using a spare Ethernet port on your router (power using an adapter, not USB port)[[n3](#footnotes)]
4. after a few minutes, connect to a new Wi-Fi network called `black.box` (passphrase: `blackbox`)
5. visit [http://blackbox/](http://blackbox/), click subscribe to setup up a PayPal billing agreement and claim your **1 month free** trial or PAYG using Bitcoin
6. once subscribed, you will be redirected back to the [dashboard](#dashboard)[[n2](#footnotes)]
7. after a few minutes, your device will finish updating and unblock the selected country
8. for issues, please contact [support](mailto:blackbox@belodedenko.me)

# dashboard
The device dashboard is accessible by navigating to [black.box](http://blackbox/) while connected to the `black.box` Wi-Fi network.

![black.box dashboard](https://raw.githubusercontent.com/ab77/black.box/master/images/dashboard.png)

To change regions, click any available flag in the top right corner of the [dashboard](#dashboard)[[n2](#footnotes)].

# cancellation
Please visit PayPal to cancel your `black.box` subscription.

![PayPal cancel subscription](https://raw.githubusercontent.com/ab77/black.box/master/images/paypal.png)

#### footnotes
1. default ports: `80/tcp`, `443/tcp` and `53/udp`
2. You may temporarily lose network connectivity while the device reboots with the new settings. To avoid this, change back to your normal network for a few minutes, before changing back to `black.box`.
3. The radio in the Pi is weak, please try to locate as close as possible to the streaming device(s).
4. [Raspberry Pi 2 Model B](https://www.raspberrypi.org/products/raspberry-pi-2-model-b/) with an [Alfa Network AWUS036NEH](https://www.amazon.co.uk/dp/B003JTM9JY) USB Wi-Fi dongle will also work and may even provide better signal due to the external Wi-Fi antenna.
5. For performance reasons, the tunnel interface provides no additional encryption overhead.

<hr>
<p align="center">&copy; 2016 <a href="http://ab77.github.io/">belodetek</a></p>
<p align="center"><a href="http://anton.belodedenko.me/"><img src="https://avatars2.githubusercontent.com/u/2033996?v=3&s=50"></a></p>

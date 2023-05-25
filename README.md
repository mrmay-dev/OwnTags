# Ⓣ OwnTags
![#f03c15](https://placehold.co/15x15/50bf54/50bf54.png) The purpose of this branch is to try using a proxy / client configurtion AND to implement using a TOML file for settings.

I work on this for a little in the evenings after work, please bear with me as I complete the documentation. Thanks!

> **Updated on May 25, 2023:** This branch now uses a TOML file for configuration. Hopefully, comments in the file make it self explanatory. Also, I'm hoping the directory structure reduces clutter and makes the project easier to look at.

This project makes it possible to use [OwnTracks](https://owntracks.org/) apps ([Android](https://play.google.com/store/apps/details?id=org.owntracks.android), [iOS](https://itunes.apple.com/us/app/mqttitude/id692424691?mt=8) and [web](https://github.com/owntracks/frontend)) as the app for following and viewing Haystack tags.

OwnTracks is well integrated into home automation projects like [Home Assistant](https://www.home-assistant.io/integrations/owntracks/) and [OpenHab](https://www.openhab.org/addons/bindings/gpstracker/). I can imagine some really cool things that could be done.

![map displaying owntracks features like track lines, heatmaps and  regions](map-features.png "OwnTracks Map Features")

<!-- I'm going to use these in some screenshots.
Robots: 33.81411508658622, -117.9209239699076
Light Saber: 33.814089694852186, -117.92266596079212
Luke: 33.8141448100308, -117.92313412450245
X-Wing: 33.814162638077384, -117.92309657349315
-->
## Installation 

This is a very new project and is under active development. I'm not the greatest programmer (something I picked up during COVID) so I learn as I go... meaning this thing could break at any moment for very silly reasons. That said, I am excited about it and hope a few others will join me to build something interesting. This work [builds the work of others](https://github.com/mrmay-dev/owntags/tree/dev-client#notes-of-gratitude).

### Requirements:

1. MacOS Monterrey (v12) or higher. (This can be an actual Mac or a virtual one. Check out [Headless Haystack](https://github.com/dchristl/headless-haystack) for a complete solution.)

2. A recent version of Python. [Homebrew](https://docs.brew.sh/Homebrew-and-Python) is probably the easiest way to get this.

3. An MQTT broker. Homebrew is [the recommended way](https://mosquitto.org/download/#mac) to get this. Cloud MQTT brokers are available. Have a look at:
     - [HiveMQ](https://www.hivemq.com/mqtt-cloud-broker/)
     - [MyQttHub](https://myqtthub.com/en)
     - [CloudMQTT](https://www.cloudmqtt.com/)
     - [fogwing](https://www.fogwing.io/)

4. A *working* OwnTracks app. Before going any further stop here. *Make sure you have [OwnTracks up and running](https://owntracks.org/booklet/) before doing anything else!* Apps are availble for [Android](https://play.google.com/store/apps/details?id=org.owntracks.android) and [iOS](https://itunes.apple.com/us/app/mqttitude/id692424691?mt=8). The [web frontend](https://github.com/owntracks/frontend) has extra reqirements and additional, cool features but is very worth the effort *after* getting the apps to work.


### Install

These instructions are based on a Homebrew installed Python with a locally hosted MQTT broker. Make changes to reflect your system. Python commands should work with regualar Python as well. If you are using Anaconda then you probably know how to do these things in a `conda` environment.

**Download**

- Download [the files](https://github.com/mrmay-dev/owntags/archive/refs/heads/main.zip) in this branch.
- Unzip and navigate to the folder in the terminal

```bash
cd /Users/lukeskywalker/Projects/owntags
```

**Create a virtual environment for Python**
```bash
python3 -m venv venv
```

**Activate the environment**

Deactivate it when done by closeing the terminal or typing `deactivate`.

```bash
source venv/bin/activate
```

### Configure

Edit the `settings.toml` file with your settings.

```toml

[owntag_options]
password = "password"  # macOS password
print_history = 1
    # positive numbers (4), the number of messages you want to see
    # negative numbers (-1) will print all fetched locations,
    # 0 will turn printing fetched locations off
status_msg = false  # publish status and metadata
    # Status messages can be sent to an MQTT Topic
status_base = "status/owntags"  # topic for status messages

[mqtt_secrets]
mqtt_broker = "your-broker.com"  # broker address
mqtt_port = 1883  # 1883 if no TLS; 8883 if TLS
mqtt_tls = "None"  # Comment out if using TLS
mqtt_user = "username"  # Broker user
mqtt_pass = "password"  # Broker password
# [mqtt_secrets.mqtt_tls]  # If TLS is activated, use this
# ca_certs = "output/isrgrootx1.cer"  # where the cert file located
    # download HiveMQ certificate: https://community.hivemq.com/t/frequently-asked-questions/514
    # create users at https://console.hivemq.com

[owntracks_options]
owntracks_device = "owntracks/user"  # Topic Base of your phone, used for waypoints
owntags_base = nan  # topic Base for tags. If `nan` owntracks_devce will be used.

[tag_options.prefix]
location = true   # (not required) locations are seen by everyone with access to the topic (they act like users)
waypoint = false  # (not required) waypoints are only seen on your phone (or device)
timestamp = 1000000001   # (required for wayponts) Must be unique, can be any past Unix/Posix timestamp.
radius = false    # (not required) use number for radius in meters, if `false` turn off, if `true` use confidence
mqtt_topic = nan  # (not required)  topic for this tag, if `nan` owntags_base will be used
status_topic = false    # (not required) if `True` messages will be published to `status_base`/prefix
# tag_name = "Tag Name"  #  (not implementented, yet) the display name of the tag
# tag_image = nan  #  (not implementented, yet) base 64 encoded, 200x200, PNG or JPEG image

```

[Sorry all, this all I had time for tonight. I add a little each day after work.]
 
## Notes of Gratitude

None of this would be possible without building on the work of many others who are much more talented than I am. This project builds on the amazing work of many projects and those involved:

- **[OpenHaystack](https://github.com/seemoo-lab/openhaystack):** the original project that figured out how to piggy-back onto Apple's FindMay real-time location system (RTLS) framework.

- **[openhaystack-python](https://github.com/hatomist/openhaystack-python):** who wrote the `AirTagCrypto` library to decode location reports that is used in many of the projects below.

- **[FindMy](https://github.com/biemster/FindMy):** who wrote the server, client and standalone scripts that allow fetching and decrypting location reports without a GUI and without an Apple Mail plugin.

- **[Headless Haystack](https://github.com/dchristl/headless-haystack):** who assembled, and is refining, the various parts to create an integrated solution that simplifies managing devices that leverage Apples' FindMy RTLS.

OwnTags builds directly on the work of [@dchristl](https://github.com/dchristl) in Headless Haystack. I've humbly taken that code, cleaned it up a bit, and added what is needed to forward locaton reports to an OwnTracks system.

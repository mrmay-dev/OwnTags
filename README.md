**Latest Update:** Monday, September 11, 2023

# Ⓣ OwnTags

I work on this for a little in the evenings after work. Thanks for visiting!

This project makes it possible to use [OwnTracks](https://owntracks.org/) apps ([Android](https://play.google.com/store/apps/details?id=org.owntracks.android), [iOS](https://itunes.apple.com/us/app/mqttitude/id692424691?mt=8) and [web](https://github.com/owntracks/frontend)) as the app for following and viewing Haystack tags.

OwnTracks is well integrated into home automation projects like [Home Assistant](https://www.home-assistant.io/integrations/owntracks/) and [OpenHab](https://www.openhab.org/addons/bindings/gpstracker/). I can imagine some really cool things that could be done.

**Updated on May 27, 2023:** 

* introduced settings TOML file for configuration. Hopefully, comments in the file make it self explanatory. 
* simplified directory structure to reduce clutter and makes the project easier to look at.
* timeframe to retreive location reports is done with `--time hh:mm` flag
* location reports can be stored to [TinyDB](https://tinydb.readthedocs.io/en/latest/index.html), this will change to [tinyfluxDB](https://tinyflux.readthedocs.io/en/latest/intro.html) soon.
* tweaked terminal output


This is a very new project and is under active development. I'm not the greatest programmer (something I picked up during COVID) so I learn as I go... meaning this thing could break at any moment for very silly reasons. That said, I am excited about it and hope a few others will join me to build something interesting. This work [builds the work of others](https://github.com/mrmay-dev/owntags/tree/dev-client#notes-of-gratitude).

<!-- ![map displaying owntracks features like track lines, heatmaps and  regions](map-features.png "OwnTracks Map Features")

I'm going to use these in some screenshots.
Robots: 33.81411508658622, -117.9209239699076
Light Saber: 33.814089694852186, -117.92266596079212
Luke: 33.8141448100308, -117.92313412450245
X-Wing: 33.814162638077384, -117.92309657349315
-->
## Installation 

To track tags with OwnTracks using this project you will need:

1. MacOS Monterrey (v12) or higher. (This can be an actual Mac or a virtual one. Check out [Headless Haystack](https://github.com/dchristl/headless-haystack) for a complete solution.)

2. Python 3.7 or newer. [Homebrew](https://docs.brew.sh/Homebrew-and-Python) is probably the easiest way to get this.

3. An MQTT broker. Homebrew is [the recommended way](https://mosquitto.org/download/#mac) to get this. Cloud MQTT brokers are an interesting option. Have a look at:
     - [HiveMQ](https://www.hivemq.com/mqtt-cloud-broker/)
     - [MyQttHub](https://myqtthub.com/en)
     - [CloudMQTT](https://www.cloudmqtt.com/)
     - [fogwing](https://www.fogwing.io/)

4. A *working* OwnTracks app. Before going any further stop here. *Make sure you have [OwnTracks up and running](https://owntracks.org/booklet/) before doing anything else!* Apps are availble for [Android](https://play.google.com/store/apps/details?id=org.owntracks.android) and [iOS](https://itunes.apple.com/us/app/mqttitude/id692424691?mt=8). The [web frontend](https://github.com/owntracks/frontend) has extra reqirements and additional, cool, features but is very worth the effort *after* getting the apps to work.

### Install

These instructions are based on a Homebrew installed Python with a locally hosted MQTT broker. Make changes to reflect your system. Python commands should work with regualar Python as well. If you are using Anaconda then you probably know how to do these things in a `conda` environment.

**Download**
- Download [the files](https://github.com/mrmay-dev/owntags/archive/refs/heads/dev-client.zip) in this branch.
- Unzip and navigate to the folder in the terminal

```bash
cd /Users/lukeskywalker/Projects/owntags
```

**Create a virtual environment for Python**

```bash
python3 -m venv venv
```

**Activate the environment**

Deactivate it when done by closing the terminal or typing `deactivate`.

```bash
source venv/bin/activate
```

**Upgrade PIP & Install required libraries:**

```bash
pip install --upgrade pip
pip install pyobjc cryptography six paho-mqtt  # tinydb, only if you want to export locations to this database
``` 

### Configure

You will need:

* keyfiles of your tags
    * Unfortunately, these tags can be used in nefarioius ways. So, it'll take some exploring to learn how to make them. These are good places to start: [OpenHaystack](https://github.com/seemoo-lab/openhaystack/tree/main/Firmware/ESP32#deploy-the-firmware) or [headless-haystack](https://github.com/dchristl/headless-haystack/tree/main/firmware/ESP32)
* iTunes passoword (to decrypt location reports)
* MQTT broker information
* OwnTracks broker topics

#### KeyFiles

Create directory `applicaton/keys/` and put your keyfiles in there:

```text
owntags/
└── application/
    └── keys/
        ├── prefix-1.keyfile
        └── prefix-2.keyfile
```

#### Settings

Add your iTunes password, MQTT broker details and OwnTracks topics to the `settings.toml` file.

```toml
# -- INSTRUCTIONS --
# Make a copy of this file and rename it settings.toml.
# add information about your system, MQTT broker, OwnTracks setup.
# Create a new settings block for each tag. 

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
mqtt_broker = "broker address "  # broker address
mqtt_port = 1883  # 1883 if no TLS; 8883 if TLS
mqtt_user = "username"  # Broker user
mqtt_pass = "password"  # Broker password
# MQTT options for using TLS. No changes needed if your server is not using TLS.
mqtt_tls = "None"  # To use TLS comment out this line by putting a '#' in front of it.
# Uncomment these lines and adjust to your needs
# [mqtt_secrets.mqtt_tls]
# ca_certs = "keys/isrgrootx1.cer"  # cert location, the 'keys' folder is a good place
# download HiveMQ certificate: https://community.hivemq.com/t/frequently-asked-questions/514
# create users at https://console.hivemq.com

[owntracks_options]
owntracks_device = "owntracks/phone"  # user Topic Base of your phone or device with owntracks, used for waypoints
owntags_base = nan  # topic base for tags. If `nan` owntracks_device will be used.

# Each tag can be configured to appear as 'waypoints' on your device only, or as 'locations' that are shared
# with other users. 'locations' are easier to start with.
# OwnTags can share the tag as both, odd things will happen and be prepared for some challenges.
[tag_options.prefix]
tag_name = "prefix"  # the prefix of your key
location = true   # (not required) locations are seen by everyone with access to the topic (they act like users)
waypoint = false  # (not required) waypoints are only seen on your phone (or device)
timestamp = 1000000001   # (required for wayponts) Must be unique, can be any past Unix/Posix timestamp.
radius = false    # (not required) use number for radius in meters, if `false` turn off, if `true` use confidence
# Advance Features
tag_image = nan  # base 64 encoded, 200x200, PNG or JPEG image
mqtt_topic = nan  # (not required)  topic for this tag, if `nan` owntags_base will be used
status_topic = false    # (not required) if `True` messages will be published to `status_base`/prefix
```

### Run
There are a couple of ways to start. The `owntags.sh` bash script will load the Python environment and fetch reports. Time is specified with `hh:mm` format. Plain double digits (`42`) will be interpreted as minutes.

```bash
./owntags.sh 0:30
```

Optionally, drop into the `application` folder and start `request_reports.py` manually. `--owntags` tells the script to send locations to OwnTracks:

```bash
cd application
request_reports.py --time 0:60 --owntags
```

[Sorry all, this all I had time for tonight. I add a little each day after work.]
 
## Notes of Gratitude

None of this would be possible without building on the work of many others who are much more talented than I am. This project builds on the amazing work of many projects and those involved:

- **[OpenHaystack](https://github.com/seemoo-lab/openhaystack):** the original project that figured out how to piggy-back onto Apple's FindMay real-time location system (RTLS) framework.

- **[openhaystack-python](https://github.com/hatomist/openhaystack-python):** who wrote the `AirTagCrypto` library to decode location reports that is used in many of the projects below.

- **[FindMy](https://github.com/biemster/FindMy):** who wrote the server, client and standalone scripts that allow fetching and decrypting location reports without a GUI and without an Apple Mail plugin.

- **[Headless Haystack](https://github.com/dchristl/headless-haystack):** who assembled, and is refining, the various parts to create an integrated solution that simplifies managing devices that leverage Apples' FindMy RTLS.

OwnTags builds directly on the work of [@dchristl](https://github.com/dchristl) in Headless Haystack. I've humbly taken that code, cleaned it up a bit, and added what is needed to forward locaton reports to an OwnTracks system.

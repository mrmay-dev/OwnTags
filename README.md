# Ⓣ OwnTags
![#f03c15](https://placehold.co/15x15/50bf54/50bf54.png) The purpose of this branch is to try using a proxy/client configurtion.

I work on this for a little in the evenings after work, please bear with me as I complete the documentation. Thanks!

> **Updated on May 10, 2023:** I'm not very good at managing a git. Good thing no one is making pull requests. I think I'd royally mess things up. I like this configuration. The work done over at headless-haystack can be tracked on the `headless-main` branch and the OwnTags-specific changes can continue on the main.

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

This is a very new project and is under active development. I'm not the greatest programmer (something I picked up during COVID) so I learn as I go... meaning this thing could break at any moment for very silly reasons. That said, I am totally excited about it and hope a few others will join me to build something interesting.

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

Edit the `secrets.py` with your settings. There are notes in there to guide you. 

Apple's FindMy location messages are encrypted on the tag and decrypted on the computer that receives them. To do that, the script needs your password so it can access the system keychain and decode location messages.

```python
secrets = {
    "password": "macOSpassowrd",  # your device's password to access keychain and decrypt messages.
```

Optionally, the script can print location reports to the terminal. I like to see the latest, but listing all messages can be useful for debugging. 

```python
    # == Console Printing
    # positive numbers (4), the number of messages you want to see
    # negative numbers (-1) will print all fetched locations,
    # 0 will turn printing fetched locations off
    "print_history": 1,
```

Console Messages can be sent to an MQTT Topic.

```
    # == Status Messages
    # Console Messages can be sent to an MQTT Topic
    "status_msg": False,  # publish status and metadata
    "status_base": "status/owntags",  # topic for status messages
```

In OwnTracks, users can have multiple devices (phone, tablet, computer, etc), tags are just another device. Typically, you'll want tags to publish as your device. By [editing the MQTT ACLs](https://duckduckgo.com/?q=mqtt+acl&t=brave&ia=web) you can control topics that are visible to others, shared devices could be put on a shared topic.

```python
    # == Owntracks Options
    "owntracks_device": "owntracks/richard",  # user Topic Base of your phone, used for waypoints
    "owntags_base": None,  # topic base for tags. If `None` owntracks_devcies will be used.
```    

Each device must have its own configuration. To do that, duplicate this key for each device and **change `tag_prefix`** to your tag's prefix and the **`"tst"` value to a unique Unix timestamp**.

```python 
    # == Device options
    "tag_prefix": {  # this is the prefix of your tag.
        "tst": 1000000001,  # this can be any past Unix/Posix timestamp
        "waypoint": False,  # Waypoints are only seen on your phone (or device)
        "location": True,  # locations are seen by everyone with access to the topic (they act like users)
        "status": False,  # if `True` messages will be published to `status_base`/prefix
        "mqtt_topic": None,  # topic for this tag, if `None` owntags_base will be used
    },
}
```


[Sorry all, this all I had time for tonight. I add a little each day after work.]
 
## Notes of Gratitude

None of this would be possible without building on the work of many others who are much more talented than I am. This project builds on the amazing work of many projects and those involved:

- **[OpenHaystack](https://github.com/seemoo-lab/openhaystack):** the original project that figured out how to piggy-back onto Apple's FindMay real-time location system (RTLS) framework.

- **[openhaystack-python](https://github.com/hatomist/openhaystack-python):** who wrote the `AirTagCrypto` library to decode location reports that is used in many of the projects below.

- **[FindMy](https://github.com/biemster/FindMy):** who wrote the server, client and standalone scripts that allow fetching and decrypting location reports without a GUI and without an Apple Mail plugin.

- **[Headless Haystack](https://github.com/dchristl/headless-haystack):** who assembled, and is refining, the various parts to create an integrated solution that simplifies managing devices that leverage Apples' FindMy RTLS.

OwnTags builds directly on the work of [@dchristl](https://github.com/dchristl) in Headless Haystack. I've humbly taken that code, cleaned it up a bit, and added what is needed to forward locaton reports to an OwnTracks system.

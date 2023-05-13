
owntag_options = {
    "password": "password",  # macOS password

    # == Console Printing
    # positive numbers (4), the number of messages you want to see
    # negative numbers (-1) will print all fetched locations,
    # 0 will turn printing fetched locations off
    "print_history": 1,

    # == Status Messages
    # Status messages can be sent to an MQTT Topic
    "status_msg": False,  # publish status and metadata
    "status_base": "status/owntags",  # topic for status messages

    # == Owntracks Options
    "owntracks_device": "owntracks/user",  # user Topic Base of your phone, used for waypoints
    "owntags_base": None,  # topic base for tags. If `None` owntracks_devcies will be used.

    # == Device options
    "tag_prefix": {  # this is the prefix of your tag.
        "tst": 1000000001,  # this can be any past Unix/Posix timestamp
        "location": True,  # locations are seen by everyone with access to the topic (they act like users)
        "waypoint": False,  # Waypoints are only seen on your phone (or device)
        "status": False,  # if `True` messages will be published to `status_base`/prefix
        "mqtt_topic": None,  # topic for this tag, if `None` owntags_base will be used
    },
}

mqtt_secrets = {
    "mqtt_broker": "",  # broker address
    "mqtt_port": 1883,  # 1883 if no TLS; 8883 if TLS
    # download HiveMQ certificate: https://community.hivemq.com/t/frequently-asked-questions/514
    # "mqtt_tls": {"ca_certs": "output/isrgrootx1.cer"},  # where the cert file located
    # create users at https://console.hivemq.com
    "mqtt_user": "ueser",  # Broker user
    "mqtt_pass": "password",  # Broker password
}

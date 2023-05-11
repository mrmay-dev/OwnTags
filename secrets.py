secrets = {
    "password": "macOSpassowrd",                 # your device's password to access keychain and decrypt messages.

    """ Console print settings """
    "print_history": 1,                          # any negative number will print all fetched locations in the console
                                                 # `0` will turn printing fetched locations off

    """ MQTT Broker Settings """
    "mqtt_broker": "ip or address",              # address of the broker for OwnTracks
    "mqtt_port": 1883,                           # Broker port
    "mqtt_user": "broker username",              # broker username
    "mqtt_pass": "broker password",              # broker password

    """ OwnTracks Settigs """
    "owntracks_device":"owntracks/user/device",  # topic of device (iPhone, Android, Web) to publish
                                                 # waypoint locatons.
    "haystack_base":"owntracks/owntags",         # topic base for tags. The tag prfix will be appended
    "encryption_key": "",                        # TODO (not ready yet) this will allow limiting who can read tag locations

    """ Debugging messages over MQTT """
    "status_msg": False,                         # should status messages be printed to MQTT.
    "status_base":"launchd/owntags"              # topic for printing status messages
}

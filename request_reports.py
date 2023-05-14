#!/usr/bin/env python3

# This script fetches OpenHaystack reports and prints them to the console
# or serves them OwnTags_plugin.py for processing.

import datetime
import argparse
import time
import json
import ssl
import re

from apple_cryptography import *

OUTPUT_FOLDER = 'output/'

start_script = '{:%Y %b %d (%a) %H:%M:%S}'.format(datetime.datetime.now())

print(f'{start_script}')
start_script = time.monotonic()

if __name__ == "__main__":
    isV3 = sys.version_info.major > 2
    print('Using python3' if isV3 else 'Using python2')
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-t', '--time', help='only show reports less than hh:mm (hours:minutes) old', default='00:00')
    parser.add_argument(
        '-d', '--days', help='only show reports less than these days.', type=int, default=0)
    parser.add_argument(
        '-p', '--prefix', help='only use keyfiles starting with this prefix', default='')
    parser.add_argument(
        '-k', '--key', help="iCloud decryption key ($ security find-generic-password -ws 'iCloud')")
    parser.add_argument(
        '-o', '--owntags', help="Enable experimental OwnTracks integration", action='store_true')
    parser.add_argument(  # willby switching to tinyfluxDB (https://github.com/citrusvanilla/tinyflux)
        '-b', '--tinydb', help="add reports to TinyDB database", action='store_true')
    args = parser.parse_args()

    pattern = re.compile("\d{1,2}:\d{2}")
    if not pattern.match(args.time):
        raise ValueError('Time not formatted as hh:mm.')
    else:
        hours_minutes = (args.time).split(":")
        hours = int(hours_minutes[0])
        minutes = int(hours_minutes[1])

    time_window = (((hours * 60) + minutes) + (args.days * 24 * 60)) * 60

    iCloud_decryptionkey = args.key if args.key else retrieveICloudKey()

    AppleDSID, searchPartyToken = getAppleDSIDandSearchPartyToken(iCloud_decryptionkey)
    machineID, oneTimePassword = getOTPHeaders()
    UTCTime, Timezone, unixEpoch = getCurrentTimes()

    request_headers = {
        'Authorization': "Basic %s" % (
            base64.b64encode((AppleDSID + ':' + searchPartyToken).encode('ascii')).decode('ascii')),
        'X-Apple-I-MD': "%s" % oneTimePassword,
        'X-Apple-I-MD-RINFO': '17106176',
        'X-Apple-I-MD-M': "%s" % machineID,
        'X-Apple-I-TimeZone': "%s" % Timezone,
        'X-Apple-I-Client-Time': "%s" % UTCTime,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-BA-CLIENT-TIMESTAMP': "%s" % unixEpoch
    }

    ids = {}
    names = {}
    prefixes = []
    for keyfile in glob.glob(OUTPUT_FOLDER + args.prefix + '*.keys'):
        # read key files generated with generate_keys.py
        with open(keyfile) as f:
            hashed_adv = ''
            priv = ''
            name = keyfile[len(OUTPUT_FOLDER):-5]
            prefixes.append(name)
            for line in f:
                key = line.rstrip('\n').split(': ')
                if key[0] == 'Private key':
                    priv = key[1]
                elif key[0] == 'Hashed adv key':
                    hashed_adv = key[1]

                if priv and hashed_adv:
                    ids[hashed_adv] = priv
                    names[hashed_adv] = name

    startdate = unixEpoch - time_window

    keys = '","'.join(ids.keys())

    data = '{"search": [{"endDate": %d, "startDate": %d, "ids":["%s"]}]}' % (
        (unixEpoch - 978307200) * 1000000, (startdate - 978307200) * 1000000, keys)
    # print(data)

    conn = six.moves.http_client.HTTPSConnection(
        'gateway.icloud.com', timeout=5, context=ssl._create_unverified_context())

    conn.request("POST", "/acsnservice/fetch", data, request_headers)
    response = conn.getresponse()
    response_status = (response.status, response.reason)
    print(response_status[0], response_status[1])
    if response.status == 500:
        raise Exception(response_status)
    res = json.loads(response.read())['results']
    print('\n%d reports received.' % len(res))
    # print(res)

    get_reports = time.monotonic()

    ordered = []
    found = set()
    for report in res:
        priv = bytes_to_int(base64.b64decode(ids[report['id']]))
        data = base64.b64decode(report['payload'])

        # the following is all copied from https://github.com/hatomist/openhaystack-python, thanks @hatomist!
        timestamp = bytes_to_int(data[0:4])
        if timestamp + 978307200 >= startdate:
            eph_key = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP224R1(), data[5:62])
            shared_key = ec.derive_private_key(priv, ec.SECP224R1(), default_backend()).exchange(ec.ECDH(), eph_key)
            symmetric_key = sha256(shared_key + b'\x00\x00\x00\x01' + data[5:62])
            decryption_key = symmetric_key[:16]
            iv = symmetric_key[16:]
            enc_data = data[62:72]
            tag = data[72:]

            decrypted = decrypt(enc_data, algorithms.AES(decryption_key), modes.GCM(iv, tag))
            res = decode_tag(decrypted)
            res['timestamp'] = timestamp + 978307200
            res['isodatetime'] = datetime.datetime.fromtimestamp(res['timestamp']).isoformat()
            res['key'] = names[report['id']]
            res['goog'] = 'https://maps.google.com/maps?q=' + str(res['lat']) + ',' + str(res['lon'])
            found.add(res['key'])
            ordered.append(res)

    ordered.sort(key=lambda item: item.get('timestamp'))

    found = list(found)
    missing = list(prefixes)
    for each in found:
        missing.remove(each)
    reports_used = len(ordered)
    print(f'{reports_used} reports used.')
    # print(f'list all: {prefixes}\nmissing: {missing}\nfound: {found}')

    if args.tinydb and len(ordered) > 0:
        from tinydb import TinyDB
        # 2023-05-12T2215_Fri %Y-%m-%dT%H%M_a%
        today_is = '{:%Y-%m-%d_%a}'.format(datetime.datetime.now())
        db = TinyDB(f'./output/tinydb/{today_is}.json')
        for each in ordered:
            db.insert(each)
        print(f'{reports_used} reports written to file.')
        
    if args.owntags:
        import OwnTags_plugin
        ordered = OwnTags_plugin.owntags(ordered, time_window, found)

    print(f'\n{"looked for:":<14}{prefixes}')
    print(f'{"missing keys:":<14}{missing}')
    print(f'{"found:":<14}{list(found)}')

    update_send = "~:~~"
    if len(found) > 0:

        send_time = ordered[len(ordered)-1]
        for key in send_time:
            send_time_key = key
            send_time_value = send_time[key]

        update_send = f'{send_time[key] - start_script:0.2f}s'
        ordered.pop()

        print(json.dumps(ordered, indent=4))  # use `separators=(',', ':')` for minimized output

end_script = time.monotonic()
print()
print(f'{"start:":<10} {start_script - start_script:0.2f}s')
print(f'{"received:":<10} {get_reports - start_script:0.2f}s')
print(f'{"MQTT sent:":<10} {update_send}')
print(f'{"end:":<10} {end_script - start_script:0.2f}s')
# print(f'time: {end_script.replace(microsecond=0).isoformat()}')

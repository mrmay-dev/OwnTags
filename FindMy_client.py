#!/usr/bin/env python3

# This script retreives reports from FindMy_proxy.py and
# - prints them to the console/terminal or,
# - serves them to OwnTags_plugin.py for processing (use `-o` or `--owntags`).

# THIS IS STILL IN ROUGH STAGES OF DEVELOPMENT.
# A LOT OF THE CODE HERE WILL BE CUT OUT OR CHANGED

import requests
import argparse
import json

from apple_cryptography import *

from output.mysecrets import owntag_options
OUTPUT_FOLDER = 'output/'
# TODO: add a minutes time_frame. This will require tweaking the `FindMy_proxy`.
# TIME_FRAME = owntag_options["time_frame"]
TIME_FRAME = 1

print(f'{datetime.datetime.now().replace(microsecond=0).isoformat()}')

if __name__ == "__main__":
    isV3 = sys.version_info.major > 2
    print('Using python3' if isV3 else 'Using python2')
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d', '--days', help='only show reports not older than these days', type=int, default=TIME_FRAME)
    parser.add_argument(
        '-p', '--prefix', help='only use keyfiles starting with this prefix', default='')
    parser.add_argument(
        '-k', '--key', help="iCloud decryption key ($ security find-generic-password -ws 'iCloud')")
    parser.add_argument(
        '-o', '--owntags', help="Enable experimental OwnTracks integration", action='store_true')
    args = parser.parse_args()

    iCloud_decryptionkey = args.key if args.key else retrieveICloudKey()
    # iCloud_decryptionkey = retrieveICloudKey()
    AppleDSID, searchPartyToken = getAppleDSIDandSearchPartyToken(iCloud_decryptionkey)
    machineID, oneTimePassword = getOTPHeaders()
    UTCTime, Timezone, unixEpoch = getCurrentTimes()
    
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
    
    # Create JSON list of keys
    keys = '","'.join(ids.keys())
    keys = json.loads(f'["{keys}"]')
    
    # Create JSON payload
    # TODO: make this minutes instead of days
    payload = {"days": args.days, "ids": keys}
    print(f'\nPayload:\n{json.dumps(payload, indent=4)}')
    if payload["ids"][0] == "":
        raise ValueError('The key prefix requested cannot be found.')
    
    # Request reports from the server
    url = 'http://localhost:6176'
    r = requests.post(url, json=payload)
    print(f'Status code: {r.status_code}')
    
    # Capture the result
    res = r.json()['results']
    # print(json.dumps(res, indent=4))
    print(f'\n{len(res)} reports received.')
    
    # Decrypt each report
    ordered = []
    found = set()
    for report in res:
        priv = bytes_to_int(base64.b64decode(ids[report['id']]))
        data = base64.b64decode(report['payload'])

        # the following is all copied from https://github.com/hatomist/openhaystack-python, thanks @hatomist!
        timestamp = bytes_to_int(data[0:4])
        eph_key = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP224R1(), data[5:62])
        shared_key = ec.derive_private_key(priv, ec.SECP224R1(), default_backend()).exchange(ec.ECDH(), eph_key)
        symmetric_key = sha256(shared_key + b'\x00\x00\x00\x01' + data[5:62])
        decryption_key = symmetric_key[:16]
        iv = symmetric_key[16:]
        enc_data = data[62:72]
        tag = data[72:]

        decrypted = decrypt(enc_data, algorithms.AES(decryption_key), modes.GCM(iv, tag))
        
        # turn decrypted data into a library object
        res = decode_tag(decrypted)
        # add a few useful items
        res['timestamp'] = timestamp + 978307200
        res['isodatetime'] = datetime.datetime.fromtimestamp(res['timestamp']).isoformat()
        res['key'] = names[report['id']]
        res['goog'] = 'https://maps.google.com/maps?q=' + str(res['lat']) + ',' + str(res['lon'])
        # add the decrypted library to the ordered list
        ordered.append(res)
        # add the processed prefix to the found set
        found.add(res['key'])

    # create a list of prefixes that were not found
    missing = list(prefixes)
    for each in found:
        missing.remove(each)

    # send reports to the owntags plugin
    if args.owntags:
        import OwnTags_plugin
        ordered = OwnTags_plugin.owntags(ordered, args.minutes, found, prefixes, missing)
    
    # print results summary
    print(f'{"looked for:":<14}{prefixes}')  
    print(f'{"missing keys:":<14}{missing}')
    print(f'{"found:":<14}{list(found)}\n')
    if ordered is not None:
        print(json.dumps(ordered, indent=4))  # use `separators=(',', ':')` for minimized output

#!/usr/bin/env python

import base64
import json
import six
import ssl
import sys

from apple_cryptography import *

PORT = 6176

class ServerHandler(six.moves.SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        if hasattr(self.headers, 'getheader'):
          content_len = int(self.headers.getheader('content-length', 0))
        else:
          content_len = int(self.headers.get('content-length'))

        post_body = self.rfile.read(content_len)

        print('Getting with post: ' + str(post_body))
        UTCTime, Timezone, unixEpoch = getCurrentTimes()
        body = json.loads(post_body)
        # CHANGED: not useing `days`. Now using `seconds`.
        if "seconds" in body:
            seconds = body['seconds']
        else: 
            seconds = 7 * 86400  # query for seven days if 'seconds' key is not present

        print('Querying for ' + str(round(seconds/86400, 2)) + ' days'
              + f' (or {round(seconds/60, 2)} minutes, or {seconds} seconds)')
        startdate = (unixEpoch - seconds) * 1000

        data = '{"search": [{"ids": [\"%s\"]}]}' % ( "\",\"".join(body['ids']))

        iCloud_decryptionkey = retrieveICloudKey()
        AppleDSID, searchPartyToken = getAppleDSIDandSearchPartyToken(
            iCloud_decryptionkey)
        machineID, oneTimePassword = getOTPHeaders()
        UTCTime, Timezone, unixEpoch = getCurrentTimes()
        request_headers = {
            'Authorization': "Basic %s" % (base64.b64encode((AppleDSID + ':' + searchPartyToken).encode('ascii')).decode('ascii')),
            'X-Apple-I-MD': "%s" % (oneTimePassword),
            'X-Apple-I-MD-RINFO': '17106176',
            'X-Apple-I-MD-M': "%s" % (machineID),
            'X-Apple-I-TimeZone': "%s" % (Timezone),
            'X-Apple-I-Client-Time': "%s" % (UTCTime),
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-BA-CLIENT-TIMESTAMP': "%s" % (unixEpoch)
        }

        conn = six.moves.http_client.HTTPSConnection(
            'gateway.icloud.com', timeout=5, context=ssl._create_unverified_context())
        conn.request("POST", "/acsnservice/fetch", data, request_headers)
        res = conn.getresponse()
        result = json.loads(res.read())
        results = result["results"]
        print(f'{len(results)} results received.')

        newResults = [] 
        latestEntry = None
        
        for idx, entry in enumerate(results):
            if (int(entry["datePublished"]) > startdate):  
                newResults.append(entry)
            if latestEntry is None:
                latestEntry = entry
            elif latestEntry["datePublished"] < entry["datePublished"]:
                latestEntry = entry

        if seconds < 1 and latestEntry is not None:
            newResults.append(latestEntry)         
        result["results"] = newResults
        self.send_response(200)
        # send response headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        # send the body of the response
        responseBody = json.dumps(result)
        self.wfile.write(responseBody.encode())

        # print(responseBody)



if __name__ == "__main__":
    isV3 = sys.version_info.major > 2
    print('Using python3' if isV3 else 'Using python2')
    retrieveICloudKey()

    Handler = ServerHandler

    httpd = six.moves.socketserver.TCPServer(("", PORT), Handler)

    print("serving at port " + str(PORT))

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
        print('Server stopped')

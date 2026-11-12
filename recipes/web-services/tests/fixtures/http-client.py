"""HTTP client confined to the release fixture's internal Docker network."""
import base64
import http.cookiejar
import json
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request

payload = json.load(sys.stdin)
url = payload['url']
target = urllib.parse.urlsplit(url)
assert target.scheme == 'http' and target.hostname.startswith('web-services-release-')
assert target.hostname.endswith(('-cms', '-origin'))


class LocalRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, destination):
        assert urllib.parse.urlsplit(destination).netloc == urllib.parse.urlsplit(request.full_url).netloc
        assert urllib.parse.urlsplit(destination).scheme == 'http'
        return super().redirect_request(request, fp, code, message, headers, destination)


jar = http.cookiejar.MozillaCookieJar('/tmp/release-cookies.txt')
if pathlib.Path(jar.filename).exists():
    jar.load(ignore_discard=True)
opener = urllib.request.build_opener(LocalRedirect(), urllib.request.HTTPCookieProcessor(jar))
request = urllib.request.Request(url, headers=payload['headers'],
                                 data=payload['data'].encode() if payload['data'] is not None else None)
try:
    response = opener.open(request, timeout=8)
except urllib.error.HTTPError as error:
    response = error
body = response.read()
jar.save(ignore_discard=True)
print(json.dumps({'status': response.code, 'headers': dict(response.headers),
                  'body': base64.b64encode(body).decode()}))

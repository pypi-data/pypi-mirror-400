import k3awssign
import httplib

access_key = "your access key"
secret_key = "your secret key"

signer = k3awssign.Signer(access_key, secret_key)

file_content = "bla bla"
request = {
    "verb": "PUT",
    "uri": "/test-bucket/test-key",
    "args": {
        "foo2": "bar2",
        "foo1": True,
        "foo3": ["bar3", True],
    },
    "headers": {
        "Host": "bscstorage.com",
        "Content-Length": len(file_content),
    },
    "body": file_content,
}

signer.add_auth(request, sign_payload=True)

conn = httplib.HTTPConnection("ss.bscstorage.com")
conn.request(request["verb"], request["uri"], request["body"], request["headers"])
resp = conn.getresponse()

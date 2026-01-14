# k3awssign

[![Action-CI](https://github.com/pykit3/k3awssign/actions/workflows/python-package.yml/badge.svg)](https://github.com/pykit3/k3awssign/actions/workflows/python-package.yml)
[![Documentation Status](https://readthedocs.org/projects/k3awssign/badge/?version=stable)](https://k3awssign.readthedocs.io/en/stable/?badge=stable)
[![Package](https://img.shields.io/pypi/pyversions/k3awssign)](https://pypi.org/project/k3awssign)

A python lib is used for adding aws version 4 signature to request.

k3awssign is a component of [pykit3] project: a python3 toolkit set.


This lib is used to sign a request using aws signature version 4. You
need to provide a python dict which represent your request(it typically
contains `verb`, `uri`, `args`, `headers`, `body`), and your access key
and your secret key. This lib will add signature to the request.



# Install

```
pip install k3awssign
```

# Synopsis

```python

import k3awssign
import httplib

access_key = 'your access key'
secret_key = 'your secret key'

signer = k3awssign.Signer(access_key, secret_key)

file_content = 'bla bla'
request = {
    'verb': 'PUT',
    'uri': '/test-bucket/test-key',
    'args': {
        'foo2': 'bar2',
        'foo1': True,
        'foo3': ['bar3', True],
    },
    'headers': {
        'Host': 'bscstorage.com',
        'Content-Length': len(file_content),
    },
    'body': file_content,
}

signer.add_auth(request, sign_payload=True)

conn = httplib.HTTPConnection('ss.bscstorage.com')
conn.request(request['verb'], request['uri'],
             request['body'], request['headers'])
resp = conn.getresponse()

```

#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>


[pykit3]: https://github.com/pykit3
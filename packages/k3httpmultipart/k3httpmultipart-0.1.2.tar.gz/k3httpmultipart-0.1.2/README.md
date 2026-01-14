# k3httpmultipart

[![Action-CI](https://github.com/pykit3/k3httpmultipart/actions/workflows/python-package.yml/badge.svg)](https://github.com/pykit3/k3httpmultipart/actions/workflows/python-package.yml)
[![Build Status](https://travis-ci.com/pykit3/k3httpmultipart.svg?branch=master)](https://travis-ci.com/pykit3/k3httpmultipart)
[![Documentation Status](https://readthedocs.org/projects/k3httpmultipart/badge/?version=stable)](https://k3httpmultipart.readthedocs.io/en/stable/?badge=stable)
[![Package](https://img.shields.io/pypi/pyversions/k3httpmultipart)](https://pypi.org/project/k3httpmultipart)

This module provides some util methods to get multipart headers and body.

k3httpmultipart is a component of [pykit3] project: a python3 toolkit set.


#   Name

k3httpmultipart

#   Status

The library is considered production ready.




# Install

```
pip install k3httpmultipart
```

# Synopsis

```python

import os

import k3httpmultipart
import k3fs

# http request headers
headers = {'Content-Length': 1200}

# http request fields
file_path = '/tmp/abc.txt'
k3fs.fwrite(file_path, '123456789')
fields = [
    {
        'name': 'aaa',
        'value': 'abcde',
    },
    {
        'name': 'bbb',
        'value': [open(file_path), os.path.getsize(file_path), 'abc.txt']
    },
]

# get http request headers
multipart = k3httpmultipart.Multipart()
res_headers = multipart.make_headers(fields, headers=headers)

print(res_headers)

#output:
#{
#    'Content-Type': 'multipart/form-data; boundary=FormBoundaryrGKCBY7',
#    'Conetnt-Length': 1200,
#}

# get http request body reader
multipart = k3httpmultipart.Multipart()
body_reader = multipart.make_body_reader(fields)
data = []

for body in body_reader:
    data.append(body)

print(''.join(data))

#output:
#--FormBoundaryrGKCBY7
#Content-Disposition: form-data; name=aaa
#
#abcde
#--FormBoundaryrGKCBY7
#Content-Disposition: form-data; name=bbb; filename=abc.txt
#Content-Type: text/plain
#
#123456789
#--FormBoundaryrGKCBY7--

```

#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>


[pykit3]: https://github.com/pykit3
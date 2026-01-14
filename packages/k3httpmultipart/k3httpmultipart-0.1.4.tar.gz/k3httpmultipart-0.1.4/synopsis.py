import os

import k3httpmultipart
import k3fs

# http request headers
headers = {"Content-Length": 1200}

# http request fields
file_path = "/tmp/abc.txt"
k3fs.fwrite(file_path, "123456789")
fields = [
    {
        "name": "aaa",
        "value": "abcde",
    },
    {"name": "bbb", "value": [open(file_path), os.path.getsize(file_path), "abc.txt"]},
]

# get http request headers
multipart = k3httpmultipart.Multipart()
res_headers = multipart.make_headers(fields, headers=headers)

print(res_headers)

# output:
# {
#    'Content-Type': 'multipart/form-data; boundary=FormBoundaryrGKCBY7',
#    'Conetnt-Length': 1200,
# }

# get http request body reader
multipart = k3httpmultipart.Multipart()
body_reader = multipart.make_body_reader(fields)
data = []

for body in body_reader:
    data.append(body)

print("".join(data))

# output:
# --FormBoundaryrGKCBY7
# Content-Disposition: form-data; name=aaa
#
# abcde
# --FormBoundaryrGKCBY7
# Content-Disposition: form-data; name=bbb; filename=abc.txt
# Content-Type: text/plain
#
# 123456789
# --FormBoundaryrGKCBY7--

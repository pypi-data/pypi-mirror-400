# pyrri

Client library for the DENIC real-time registration interface RRI

## Install

```
pip install pyrri
```

## Quickstart

```
from rri import RRIClient


rri = RRIClient()
rri.connect("rri.denic.de", 51131)
rri.login(username, password)

answer = rri.talk(order)

rri.logout()
rri.disconnect()
```

`order` can be `k/v` or `xml` formatted.
See [Examples section in DENIC manual](https://docs.denic.de/en/Content/Beispiele/50/Overview-Beispiele.htm) for more information about what is expected.

## Interactive CLI

Show help:

```
rri --help
```

```
usage: rri.py [-h] [-s SERVER] [-u USERNAME] [-p PASSWORD] [-i INPUT] [-o OUTPUT]

RRI-Client

options:
  -h, --help            show this help message and exit
  -s, --server SERVER   Hostname and port of rri-server. or IP-address of RRI-server
                        (default: rri.denic.de:51131)
  -u, --user USERNAME   Username for RRI-server. For more security, this can also be set by
                        environment variable RRI_USERNAME (default: None)
  -p, --password PASSWORD
                        Password for RRI-server. For more security, this can also be set by
                        environment variable RRI_PASSWORD (default: None)
  -i, --input INPUT     Filename with order to send to RRI. When skipping this parameter,
                        the order is read from stdin (default: None)
  -o, --output OUTPUT   Filename in which the answer from RRI is stored. When skipping this
                        parameter, answer is written to stdout (default: None)
```

## Attribution

This project is based on the [DENIC pyrri example code](https://github.com/DENICeG/pyrri).

## License

Copyright (c) 2019 DENIC eG

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.



# SMS Demo Server

This demonstration presents three implementations of an SMS echo server
using Telnyx's SMS API. The first implementation uses the
[aiohttp](http://aiohttp.readthedocs.io/en/stable/) library; the second
uses [Flask](http://flask.pocoo.org/); and the third is built using the
standard library's HTTPServer.

## Overview

The structure of the repository is as follows.

```
.
├── bin
│   └── demoserver          <--- top level script with CLI
├── README.md
├── requirements.txt
├── setup.py
└── smsdemo
    ├── aiohttpserver       <--- aiohttp implementation
    │   └── __init__.py
    ├── constants.py        <--- shared default constants used by all three
    ├── flaskserver         <--- flask implementation
    │   └── __init__.py
    ├── httpserver          <--- http implementation
    │   ├── __init__.py
    │   └── handler.py
    ├── __init__.py
    ├── message.py          <--- simple class to manipulates HTTP content
    └── util.py             <--- shared utility functions for sending and
                                 validation message integrity
```

## Implementations

### aiohttp

This implementation is a straightforward variant of the server example
from the quick start guide
[here](http://aiohttp.readthedocs.io/en/stable/tutorial.html).

One POST route is added to the application and any blocking I/O
operations such as reading request body and sending a request are
handled asynchronously. (If you are not so familiar with asynchronous
programming, there are a number of helpful tutorials out there, such as
this [Asynchronous I/O
Walkthrough](http://www.pgbovine.net/python-async-io-walkthrough.htm).

### Flask

This is yet another straightforward implementation. The `echo()`
function is decorated with Flask's `@app.route` decorator. It only
accepts `POST` requests. The receive and echo functions in this case are
synchronous, i.e. blocking on I/O.

### HTTPServer

The python
[http.server](https://docs.python.org/3/library/http.server.html) is not
ideal for this application, for two reasons: (1) You can't easily pass
custom parameters, e.g. secret key, to the function that handles your
request. (2) You have to do all the manual parsing of the request and
en/decoding.

To solve the first problem, you need to wrap a factory function around
the class definition and return the class back to the invoking function,
as demonstrated in `smsdemo/httpserver/handler.py`. For the second
problem, you just have to be careful with classic Unicode vs bytes
distinction.

## Running a demo server

1. Clone the repository.
2. Create a virtual environment (using
   [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/)):
   ```
   user@sms-demo:~/sms-demo$ mkvirtualenv -p /usr/bin/python3 sms-demo
   ```
3. Install dependencies:
   ```
   (sms-demo) user@sms-demo:~/sms-demo$ pip install -r requirements.txt
   ```
4. Install this package under your path:
   ```
   (sms-demo) user@sms-demo:~/sms-demo$ python setup.py install
   ```
5. Choose an implementation to run:
   ```
   (sms-demo) user@sms-demo:~/sms-demo$ ./bin/demoserver
   Usage: demoserver [OPTIONS] COMMAND [ARGS]...

     Run a sample SMS echo server. The server accepts Telnyx SMS webhook
     deliveries and sends an echo of the message back to the sender.

     Please ensure that the delivery url option is set properly. Otherwise,
     signature validation will fail. The url should end with the path "/sms".

   Options:
     -h, --host TEXT     HTTP server IP.
     -p, --port INTEGER  HTTP server port.
     -s, --secret TEXT   Secret from your SMS messaging profile.  [required]
     -u, --url TEXT      Callback url from your SMS messaging profile (needed for
                         signature verification).
     --help              Show this message and exit.

   Commands:
     aiohttp  Run the aiohttp-based demo server.
     flask    Run the Flask-based demo server.
     http     Run the HTTPServer-based demo server.

   (sms-demo) user@sms-demo:~/sms-demo$ ./bin/demoserver -h 0.0.0.0 -p 8089
   -s MY-SUPER-SECRET-SECRET -u http://sms-demo.telnyx.com:8089/sms aiohttp
   ```

Please make sure that the `-u` parameter matches the URL that you set as
the "Webhook URL" for your messaging profile in the [Telnyx
Portal](https://portal.telnyx.com/). Also, ensure that you are setting
`-s` to the correct messaging profile secret.

## Miscellaneous notes

1. We recommend setting up a python virtual environment while developing
   your application, so that your native environment is preserved. You
   can find more information about virtual environments
   [here](http://python-guide.readthedocs.io/en/latest/dev/virtualenvs/).
2. Please avoid hard coding your messaging profile secret for sending
   SMS in the production environment. If your secret is ever
   compromised, be sure to generate a new one through the [Telnyx
   Portal](https://portal.telnyx.com/).
3. There are of course many other options for implementing such servers,
   e.g. by using the [Twisted
   framework](https://twistedmatrix.com/trac/). We would love to expand
   these demo servers and would welcome any contributions.

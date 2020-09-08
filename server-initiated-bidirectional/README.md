= Issue 123772 =

== Certificate ==
Generate a self-signed certificate with the files `localhost.crt` and `localhost.key`. All components in this example will use this certificate.

```
./cert-generate
```

== QuicTransport Server ==
Run a simple QuicTransport server that listens for connections on `localhost:4443`, opens a bidirectional stream, writes "ping" to it, and logs all QUIC events received.

```bash
python3 server.py
```

== QuicTransport Client ==
`client.html` is a simple client that establishes a connection to `localhost:4443`, accepts a bidirectional stream, reads all of the contents, and then write "PONG" to it. The page is blank; all output is via the console.

This will need to be hosted on `https://localhost:4444` with a web server and opened using a browser that allows the self-signed certificate:

=== Web Server ===
Use a HTTPS server to host `localhost:4444/client.html`

```bash
python3 web.py
```

=== Browser ==
Open a browser instance to `localhost:4444/client.html`. Make sure all existing Chrome instances are closed, otherwise the flags will have no effect.

```bash
FINGERPRINT=`./cert-fingerprint`
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --origin-to-force-quic-on="localhost:4443" --ignore-certificate-errors-spki-list="${FINGERPRINT}" https://localhost:4444/client.html
```

Replace above with the correct path to the version of Chrome to test.

== Results ==
=== Expected ===
Client received "ping", writes "PONG", and closes.

=== Actual ===
*Chrome 85.0.4183.102*: Full browser crash.
*Chrome Canary 87.0.4258.2*: Client resets stream, and claims the remote closed the stream.

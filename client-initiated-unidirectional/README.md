# Issue 1123766

## Certificate
Generate a self-signed certificate with the files `localhost.crt` and `localhost.key`. All components in this example will use this certificate.

```
./cert-generate
```

## QuicTransport Server
Run a simple QuicTransport server that listens for connections on `localhost:4443`, counts all bytes received, and prints the size on the first RESET or STREAM FINAL frame.

```bash
python3 server.py
```

## QuicTransport Client
`client.html` is a simple client that establishes a connection to `localhost:4443`, creates a unidirectional stream, writes 1000000 bytes to it and closes the stream. The page is blank and there is no console output.

This will need to be hosted on `https://localhost:4444` with a web server and opened using a browser that allows the self-signed certificate:

### Web Server
Use a HTTPS server to host `localhost:4444/client.html`

```bash
python3 web.py
```

### Browser
Open a browser instance to `localhost:4444/client.html`. Make sure all existing Chrome instances are closed, otherwise the flags will have no effect.

```bash
FINGERPRINT=`./cert-fingerprint`
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --origin-to-force-quic-on="localhost:4443" --ignore-certificate-errors-spki-list="${FINGERPRINT}" https://localhost:4444/client.html
```

Replace above with the correct path to the version of Chrome to test.

## Results
Keep refreshing or modify the loopback interface to get random packet loss.

### Expected
Server prints "FINAL 1000000" on every page load. This means all of the data arrived.

### Chrome 85.0.4183.102
RESET 998844
FINAL 1000000
RESET 996524
FINAL 1000000
FINAL 1000000
FINAL 1000000
FINAL 1000000
FINAL 1000000
RESET 995521
RESET 1000000
FINAL 1000000
RESET 996139

#### Chrome Canary 87.0.4258.2
RESET 996524
RESET 996838
RESET 992198
RESET 995521
FINAL 1000000
FINAL 1000000
RESET 998155
FINAL 1000000
RESET 995521
FINAL 1000000

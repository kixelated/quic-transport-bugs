# Issue 1129597

## Certificate
Generate a self-signed certificate with the files `localhost.crt` and `localhost.key`. All components in this example will use this certificate.

```
./cert-generate
```

## QuicTransport Server
Runs a simple QuicTransport server that listens for connections on `localhost:4443`, creates a unidirectional stream, sends "ping" but does not close the connection.

```bash
python3 server.py
```

## QuicTransport Client
`client.html` is a simple client that establishes a connection to `localhost:4443`, listens for a unidirectional stream, and reads/prints the contents. The page is blank and there is no console output.

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
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --origin-to-force-quic-on="localhost:4443" --ignore-certificate-errors-spki-list="`./cert-fingerprint`" https://localhost:4444/client.html
```

Replace above with the correct path to the version of Chrome to test.

## Results
### Expected
Prints "ping" and uses minimal CPU.

#### Chrome Canary 87.0.4258.2
Prints nothing and uses 100% cpu.

# Aerix Certbot Plugin

This repository provides a Certbot authenticator plugin that writes HTTP-01
challenge responses into Aerix's built-in ACME responder directory structure
(`/var/lib/aerix/<domain>/<token>`). Once the files are written, Aerix serves
them at `http://<domain>/.well-known/acme-challenge/<token>` automatically
before any other routing or redirects, allowing Certbot to complete domain
validation without manual web server configuration.

## Installation

Install the plugin into the same Python environment that runs Certbot. When
published to PyPI you can install it directly:

```bash
pip install aerix-certbot
```

If you are working from a checkout of this repository, run `pip install .`
instead to install from the local sources.

You can confirm Certbot sees the plugin with:

```bash
certbot plugins
```

## Usage

Run Certbot with the Aerix authenticator selected. The plugin writes challenge
files to `/var/lib/aerix/<domain>/<token>`, which Aerix serves automatically at
`/.well-known/acme-challenge/<token>` before routing or redirects.

Use `--aerix-debug` to log where the plugin writes and removes challenge files:

```bash
certbot certonly \
  --authenticator aerix \
  --aerix-debug \
  --agree-tos \
  -m admin@example.com \
  -d example.com
```

When running `certbot renew`, the plugin restarts the Aerix service after it
cleans up challenge files so Aerix can pick up any state changes.

Certbot writes the validation file to
`/var/lib/aerix/example.com/<token>`, which Aerix serves automatically at
`http://example.com/.well-known/acme-challenge/<token>`.

## Uninstallation

To remove the plugin from the Certbot environment:

```bash
pip uninstall aerix-certbot
```

## Notes

- The plugin only supports HTTP-01 challenges.
- Certbot must have permission to create files under `/var/lib/aerix`.

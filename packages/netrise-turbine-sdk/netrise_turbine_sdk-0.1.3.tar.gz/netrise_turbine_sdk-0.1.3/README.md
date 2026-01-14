# Turbine Python SDK

Minimal, sync-first Python client for the Turbine GraphQL API.

## Getting Started

### Installation from PyPI

Install from PyPI as `netrise-turbine-sdk`:

```bash
# pip
pip install netrise-turbine-sdk

# poetry
poetry add netrise-turbine-sdk

# uv
uv add netrise-turbine-sdk
```

### Configure environment variables

Copy the example environment variable file:

```bash
cp .env.example .env
```

The `.env` file should look similar to this example:

```bash
TURBINE_GRAPHQL_ENDPOINT=https://apollo.turbine.netrise.io/graphql/v3
AUTH0_AUDIENCE=https://prod.turbine.netrise.io/
AUTH0_DOMAIN=https://authn.turbine.netrise.io
AUTH0_CLIENT_ID=<client_secret>
AUTH0_CLIENT_SECRET=<client_id>
AUTH0_ORGANIZATION_ID=<org_id>
AUTH0_ORGANIZATION_NAME=<org_name>
```

Populate the missing values. Reach out to [mailto:support@netrise.io](support@netrise.io) if you need assistance.

## License

See [LICENSE](https://github.com/NetRiseInc/Python-Turbine-SDK/blob/main/LICENSE) for details.

## Documentation

- [API Documentation & Code Samples](https://github.com/NetRiseInc/Python-Turbine-SDK/blob/main/docs/README.md) - detailed examples for all client SDK operations.

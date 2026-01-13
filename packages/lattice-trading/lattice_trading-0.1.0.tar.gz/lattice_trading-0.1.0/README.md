# Lattice Python SDK
A Python client for the Lattice Prediction Market API.

## Install
```bash
pip install lattice-trading
```

## Quickstart
```python
from lattice import LatticeClient
from lattice.api.markets import get_api_v1_markets

client = LatticeClient(
    tenant_id="tenant-id",
    api_key="lat_example",
)

markets = client.call(get_api_v1_markets.sync_detailed, limit=25, offset=0)
print(markets.markets)
```

To point at staging, override `base_url`:
```python
client = LatticeClient(
    base_url="https://staging-api.lattice.market",
    tenant_id="tenant-id",
    api_key="lat_example",
)
```

## Async usage
```python
from lattice import AsyncLatticeClient
from lattice.api.orders import post_api_v1_orders

client = AsyncLatticeClient(
    tenant_id="tenant-id",
    api_key="lat_example",
)

order = await client.call_async(
    post_api_v1_orders.asyncio_detailed,
    market_id="market-id",
    outcome_id="outcome-id",
    side="buy",
    type="limit",
    price=55,
    quantity=10,
    idempotency_key="order-001",
)
print(order.id)
```

## Validation and logging
The SDK validates request parameters against type hints before sending requests.
```python
import logging
from lattice import LatticeClient
from lattice.api.markets import get_api_v1_markets

logger = logging.getLogger("lattice")
client = LatticeClient(
    tenant_id="tenant-id",
    api_key="lat_example",
    logger=logger,
)

client.call(get_api_v1_markets.sync_detailed, limit=10, offset=0)
```

Disable validation if you need to bypass strict checks:
```python
client = LatticeClient(
    tenant_id="tenant-id",
    api_key="lat_example",
    validate=False,
)
```

## Pagination helpers
```python
from lattice.pagination import paginate_offset
from lattice.api.orders import get_api_v1_orders

client = LatticeClient(tenant_id="tenant-id", api_key="lat_example")

def fetch_page(limit: int, offset: int):
    response = client.call(get_api_v1_orders.sync_detailed, limit=limit, offset=offset)
    return response.orders, response.limit, response.offset, response.total

for order in paginate_offset(fetch_page, limit=50):
    print(order.id)
```

## Notes
- Generated endpoint modules live in `lattice.api.*`.
- `x_tenant_id` is injected automatically by `LatticeClient`.
- Use `idempotency_key` for state-changing operations.
- `price` and `amount` values are integers in cents.
 - See `docs/getting-started.md` and `docs/api-reference.md` for more detail.

## Advanced customization
You can still use the generated `Client` and `AuthenticatedClient` directly for full control over `httpx` settings.

```python
from lattice import Client

def log_request(request):
    print(f"Request event hook: {request.method} {request.url} - Waiting for response")

def log_response(response):
    request = response.request
    print(f"Response event hook: {request.method} {request.url} - Status {response.status_code}")

client = Client(
    base_url="https://api.lattice.market",
    httpx_args={"event_hooks": {"request": [log_request], "response": [log_response]}},
)

# Or get the underlying httpx client to modify directly with client.get_httpx_client() or client.get_async_httpx_client()
```

You can even set the httpx client directly, but beware that this will override any existing settings (e.g., base_url):

```python
import httpx
from lattice import Client

client = Client(
    base_url="https://api.lattice.market",
)
# Note that base_url needs to be re-set, as would any shared cookies, headers, etc.
client.set_httpx_client(httpx.Client(base_url="https://api.lattice.market", proxies="http://localhost:8030"))
```

## Building / publishing this package
This project uses [Poetry](https://python-poetry.org/) to manage dependencies and packaging. Here are the basics:
1. Update the metadata in pyproject.toml (e.g. authors, version)
1. If you're using a private repository, configure it with Poetry
    1. `poetry config repositories.<your-repository-name> <url-to-your-repository>`
    1. `poetry config http-basic.<your-repository-name> <username> <password>`
1. Publish the client with `poetry publish --build -r <your-repository-name>` or, if for public PyPI, just `poetry publish --build`

If you want to install this client into another project without publishing it (e.g. for development) then:
1. If that project is using Poetry, you can simply do `poetry add <path-to-this-client>` from that project
1. If that project is not using Poetry:
    1. Build a wheel with `poetry build -f wheel`
    1. Install that wheel from the other project `pip install <path-to-wheel>`

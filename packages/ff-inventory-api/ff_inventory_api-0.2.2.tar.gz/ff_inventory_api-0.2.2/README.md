# ff-inventory-api

Unofficial Python client for the FF-Inventory web app.

## Features

- Session handling and login (CSRF extraction)
- Read organizational lists, create/delete lists, add/remove items
- Parse inspection basket and upcoming inspections
- Scrape users overview

## Installation

```bash
pip install ff-inventory-api
```

## Usage

```python
from ff_inventory_api import FFInventoryAPI, OrganizationalList

api = FFInventoryAPI()
api.login("user@example.com", "password")

# Lists
lists = api.get_organisational_lists()
if lists:
    first = lists[0]
    print(first.id, first.title)

# Basket
basket = api.get_basket()
print(basket)
```

## Development

- Python >= 3.10
- Install deps:

```bash
pip install -r requirements.txt -r requirements-test.txt
```

- Run tests:

```bash
pytest -q
```

## License

MIT

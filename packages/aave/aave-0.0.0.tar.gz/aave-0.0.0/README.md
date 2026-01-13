# Overview

Ape-based SDK for working with deployments of the Aave family of protocols

## Dependencies

- [python](https://python.org/downloads) v3.10+, python3-dev
- [Ape](https://docs.apeworx.io/ape/stable/userguides/overview#installation) v0.8+

## Installation

### via `pip`

You can install the latest release via [`pip`](https://pypi.org/project/pip):

```sh
pip install aave
```

### via `uv`

You can install the latest release via [`uv`](https://docs.astral.sh/uv):

```sh
uv pip install aave
```

## Quick Usage

### Scripting

The SDK can be used for any scripting task:

```python
>>> from aave import Aave
>>> aave = Aave()
>>> market = Aave.all_markets[0]
>>> pos = market.get_position(<acct>)
>>> pos.ltv
Decimal('0.56')
>>> pos.health_factor
Decimal('1.48')
>>> pos.repay("<TOKEN>", amount="100 TOKEN", sender=me)
```

### CLI

TBD

### Silverback

TBD

## Development

This project is in development and should be considered a beta.
Things might not be in their final state and breaking changes may occur.
Comments, questions, criticisms and pull requests are welcomed.

### Support

Support for different parts of the Aave protocols:

- [ ] V1 (deprecated)
- [ ] V2 (deprecated)
- [x] V3 (actively used)
- [ ] V4 (protocol unreleased)
- [ ] Aave staking

## License

This project is licensed under [Apache 2.0](./LICENSE).

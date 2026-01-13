# django-amiqus

> ⚠️ **NOTICE** ⚠️
>
> This package is scheduled to be moved to a private repository soon. Please do not rely on this
> public version for new projects.

Django app for integration with the Amiqus API.

The current version supports Django 5.2-6.0 and Python 3.12+.

## Background

Amiqus is an online identity verification service. We use this library to integrate with it.

## Amiqus workflow

Core entities included in this app are `Client`, `Record`, `Step`, `Check`, `Form`, and `Review`

### `Client`

Represents a person against whom you wish to carry out an identity or background check. They are
unique within Amiqus, although it is possible to carry out multiple checks over a period of time
against one user.

### `Record`

A collection of `Steps` that a `Client` is required to complete. The `Client` receives a link where
they are presented with the various `Steps`.

### `Step`

Can be either a `Check` or a `Form`. The Amiqus platform does support `Document` type `Steps`, but
these are not currently supported by this package.

### `Check`

May each be of the types described in `Check.CheckType`. This includes things like photo ID
verification and watchlist monitoring.

### `Form`

Defined in the Amiqus platform and consists of one or more questions that the `Client` must answer.

### `Review`

Each `Step` may be reviewed in the Amiqus interface. This creates a `Review` object that can be
queried via the API .

## Installation

The project is available through PyPI as `django-amiqus`:

```bash
$ pip install django-amiqus
```

## Tests

If you want to run the tests manually, install `poetry`.

```bash
$ poetry install
$ poetry run pytest
```

If you are hacking on the project, please keep coverage up.

## Contributing

Standard GH rules apply: clone the repo to your own account, make sure you update the tests, and
submit a pull request.

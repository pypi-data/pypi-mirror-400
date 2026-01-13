<img src="https://cdn.startinblox.com/tems/cofund.png" width="300" />

# DjangoLDP TEMS

[![pypi](https://img.shields.io/pypi/v/djangoldp-tems)](https://pypi.org/project/djangoldp-tems/)

## Description

`djangoldp-tems` is a DjangoLDP package providing a set of models for representing various types of TEMS objects, conforming to the Linked Data Platform (LDP) and the TEMSCore specifications. It includes models for shared entities, media objects, civil society, fact-checking, interactive infographics, stories, 3D objects, and sentiment analysis. This package is designed to be used as a component within TEMS data servers.

## Installation

This package is intended to be used as a dependency within a Django project that uses `djangoldp` and `djangoldp-account`.

### Install the package

```bash
pip install djangoldp-tems
```

### Configure your server

Add to `settings.yml`

Within your Django project's `settings.yml` file, add `djangoldp-tems` to the `dependencies` list and the wanted individual model packages to the `ldppackages` list. The order in `ldppackages` matters, so maintain the order shown below.

```yaml
dependencies:
  - djangoldp-tems

ldppackages:
  - djangoldp_mediaobject
  - djangoldp_civilsociety
  - djangoldp_factchecking
  - djangoldp_interactiveinfographic
  - djangoldp_story
  - djangoldp_object3d
  - djangoldp_sentiment
```

If you do not have a settings.yml file, you should follow the djangoldp server installation guide.

### Run migrations

```bash
./manage.py migrate
```

## Sample Data

A sample fixture is provided to demonstrate the structure and relationships of the models.

To load the sample data:

```bash
./manage.py loaddata tems-shared
./manage.py generate_mock_data
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

# Zou Karaoke

## Installation

```shell
poetry install
```

## Start

```shell
poetry run start
```

## Trouble Fixing

### Video can't be played

If you encounter following issue and video can't be played.

```text
DirectShowPlayerService::doRender: Unresolved error code 0x80040266 (IDispatch error #102)
```

Please download the [filters](https://github.com/Nevcairiel/LAVFilters/releases) and install them.

> When you want to install the filters `install_*.bat`, please use admin to install.

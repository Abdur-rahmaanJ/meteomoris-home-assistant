# meteomoris-home-assistant

## Quick install

```
cd config/custom_components
git clone https://github.com/Abdur-rahmaanJ/meteomoris-home-assistant
```

in configuration.yaml

```
sensor:
  - platform: meteomoris
    name: "Mauritius"
    scan_interval: 1800 
```

## Development

Python3.13 create and activate venv

```
python3.13 -m venv venv
. venv/bin/activate
pip install homeassistant meteomoris
mkdir config
mkdir config/custom_components
hass --config config
```

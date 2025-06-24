# nearport

Real-time flight tracker that:

- Pulls live ADS-B feeds (default: flights near OGG)
- Detects takeoffs, landings & which runway is in use
- Resolves ICAO24 addresses & callsigns to friendly names

## Setup

This project uses [uv](https://github.com/astral-sh/uv) for dependency management and task running. You can install it from [here](https://docs.astral.sh/uv/getting-started/installation/#installing-uv)

Once you have `uv` installed, pull the required dependencies and set up your environment:

```bash
uv install
```

Create a `.env` file in the root directory with your desired configuration. You can use the provided `.env.example` as a template.

```bash
cp .env.example .env
```

To modify the ICAO and Callsign resolution, you can place fields within the `known_adsb_icao.json` to resolve ICAO24 addresses and callsigns to friendly names. This file is used to map the raw ADS-B data to more human-readable identifiers, like individual names for an aircraft.


Finally, run the application:

```bash
uv run main.py
```

By default, you’ll see live traffic logged in your console around Kahului (OGG); tweak your lat/lon/radius or add more airports in `.env` or a custom config file.

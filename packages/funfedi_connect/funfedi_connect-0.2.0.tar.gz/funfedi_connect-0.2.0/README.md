# funfedi_connect

FunFedi connect represents an unified query and verify code
for the Fediverse applications provided on 
[containers.funfedi.dev](https://containers.funfedi.dev/).

## Development

One can run the unit tests via

```bash
uv run pytest
```

### Behave

Start the container with

```bash
docker compose up --wait
docker compose exec pasture-one-actor /bin/sh
```

then run the behave tests with

```bash
FEDI_APP=name behave
```

the app `name` must be running from the funfedi.dev containers.

# funfedi_results

The goal of this package is to manage the results generated
by the [funfedi.dev](https://funfedi.dev) tooling.


## Usage


```
uv run python -mfunfedi_results download --as_allure_results
```

then

```
docker run --rm -ti -v .:/work helgekr/allure allure awesome allure-results
python -mhttp.server -dallure-report
```

## Development

Run

```bash
uv run pytest
```

to run tests
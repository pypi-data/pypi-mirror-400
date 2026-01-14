# limr

This is the Late-Inspiral Merger Ringdown (LIMR) model. It is a non-parametric non-spinning higher multipole model for the gravitational waves emitted from merging black holes.

## Installation

TODO

## Documentation

TODO

code that fit the models lives [here](https://gitlab.com/SpaceTimeKhantinuum/ml/-/tree/master/waveforms/p(h)enom-non-spinning/dev-examples/merger_only/nr-catalogue/initial_modelling/model-using-calibration-set)

## Development

### Publish

`uv` commands like `build`, `build --clear`, `version X.Y.Z`

and publish to pypi with

```bash
$ uv publish --username __token__
```


### Run an example

```bash
uv run --with gw-limr --no-project -- python examples/limr_example.py
```





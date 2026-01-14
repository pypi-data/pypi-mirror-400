# Light Mastodon Reader for Python

This is a lighter version of [Mastodon Reader for Python](https://github.com/mastodon-sc/python-mastodon-importer) from [Chrisoph Sommer](https://github.com/sommerc).

Import the *spots and links tables*, *features*, *tags* and meta data from a *Mastodon project file*.

Ported to Python from: [matlab-mastodon-importer](https://github.com/mastodon-sc/matlab-mastodon-importer)

This reader is lighter mainly because it does not depend on `pandas` nor on `networkx` and it therefore only depends on `numpy`.

## Example

Read the mastodon file:

```python
from micromastodonreader import MicroMastodonReader

mr = MicroMastodonReader("demo/demo.mastodon")

# show meta data
meta_data = mr.read_metadata()

# read spot and link tables with features and tags columns
spots, links, tag_definition, features = mr.read(tags=True, features=True)
```

`spots` is a `numpy.ndarray` where:

- `spots[int_id]` is the cell with id `int_id`
- `spots[int_id, 0]` is the `x` coordinate of the cell `int_id`
- `spots[int_id, 1]` is the `y` coordinate of the cell `int_id`
- `spots[int_id, 2]` is the `z` coordinate of the cell `int_id`
- `spots[int_id, 3]` is the time of the cell `int_id`
- `spots[int_id, 3:10]` are the values of the elongation matrix representing the cell `int_id` sphere
- `spots[int_id, 10]` is the `bsrs` (??) of `int_id`

`links` is a `numpy.ndarray` where:

- `links[int_pos]` is an edge
- `links[int_pos, 2]` is the id of the edge
- `links[int_pos, 0]` is the id of the cell at time `t`
- `links[int_pos, 1]` is the id of the cell at time `t + 1`

`tag_definition` and `features` are a bit more complicated 🫠

You can also read information separately

```python
# read only spot and link tables
spots, links = mr.read_tables()

# read tag_definition
tag_definition = mr.read_tags()

# read features
mr.read_features()
```

## Installation

### Current version

`pip install git+git://github.com/GuignardLab/python-mastodon-importer-light`

### pip

`pip install micro-mastodon-reader`

more information [on PyPi](https://pypi.org/project/micro-mastodon-reader/)

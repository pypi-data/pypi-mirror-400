# haematite

Runtime support for [Haematite](https://github.com/tomWhiting/haematite) notebooks.

## Installation

```bash
pip install haematite
```

## Usage

Export values from your notebook cells:

```python
import haematite as hm

# Export a specific value
data = [1, 2, 3, 4, 5]
hm.export("my_data", data)

# Take a snapshot of all local variables
hm.snapshot("checkpoint")
```

Exported values are automatically captured and can be used in subsequent cells or visualizations.

## API

### `hm.export(name: str, value: Any) -> None`

Export a named value. The value is captured at the point of the call, preserving its state at that moment.

### `hm.snapshot(label: str, filter: Optional[List[str]] = None) -> None`

Capture all local variables at the current point. Optionally filter to specific variable names.

## License

MIT

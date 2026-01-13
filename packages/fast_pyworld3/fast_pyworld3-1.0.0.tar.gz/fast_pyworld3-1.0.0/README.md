# fast_pyworld3

A high-performance Python implementation of the World3 model from "Limits to Growth: The 30-Year Update" (2004). Resolves circular dependency issues for faster simulation.

## Installation

```bash
pip install fast_pyworld3
```

## Usage

```python
from fast_pyworld3 import World3

world3 = World3()
world3.run()
results = world3.get_results()
```

```python
from fast_pyworld3.core import World3, World3Config
config = World3Config(year_max=2050, dt=0.25)
world3 = World3(config)
world3.init_constants(nri=1.5e12)  # custom
world3.init_variables()
world3.set_table_functions()
world3.set_delay_functions()
world3.run()

```


## Simulation Sectors

- Population
- Capital (Industrial/Service)
- Agriculture
- Pollution (Persistent)
- Resources (Nonrenewable)

## Benchmark

**20x faster** than PyWorld3-03 with identical results.

| Metric  | PyWorld3-03 | fast_pyworld3 |
| ------- | ----------- | ------------- |
| Mean    | 1903.91 ms  | 94.24 ms      |
| Speedup | -           | **20.20x**    |

### Validation

| Variable          | Correlation | Mean Rel Err | Max Rel Err |
| ----------------- | ----------- | ------------ | ----------- |
| Total Population  | 1.000000    | 0.0000%      | 0.0000%     |
| Industrial Output | 1.000000    | 0.0000%      | 0.0000%     |
| Food Per Capita   | 1.000000    | 0.0000%      | 0.0000%     |
| Pollution Index   | 1.000000    | 0.0000%      | 0.0000%     |
| Natural Resources | 1.000000    | 0.0000%      | 0.0000%     |

### Time Step Scaling

| dt    | Steps | PyWorld3-03 | fast_pyworld3 | Speedup |
| ----- | ----- | ----------- | ------------- | ------- |
| 1.000 | 201   | 978.25 ms   | 50.67 ms      | 19.31x  |
| 0.500 | 401   | 1915.30 ms  | 92.16 ms      | 20.78x  |
| 0.250 | 801   | 3840.44 ms  | 190.58 ms     | 20.15x  |
| 0.125 | 1601  | 7794.03 ms  | 381.27 ms     | 20.44x  |

## Requirements

- Python >= 3.13
- numpy, scipy, matplotlib

## License

CeCILL v2.1

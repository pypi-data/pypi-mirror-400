# PhysAnim

PhysAnim is a Python library designed to make physics simulations and animations effortless.

## Installation

```bash
pip install .
```

## Usage

```python
import physanim
from physanim.systems import DoublePendulum

# Create a customized double pendulum
pendulum = DoublePendulum(L1=1.0, L2=1.0, m1=1.0, m2=1.0)

# Animate it!
physanim.animate(pendulum)
```

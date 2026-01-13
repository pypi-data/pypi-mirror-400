# table-rl
This repository contains a set of implementations and functionality of purely online tabular reinforcement learning algorithms.

Currently we support Python 3.8.

## Installation

You should be able to install `table-rl` from PyPi.

```
pip3 install table-rl
```

You can also install `table-rl` from source.

```
git clone https://github.com/prabhatnagarajan/table-rl.git
cd table-rl
pip3 install -e .
```

## How the library works
Reward functions, value functions, transition functions are all `numpy` arrays and matrices. We follow the conventions from Sutton and Barto's [RL Book](http://incompleteideas.net/book/RLbook2020.pdf). 

We focus only on online algorithms that interact with and get experience from the environment in a purely online way.
## Contributing

Use `pytest` on the test directories.

```
python -m pytest tests/
```


## License

[MIT License](LICENSE).


from itertools import pairwise
from typing import Sequence

from chex import Array
from flax import nnx


class MLP(nnx.Module):
    def __init__(
        self,
        layer_sizes: Sequence[int],
        activation=nnx.relu,
        use_bias: bool = True,
        *,
        rngs: nnx.Rngs
    ):
        self.layers = [
            nnx.Linear(in_features, out_features, use_bias=use_bias, rngs=rngs)
            for (in_features, out_features) in pairwise(layer_sizes)
        ]

        self.activation = activation

    def __call__(self, x: Array) -> Array:
        x = x.reshape((x.shape[0], -1))  # flatten if not already
        for layer in self.layers[:-1]:
            x = self.activation(layer(x))
        x = self.layers[-1](x)
        return x

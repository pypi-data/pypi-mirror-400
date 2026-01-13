from itertools import pairwise
from typing import Sequence

from flax import nnx
from flax.typing import PaddingLike


class CNN(nnx.Module):
    def __init__(
        self,
        num_channels: Sequence[int],
        kernel_sizes: Sequence[int | Sequence[int]],
        embedding_dim: int,
        num_classes: int,
        use_bias: bool = True,
        padding: PaddingLike = "SAME",
        strides: int | Sequence[int] | None = 1,
        activation=nnx.relu,
        *,
        rngs: nnx.Rngs,
    ):
        if len(kernel_sizes) == 1:
            kernel_sizes = kernel_sizes * len(num_channels)
        if len(num_channels) != len(kernel_sizes):
            raise ValueError(
                f"Number of channels = {len(num_channels)} != {len(kernel_sizes)}"
                " = number of kernel sizes."
            )

        self.layers = [
            nnx.Conv(
                in_features=inc,
                out_features=outc,
                kernel_size=k,
                strides=strides,
                padding=padding,
                use_bias=use_bias,
                rngs=rngs,
            )
            for (inc, outc), k in zip(pairwise(num_channels), kernel_sizes)
        ]

        self.activation = activation

        self.fc1 = nnx.Linear(num_channels[-1], embedding_dim, rngs=rngs)
        self.fc2 = nnx.Linear(embedding_dim, num_classes, rngs=rngs)

    def __call__(self, x):
        for layer in self.layers:
            x = self.activation(layer(x))
            x = nnx.max_pool(x, window_shape=layer.kernel_size, padding="SAME")

        x = nnx.avg_pool(x, (x.shape[1], x.shape[2]))
        x = x.reshape((x.shape[0], -1))
        x = self.activation(self.fc1(x))
        x = self.fc2(x)
        return x

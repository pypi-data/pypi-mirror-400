# adapted from:
# https://uvadlc-notebooks.readthedocs.io/en/latest/tutorial_notebooks/JAX/tutorial5/Inception_ResNet_DenseNet.html#DenseNet

from collections.abc import Callable

import jax.numpy as jnp
from chex import Array
from flax import nnx

dense_kernel_init = nnx.initializers.kaiming_normal()


class DenseLayer(nnx.Module):
    def __init__(
        self,
        num_channels: int,
        bottleneck_size: int,
        growth_rate: int,
        activation: Callable[[Array], Array],
        *,
        rngs: nnx.Rngs,
    ):
        super().__init__()
        self.bottleneck_size = bottleneck_size
        self.growth_rate = growth_rate
        self.activation = activation

        self.bn1 = nnx.BatchNorm(num_channels, rngs=rngs)
        self.conv1 = nnx.Conv(
            num_channels,
            self.bottleneck_size * self.growth_rate,
            kernel_size=(1, 1),
            kernel_init=dense_kernel_init,
            use_bias=False,
            rngs=rngs,
        )
        self.bn2 = nnx.BatchNorm(self.bottleneck_size * self.growth_rate, rngs=rngs)
        self.conv2 = nnx.Conv(
            self.bottleneck_size * self.growth_rate,
            self.growth_rate,
            kernel_size=(3, 3),
            kernel_init=dense_kernel_init,
            use_bias=False,
            rngs=rngs,
        )

    def __call__(self, x):
        z = self.bn1(x)
        z = self.activation(z)
        z = self.conv1(z)

        z = self.bn2(z)
        z = self.activation(z)
        z = self.conv2(z)

        z = jnp.concatenate((x, z), axis=-1)
        return z


class DenseBlock(nnx.Module):
    def __init__(
        self,
        num_layers: int,
        num_channels: int,
        bottleneck_size: int,
        growth_rate: int,
        activation: Callable[[Array], Array],
        *,
        rngs: nnx.Rngs,
    ):
        super().__init__()
        nc = num_channels
        self.layers = []
        for _ in range(num_layers):
            self.layers.append(
                DenseLayer(nc, bottleneck_size, growth_rate, activation, rngs=rngs)
            )
            nc += growth_rate

    def __call__(self, x):
        for layer in self.layers:
            x = layer(x)
        return x


class Transition(nnx.Module):
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        activation: Callable[[Array], Array],
        *,
        rngs: nnx.Rngs,
    ):
        super().__init__()
        self.bn = nnx.BatchNorm(in_channels, rngs=rngs)
        self.conv = nnx.Conv(
            in_channels,
            out_channels,
            kernel_size=(1, 1),
            kernel_init=dense_kernel_init,
            use_bias=False,
            rngs=rngs,
        )
        self.activation = activation

    def __call__(self, x):
        x = self.bn(x)
        x = self.activation(x)
        x = self.conv(x)
        x = nnx.avg_pool(x, (2, 2), strides=(2, 2))
        return x


class DenseNet(nnx.Module):
    def __init__(
        self,
        num_layers: list[int],
        num_channels: int,
        bottleneck_size: int,
        growth_rate: int,
        num_classes: int,
        activation: Callable[[Array], Array],
        *,
        rngs: nnx.Rngs,
    ):
        super().__init__()
        self.num_layers = num_layers
        self.bottleneck_size = bottleneck_size
        self.growth_rate = growth_rate
        self.num_classes = num_classes
        self.activation = activation

        hidden_channels = self.growth_rate * self.num_layers[0]
        self.conv = nnx.Conv(
            num_channels,
            hidden_channels,
            kernel_size=(3, 3),
            kernel_init=dense_kernel_init,
            rngs=rngs,
        )

        self.layers = []
        for i, n in enumerate(self.num_layers):
            self.layers.append(
                DenseBlock(
                    n,
                    hidden_channels,
                    self.bottleneck_size,
                    self.growth_rate,
                    self.activation,
                    rngs=rngs,
                )
            )
            hidden_channels += n * self.growth_rate

            if i < len(self.num_layers) - 1:
                self.layers.append(
                    Transition(
                        hidden_channels,
                        hidden_channels // 2,
                        self.activation,
                        rngs=rngs,
                    )
                )
                hidden_channels = hidden_channels // 2

        self.bn = nnx.BatchNorm(hidden_channels, rngs=rngs)
        self.linear = nnx.Linear(hidden_channels, num_classes, rngs=rngs)

    def __call__(self, x):
        x = self.conv(x)
        for layer in self.layers:
            x = layer(x)
        x = self.bn(x)
        x = self.activation(x)
        x = nnx.avg_pool(x, (x.shape[1], x.shape[2]))
        x = x.reshape((x.shape[0], -1))
        x = self.linear(x)
        return x

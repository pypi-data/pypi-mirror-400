# adapted from:
# https://github.com/tomgoldstein/loss-landscape/blob/master/cifar10/models/vgg.py

from functools import partial
from itertools import pairwise

from flax import nnx


class VGG(nnx.Module):
    def __init__(
        self,
        num_channels: int,
        num_filters: list[list[int]],
        num_classes: int,
        rngs: nnx.Rngs,
    ):
        super().__init__()
        self.num_layers = num_filters
        self.num_channels = num_channels
        self.out_channels = num_filters[-1][-1]
        self.rngs = rngs
        layers = [self._make_layer(num_channels, self.num_layers[0])]
        for nl1, nl2 in pairwise(self.num_layers):
            layers.append(self._make_layer(nl1[-1], nl2))

        self.feature_extractors = nnx.Sequential(*layers)

        self.fc = nnx.Sequential(
            *[
                nnx.Linear(self.out_channels, self.out_channels, rngs=self.rngs),
                nnx.BatchNorm(self.out_channels, rngs=self.rngs),
                nnx.relu,
            ]
        )

        self.classifier = nnx.Linear(self.out_channels, num_classes, rngs=self.rngs)

    def _make_layer(self, in_channels: int, num_filters: list[int]):
        layers = []
        channels = in_channels
        for v in num_filters:
            layers.append(
                nnx.Conv(
                    channels, v, kernel_size=(2, 2), padding=(1, 1), rngs=self.rngs
                )
            )
            layers.append(nnx.BatchNorm(v, rngs=self.rngs))
            layers.append(nnx.relu)
            channels = v
        layers.append(partial(nnx.max_pool, window_shape=(2, 2), strides=(2, 2)))

        return nnx.Sequential(*layers)

    def __call__(self, x):
        x = self.feature_extractors(x)
        x = nnx.avg_pool(x, (x.shape[1], x.shape[2]))
        x = x.reshape((x.shape[0], -1))
        x = self.fc(x)
        x = self.classifier(x)
        return x


def vgg9(*, num_channels: int = 3, num_classes: int = 10, rngs: nnx.Rngs):
    return VGG(
        num_channels, [[64, 64], [128, 128], [256, 256, 256]], num_classes, rngs=rngs
    )


def vgg16(*, num_channels: int = 3, num_classes: int = 10, rngs: nnx.Rngs):
    return VGG(
        num_channels,
        [[64, 64], [128, 128], [256, 256, 256], [512, 512, 512], [512, 512, 512]],
        num_classes,
        rngs=rngs,
    )


def vgg19(*, num_channels: int = 3, num_classes: int = 10, rngs: nnx.Rngs):
    return VGG(
        num_channels,
        [
            [64, 64],
            [128, 128],
            [256, 256, 256, 256],
            [512, 512, 512, 512],
            [512, 512, 512, 512],
        ],
        num_classes,
        rngs=rngs,
    )

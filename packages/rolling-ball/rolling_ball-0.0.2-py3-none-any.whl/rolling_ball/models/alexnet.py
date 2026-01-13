from chex import Array
from flax import nnx


class AlexNet(nnx.Module):
    def __init__(
        self,
        num_classes: int,
        dropout_rate: float = 0.5,
        *,
        rngs: nnx.Rngs,
    ):
        super().__init__()
        self.feature_extractor = nnx.Sequential(
            nnx.Conv(
                3, 64, kernel_size=(4, 4), strides=(2, 2), padding=(2, 2), rngs=rngs
            ),
            nnx.relu,
            lambda x: nnx.max_pool(x, (3, 3), strides=(2, 2)),
            nnx.Conv(64, 192, kernel_size=(5, 5), padding=(2, 2), rngs=rngs),
            nnx.relu,
            lambda x: nnx.max_pool(x, (3, 3), strides=(2, 2)),
            nnx.Conv(192, 384, kernel_size=(3, 3), padding=(1, 1), rngs=rngs),
            nnx.relu,
            nnx.Conv(384, 256, kernel_size=(3, 3), padding=(1, 1), rngs=rngs),
            nnx.relu,
            nnx.Conv(256, 256, kernel_size=(3, 3), padding=(1, 1), rngs=rngs),
            nnx.relu,
            lambda x: nnx.max_pool(x, (3, 3), strides=(2, 2)),
        )

        self.classifier = nnx.Sequential(
            nnx.Dropout(dropout_rate, rngs=rngs),
            nnx.Linear(256, 4096, rngs=rngs),
            nnx.relu,
            nnx.Dropout(dropout_rate, rngs=rngs),
            nnx.Linear(4096, 4096, rngs=rngs),
            nnx.relu,
            nnx.Linear(4096, num_classes, rngs=rngs),
        )

    def __call__(self, x: Array) -> Array:
        x = self.feature_extractor(x)
        x = nnx.avg_pool(x, (x.shape[1], x.shape[2]))
        x = x.reshape((x.shape[0], -1))
        x = self.classifier(x)
        return x

from flax import nnx


class LeNet(nnx.Module):
    def __init__(self, in_channels: int, rngs: nnx.Rngs):
        super().__init__()
        self.conv1 = nnx.Conv(
            in_channels,
            6,
            kernel_size=(5, 5),
            padding="SAME",
            rngs=rngs,
        )
        self.conv2 = nnx.Conv(
            6,
            16,
            kernel_size=(5, 5),
            strides=(1, 1),
            padding="VALID",
            rngs=rngs,
        )
        self.fc1 = nnx.Linear(16, 120, rngs=rngs)
        self.fc2 = nnx.Linear(120, 84, rngs=rngs)
        self.fc3 = nnx.Linear(84, 10, rngs=rngs)

    def __call__(self, x):
        x = nnx.relu(self.conv1(x))
        x = nnx.avg_pool(x, (2, 2), strides=(2, 2))
        x = nnx.relu(self.conv2(x))
        x = nnx.avg_pool(x, (2, 2), strides=(2, 2))
        x = nnx.avg_pool(x, (x.shape[1], x.shape[2]))
        x = x.reshape((x.shape[0], -1))
        x = nnx.relu(self.fc1(x))
        x = nnx.relu(self.fc2(x))
        x = self.fc3(x)
        return x

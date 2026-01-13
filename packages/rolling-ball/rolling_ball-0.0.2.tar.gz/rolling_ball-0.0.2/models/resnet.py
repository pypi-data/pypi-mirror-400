# adapted from: https://docs.jaxstack.ai/en/latest/JAX_for_PyTorch_users.html
# and: https://github.com/pytorch/vision/blob/main/torchvision/models/resnet.py

from chex import Array
from flax import nnx


class BasicBlock(nnx.Module):
    expansion = 1

    def __init__(
        self,
        in_planes: int,
        planes: int,
        stride: int = 1,
        *,
        use_bias: bool = False,
        use_residual: bool = True,
        use_batch_norm: bool = True,
        rngs: nnx.Rngs,
    ):
        self.use_residual = use_residual
        self.conv1 = nnx.Conv(
            in_planes,
            planes,
            kernel_size=(3, 3),
            strides=(stride, stride),
            padding=1,
            use_bias=use_bias,
            rngs=rngs,
        )
        self.bn1 = (
            nnx.BatchNorm(planes, momentum=0.9, epsilon=1e-5, rngs=rngs)
            if use_batch_norm
            else lambda x: x
        )

        self.conv2 = nnx.Conv(
            planes,
            planes,
            kernel_size=(3, 3),
            strides=(1, 1),
            padding=1,
            use_bias=use_bias,
            rngs=rngs,
        )
        self.bn2 = (
            nnx.BatchNorm(planes, momentum=0.9, epsilon=1e-5, rngs=rngs)
            if use_batch_norm
            else lambda x: x
        )

        if stride != 1 or in_planes != planes:
            self.downsample = nnx.Sequential(
                nnx.Conv(
                    in_planes,
                    planes,
                    kernel_size=(1, 1),
                    strides=(stride, stride),
                    padding="VALID",
                    use_bias=use_bias,
                    rngs=rngs,
                ),
                nnx.BatchNorm(planes, momentum=0.9, epsilon=1e-5, rngs=rngs),
            )
        else:
            self.downsample = None

    def __call__(self, x: Array) -> Array:
        identity = x

        out = nnx.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))

        if self.downsample:
            identity = self.downsample(x)
        if self.use_residual:
            out += identity
        out = nnx.relu(out)
        return out


class Bottleneck(nnx.Module):
    expansion = 4

    def __init__(
        self,
        in_planes: int,
        planes: int,
        stride: int = 1,
        *,
        use_bias: bool = False,
        use_batch_norm: bool = True,
        use_residual: bool = True,
        rngs: nnx.Rngs,
    ):
        width = planes
        self.use_residual = use_residual
        self.conv1 = nnx.Conv(
            in_planes,
            width,
            kernel_size=(1, 1),
            strides=(1, 1),
            padding="VALID",
            use_bias=use_bias,
            rngs=rngs,
        )
        self.bn1 = (
            nnx.BatchNorm(width, momentum=0.9, epsilon=1e-5, rngs=rngs)
            if use_batch_norm
            else lambda x: x
        )

        self.conv2 = nnx.Conv(
            width,
            width,
            kernel_size=(3, 3),
            strides=(stride, stride),
            padding="SAME",
            use_bias=use_bias,
            rngs=rngs,
        )
        self.bn2 = (
            nnx.BatchNorm(width, momentum=0.9, epsilon=1e-5, rngs=rngs)
            if use_batch_norm
            else lambda x: x
        )

        self.conv3 = nnx.Conv(
            width,
            planes * self.expansion,
            kernel_size=(1, 1),
            strides=(1, 1),
            padding="VALID",
            use_bias=use_bias,
            rngs=rngs,
        )
        self.bn3 = (
            nnx.BatchNorm(
                planes * self.expansion, momentum=0.9, epsilon=1e-5, rngs=rngs
            )
            if use_batch_norm
            else lambda x: x
        )

        if stride != 1 or in_planes != planes * self.expansion:
            self.downsample = nnx.Sequential(
                nnx.Conv(
                    in_planes,
                    planes * self.expansion,
                    kernel_size=(1, 1),
                    strides=(stride, stride),
                    padding="VALID",
                    use_bias=use_bias,
                    rngs=rngs,
                ),
                nnx.BatchNorm(
                    planes * self.expansion, momentum=0.9, epsilon=1e-5, rngs=rngs
                ),
            )
        else:
            self.downsample = None

    def __call__(self, x: Array) -> Array:
        identity = x

        out = nnx.relu(self.bn1(self.conv1(x)))
        out = nnx.relu(self.bn2(self.conv2(out)))
        out = self.bn3(self.conv3(out))

        if self.downsample:
            identity = self.downsample(x)

        if self.use_residual:
            out += identity
        out = nnx.relu(out)
        return out


class ResNet(nnx.Module):
    def __init__(
        self,
        block_cls: type[nnx.Module],
        layers: list[int],
        num_classes: int = 1000,
        num_channels: int = 3,
        *,
        use_bias: bool = False,
        use_batch_norm: bool = True,
        use_residual: bool = True,
        rngs: nnx.Rngs,
    ):
        self.in_planes = 64

        self.use_residual = use_residual
        self.use_batch_norm = use_batch_norm
        self.use_bias = use_bias

        self.conv1 = nnx.Conv(
            num_channels,
            self.in_planes,
            kernel_size=(7, 7),
            strides=(2, 2),
            padding=3,
            use_bias=use_bias,
            rngs=rngs,
        )
        self.bn1 = (
            nnx.BatchNorm(64, momentum=0.9, epsilon=1e-5, rngs=rngs)
            if use_batch_norm
            else lambda x: x
        )

        self.layer1 = self._make_layer(block_cls, 64, layers[0], stride=1, rngs=rngs)
        self.layer2 = self._make_layer(block_cls, 128, layers[1], stride=2, rngs=rngs)
        self.layer3 = self._make_layer(block_cls, 256, layers[2], stride=2, rngs=rngs)
        self.layer4 = self._make_layer(block_cls, 512, layers[3], stride=2, rngs=rngs)

        *_, (final_planes, _) = [
            (p, l) for p, l in zip([64, 128, 256, 512], layers) if l > 0
        ]

        self.fc = nnx.Linear(final_planes * block_cls.expansion, num_classes, rngs=rngs)

    def _make_layer(
        self,
        block: type[nnx.Module],
        planes: int,
        num_blocks: int,
        stride: int,
        *,
        rngs: nnx.Rngs,
    ):
        if num_blocks == 0:
            return nnx.Sequential(lambda x: x)
        layers = []
        layers.append(
            block(
                self.in_planes,
                planes,
                stride=stride,
                use_bias=self.use_bias,
                use_batch_norm=self.use_batch_norm,
                use_residual=self.use_residual,
                rngs=rngs,
            )
        )
        self.in_planes = planes * block.expansion
        for _ in range(1, num_blocks):
            layers.append(block(self.in_planes, planes, stride=1, rngs=rngs))
        return nnx.Sequential(*layers)

    def __call__(self, x: Array) -> Array:
        x = nnx.relu(self.bn1(self.conv1(x)))
        x = nnx.max_pool(x, (3, 3), strides=(2, 2), padding="SAME")

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)

        x = nnx.avg_pool(x, (x.shape[1], x.shape[2]))
        x = x.reshape((x.shape[0], -1))
        x = self.fc(x)
        return x


def resnet6(
    *,
    num_classes: int = 1000,
    num_channels: int = 3,
    use_bias=False,
    use_batch_norm=True,
    use_residual=True,
    rngs: nnx.Rngs,
):
    return ResNet(
        BasicBlock,
        [1, 1, 0, 0],
        num_classes=num_classes,
        num_channels=num_channels,
        use_bias=use_bias,
        use_batch_norm=use_batch_norm,
        use_residual=use_residual,
        rngs=rngs,
    )


def resnet8(
    *,
    num_classes: int = 1000,
    num_channels: int = 3,
    use_bias=False,
    use_batch_norm=True,
    use_residual=True,
    rngs: nnx.Rngs,
):
    return ResNet(
        Bottleneck,
        [1, 1, 0, 0],
        num_classes=num_classes,
        num_channels=num_channels,
        use_bias=use_bias,
        use_batch_norm=use_batch_norm,
        use_residual=use_residual,
        rngs=rngs,
    )


def resnet10(
    *,
    num_classes: int = 1000,
    num_channels: int = 3,
    use_bias=False,
    use_batch_norm=True,
    use_residual=True,
    rngs: nnx.Rngs,
):
    return ResNet(
        BasicBlock,
        [2, 2, 0, 0],
        num_classes=num_classes,
        num_channels=num_channels,
        use_bias=use_bias,
        use_batch_norm=use_batch_norm,
        use_residual=use_residual,
        rngs=rngs,
    )


def resnet11(
    *,
    num_classes: int = 1000,
    num_channels: int = 3,
    use_bias=False,
    use_batch_norm=True,
    use_residual=True,
    rngs: nnx.Rngs,
):
    return ResNet(
        Bottleneck,
        [1, 1, 1, 0],
        num_classes=num_classes,
        num_channels=num_channels,
        use_bias=use_bias,
        use_batch_norm=use_batch_norm,
        use_residual=use_residual,
        rngs=rngs,
    )


def resnet14(
    *,
    num_classes: int = 1000,
    num_channels: int = 3,
    use_bias=False,
    use_batch_norm=True,
    use_residual=True,
    rngs: nnx.Rngs,
):
    return ResNet(
        Bottleneck,
        [2, 2, 0, 0],
        num_classes=num_classes,
        num_channels=num_channels,
        use_bias=use_bias,
        use_batch_norm=use_batch_norm,
        use_residual=use_residual,
        rngs=rngs,
    )


def resnet18(
    *,
    num_classes: int = 1000,
    num_channels: int = 3,
    use_bias=False,
    use_batch_norm=True,
    use_residual=True,
    rngs: nnx.Rngs,
):
    return ResNet(
        BasicBlock,
        [2, 2, 2, 2],
        num_classes=num_classes,
        num_channels=num_channels,
        use_bias=use_bias,
        use_batch_norm=use_batch_norm,
        use_residual=use_residual,
        rngs=rngs,
    )


def resnet34(
    *,
    num_classes: int = 1000,
    num_channels: int = 3,
    use_bias=False,
    use_batch_norm=True,
    use_residual=True,
    rngs: nnx.Rngs,
):
    return ResNet(
        BasicBlock,
        [3, 4, 6, 3],
        num_classes=num_classes,
        num_channels=num_channels,
        use_bias=use_bias,
        use_batch_norm=use_batch_norm,
        use_residual=use_residual,
        rngs=rngs,
    )


def resnet50(
    *,
    num_classes: int = 1000,
    num_channels: int = 3,
    use_bias=False,
    use_batch_norm=True,
    use_residual=True,
    rngs: nnx.Rngs,
):
    return ResNet(
        Bottleneck,
        [3, 4, 6, 3],
        num_classes=num_classes,
        num_channels=num_channels,
        use_bias=use_bias,
        use_batch_norm=use_batch_norm,
        use_residual=use_residual,
        rngs=rngs,
    )


def resnet101(
    *,
    num_classes: int = 1000,
    num_channels: int = 3,
    use_bias=False,
    use_batch_norm=True,
    use_residual=True,
    rngs: nnx.Rngs,
):
    return ResNet(
        Bottleneck,
        [3, 4, 23, 3],
        num_classes=num_classes,
        num_channels=num_channels,
        use_bias=use_bias,
        use_batch_norm=use_batch_norm,
        use_residual=use_residual,
        rngs=rngs,
    )


def resnet152(
    *,
    num_classes: int = 1000,
    num_channels: int = 3,
    use_bias=False,
    use_batch_norm=True,
    use_residual=True,
    rngs: nnx.Rngs,
):
    return ResNet(
        Bottleneck,
        [3, 8, 36, 3],
        num_classes=num_classes,
        num_channels=num_channels,
        use_bias=use_bias,
        use_batch_norm=use_batch_norm,
        use_residual=use_residual,
        rngs=rngs,
    )

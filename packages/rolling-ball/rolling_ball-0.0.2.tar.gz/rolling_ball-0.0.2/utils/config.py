from pathlib import Path
from typing import Literal, Sequence

from flax.typing import PaddingLike
from pydantic import BaseModel

ActivationName = Literal["relu", "sigmoid", "tanh", "swish"]
ModelName = Literal["mlp", "cnn", "resnet"]
OptimizerName = Literal["sgd", "adam", "rbo"]
DatasetName = Literal[
    "mnist",
    "cifar10",
    "cifar100",
    "celeb_a",
    "stanford_dogs",
    "oxford_iiit_pet",
    "oxford_flowers102",
    "imagenette",
    "imagenet_resized32x32",
]
TransformName = Literal["normalize", "to-tuple", "resize", "drop-alpha"]


class MLPConfig(BaseModel):
    layer_sizes: list[int]
    activation: ActivationName
    use_bias: bool


class CNNConfig(BaseModel):
    n_channels: list[int]
    kernel_sizes: Sequence[int | Sequence[int]]
    embedding_dim: int
    n_classes: int
    use_bias: bool
    activation: ActivationName
    padding: PaddingLike = "SAME"
    strides: int | Sequence[int] | None = 1


class ResNetConfig(BaseModel):
    variant: Literal[
        "resnet6",
        "resnet8",
        "resnet10",
        "resnet11",
        "resnet14",
        "resnet18",
        "resnet34",
        "resnet50",
        "resnet101",
    ]
    n_channels: int
    n_classes: int
    use_bias: bool
    use_residual: bool
    use_batch_norm: bool


class VGGConfig(BaseModel):
    variant: Literal["vgg9", "vgg16", "vgg19"]
    n_channels: int
    n_classes: int


class AlexNetConfig(BaseModel):
    n_classes: int
    dropout_rate: float


class ScheduleConfig(BaseModel):
    name: str
    params: dict


class SGDConfig(BaseModel):
    learning_rate: float


class AdamConfig(BaseModel):
    learning_rate: float
    beta1: float
    beta2: float
    eps: float


class AdamWConfig(BaseModel):
    learning_rate: float
    beta1: float
    beta2: float
    eps: float
    weight_decay: float


class RMSPropConfig(BaseModel):
    learning_rate: float
    decay: float
    eps: float
    initial_scale: float


class LBFGSConfig(BaseModel):
    learning_rate: float
    memory_size: int


TxConfig = SGDConfig | AdamConfig | AdamWConfig | RMSPropConfig | LBFGSConfig


class ResizeConfig(BaseModel):
    name: Literal["resize"] = "resize"
    height: int
    width: int


class NormalizeConfig(BaseModel):
    name: Literal["normalize"] = "normalize"


class ToTupleConfig(BaseModel):
    name: Literal["to-tuple"] = "to-tuple"


class DropAlphaConfig(BaseModel):
    name: Literal["drop-alpha"] = "drop-alpha"


TransformConfig = ResizeConfig | NormalizeConfig | ToTupleConfig | DropAlphaConfig


class SAMConfig(BaseModel):
    txconfig: TxConfig
    rho: float


class RBOConfig(BaseModel):
    learning_rate: float
    radius: float
    projection_step_size: float
    n_projection_steps: int


class EntropySGDConfig(BaseModel):
    learning_rate: float
    scope: float
    num_langevin_steps: int
    langevin_step_size: float
    noise_scale: float
    alpha: float
    seed: int


class DatasetConfig(BaseModel):
    name: DatasetName
    num_channels: int
    num_classes: int
    transforms: list[TransformConfig]
    data_dir: Path


class SingleDataLoaderConfig(BaseModel):
    batch_size: int
    num_workers: int
    split: str
    seed: int


class DataLoaderConfig(BaseModel):
    train: SingleDataLoaderConfig
    validation: SingleDataLoaderConfig | None = None
    test: SingleDataLoaderConfig | None = None


ModelConfig = MLPConfig | CNNConfig | ResNetConfig | VGGConfig | AlexNetConfig
OptimizerConfig = (
    SGDConfig
    | AdamConfig
    | RBOConfig
    | SAMConfig
    | LBFGSConfig
    | RMSPropConfig
    | AdamWConfig
    | EntropySGDConfig
)


class Config(BaseModel):
    model: ModelConfig
    optimizer: OptimizerConfig
    dataset: DatasetConfig
    dataloaders: DataLoaderConfig
    seed: int
    n_epochs: int

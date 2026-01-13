from pathlib import Path
from typing import get_args

import tensorflow_datasets as tfds
from flax import nnx
from grain import python as grain
from optax import adam, adamw, lbfgs, rmsprop, sgd

from ..models import (
    CNN,
    MLP,
    AlexNet,
    resnet6,
    resnet8,
    resnet10,
    resnet11,
    resnet14,
    resnet18,
    resnet34,
    resnet50,
    resnet101,
    vgg9,
    vgg16,
    vgg19,
)
from ..optim import SAM, EntropySGD, OptaxOptimizer, RollingBallOptimizer
from .config import (
    ActivationName,
    AdamConfig,
    AdamWConfig,
    AlexNetConfig,
    CNNConfig,
    Config,
    DataLoaderConfig,
    DatasetConfig,
    DropAlphaConfig,
    EntropySGDConfig,
    LBFGSConfig,
    MLPConfig,
    NormalizeConfig,
    OptimizerConfig,
    RBOConfig,
    ResizeConfig,
    ResNetConfig,
    RMSPropConfig,
    SAMConfig,
    ScheduleConfig,
    SGDConfig,
    ToTupleConfig,
    TransformConfig,
    TransformName,
    VGGConfig,
)
from .data import DropAlpha, Normalize, Resize, ToTuple, cifar10, cifar100, mnist


def get_activation(name: ActivationName):
    match name:
        case "relu":
            return nnx.relu
        case "sigmoid":
            return nnx.sigmoid
        case "tanh":
            return nnx.tanh
        case "swish":
            return nnx.swish
        case _:
            raise ValueError(
                f"Invalid activation function: '{name}'. "
                f"Must be one of {get_args(ActivationName)}."
            )


def get_transform(config: TransformConfig):
    match config:
        case ResizeConfig(height=height, width=width):
            return Resize(height, width)
        case NormalizeConfig():
            return Normalize()
        case ToTupleConfig():
            return ToTuple()
        case DropAlphaConfig():
            return DropAlpha()
        case _:
            raise ValueError(
                f"Invalid transform: '{config.name}'. "
                f"Must be one of {get_args(TransformName)}."
            )


def get_data_source(config: DatasetConfig, split):
    name = config.name
    data_dir = config.data_dir

    return tfds.data_source(
        data_dir=data_dir,
        name=name,
        split=split,
        download_and_prepare_kwargs={"file_format": "array_record"},
    )


def get_loaders(config: DataLoaderConfig, dataconfig: DatasetConfig):
    result = {}
    train, validation, test = config.train, config.validation, config.test
    if train is None:
        raise ValueError("Must provide a train loader")

    transforms = [get_transform(t) for t in dataconfig.transforms]
    train_source = get_data_source(dataconfig, train.split)
    train_loader = grain.DataLoader(
        data_source=train_source,
        operations=[*transforms, grain.Batch(train.batch_size)],
        sampler=grain.SequentialSampler(num_records=len(train_source), seed=train.seed),
    )
    result["train"] = train_loader
    if validation is not None:
        validation_source = get_data_source(dataconfig, validation.split)
        validation_loader = grain.DataLoader(
            data_source=validation_source,
            operations=[*transforms, grain.Batch(validation.batch_size)],
            sampler=grain.SequentialSampler(
                num_records=len(validation_source), seed=validation.seed
            ),
        )
        result["validation"] = validation_loader

    if test is not None:
        test_source = get_data_source(dataconfig, test.split)
        test_loader = grain.DataLoader(
            data_source=test_source,
            operations=[*transforms, grain.Batch(test.batch_size)],
            sampler=grain.SequentialSampler(
                num_records=len(test_source), seed=test.seed
            ),
        )
        result["test"] = test_loader
    return result


def get_model(config: Config):
    seed = config.seed
    match config.model:
        case MLPConfig(
            layer_sizes=layer_sizes, activation=activation, use_bias=use_bias
        ):
            activation = get_activation(activation)
            return MLP(layer_sizes, activation, use_bias, rngs=nnx.Rngs(seed))
        case CNNConfig(
            n_channels=n_channels,
            kernel_sizes=kernel_sizes,
            embedding_dim=embedding_dim,
            use_bias=use_bias,
            activation=activation,
            padding=padding,
            strides=strides,
            n_classes=n_classes,
        ):
            activation = get_activation(activation)
            return CNN(
                num_channels=n_channels,
                kernel_sizes=kernel_sizes,
                embedding_dim=embedding_dim,
                use_bias=use_bias,
                padding=padding,
                strides=strides,
                activation=activation,
                num_classes=n_classes,
                rngs=nnx.Rngs(seed),
            )
        case ResNetConfig(
            variant=variant,
            n_channels=n_channels,
            n_classes=n_classes,
            use_bias=use_bias,
            use_residual=use_residual,
            use_batch_norm=use_batch_norm,
        ):
            match variant:
                case "resnet6":
                    model_fn = resnet6
                case "resnet8":
                    model_fn = resnet8
                case "resnet10":
                    model_fn = resnet10
                case "resnet11":
                    model_fn = resnet11
                case "resnet14":
                    model_fn = resnet14
                case "resnet18":
                    model_fn = resnet18
                case "resnet34":
                    model_fn = resnet34
                case "resnet50":
                    model_fn = resnet50
                case "resnet101":
                    model_fn = resnet101
                case _:
                    raise ValueError(f"Invalid ResNet variant {variant}.")

            return model_fn(
                num_classes=n_classes,
                num_channels=n_channels,
                use_bias=use_bias,
                use_batch_norm=use_batch_norm,
                use_residual=use_residual,
                rngs=nnx.Rngs(seed),
            )

        case VGGConfig(variant=variant, n_channels=n_channels, n_classes=n_classes):
            match variant:
                case "vgg9":
                    model_fn = vgg9
                case "vgg16":
                    model_fn = vgg16
                case "vgg19":
                    model_fn = vgg19
                case _:
                    raise ValueError(f"Invalid VGG variant {variant}.")
            return model_fn(
                num_channels=n_channels, num_classes=n_classes, rngs=nnx.Rngs(seed)
            )

        case AlexNetConfig(n_classes=n_classes, dropout_rate=dropout_rate):
            return AlexNet(
                num_classes=n_classes, dropout_rate=dropout_rate, rngs=nnx.Rngs(seed)
            )

        case _ as model:
            raise ValueError(f"Invalid model config: {model.__class__.__name__}")


def get_schedule(config: ScheduleConfig): ...


def get_optimizer(config: OptimizerConfig, model: nnx.Module):
    if not isinstance(model, nnx.Module):
        raise ValueError("model must be an instance of nnx.Module")
    match config:
        case SGDConfig(learning_rate=learning_rate):
            return OptaxOptimizer(model, tx=sgd(learning_rate))
        case AdamConfig(learning_rate=learning_rate, beta1=beta1, beta2=beta2, eps=eps):
            return OptaxOptimizer(model, tx=adam(learning_rate, beta1, beta2, eps))
        case AdamWConfig(
            learning_rate=learning_rate,
            beta1=beta1,
            beta2=beta2,
            eps=eps,
            weight_decay=weight_decay,
        ):
            return OptaxOptimizer(
                model,
                tx=adamw(learning_rate, beta1, beta2, eps, weight_decay=weight_decay),
            )
        case RMSPropConfig(learning_rate=learning_rate, decay=decay, eps=eps):
            return OptaxOptimizer(model, tx=rmsprop(learning_rate, decay, eps))
        case LBFGSConfig(learning_rate=learning_rate, memory_size=memory_size):
            return OptaxOptimizer(model, tx=lbfgs(learning_rate, memory_size))
        case SAMConfig(rho=rho, txconfig=txconfig):
            return SAM(model, tx=get_optimizer(txconfig, model).tx, rho=rho)

        case RBOConfig(
            learning_rate=learning_rate,
            radius=radius,
            projection_step_size=projection_step_size,
            n_projection_steps=n_projection_steps,
        ):
            return RollingBallOptimizer(
                model, learning_rate, radius, projection_step_size, n_projection_steps
            )
        case EntropySGDConfig(
            learning_rate=learning_rate,
            scope=scope,
            num_langevin_steps=num_langevin_steps,
            langevin_step_size=langevin_step_size,
            noise_scale=noise_scale,
            alpha=alpha,
            seed=seed,
        ):
            return EntropySGD(
                model,
                learning_rate,
                scope,
                num_langevin_steps,
                langevin_step_size,
                noise_scale,
                alpha,
                rngs=nnx.Rngs(seed),
            )
        case _:
            raise ValueError(f"Invalid optimizer config: {config.__class__.__name__}")


def make(config: Config):
    model = get_model(config)
    optimizer = get_optimizer(config.optimizer, model)
    loaders = get_loaders(config.dataloaders, config.dataset)
    return model, optimizer, loaders


def data(
    name: str,
    data_dir: str | Path = "data",
    batch_size: int = 256,
    validation_split: str = "20%",
    seed: int = 0,
):
    if name == "mnist":
        return mnist(data_dir, batch_size, validation_split, seed)
    if name == "cifar10":
        return cifar10(data_dir, batch_size, validation_split, seed)
    if name == "cifar100":
        return cifar100(data_dir, batch_size, validation_split, seed)

    raise ValueError(f"Unknown dataset: {name}")

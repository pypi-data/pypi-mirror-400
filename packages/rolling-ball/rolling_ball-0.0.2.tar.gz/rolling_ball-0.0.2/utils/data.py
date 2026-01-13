from collections import namedtuple
from math import ceil
from pathlib import Path

import albumentations as A
import tensorflow_datasets as tfds
from grain import python as grain


class Normalize(grain.MapTransform):
    def map(self, element):
        image = element["image"]
        element["image"] = image / 255.0
        return element


class ToTuple(grain.MapTransform):
    def map(self, element):
        image = element["image"]
        label = element["label"]
        return (image, label)


class Resize(grain.MapTransform):
    def __init__(self, height: int = 100, width: int = 100):
        self.transform = A.Resize(height=height, width=width)

    def map(self, element):
        image = element["image"]
        image = self.transform(image=image)["image"]
        element["image"] = image
        return element


class DropAlpha(grain.MapTransform):
    def map(self, element):
        image = element["image"]
        image = image[:, :, :3]
        element["image"] = image
        return element


class DataLoader(grain.DataLoader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.num_classes = self._data_source.dataset_info.features["label"].num_classes

    def __len__(self):
        num_samples = len(self._data_source)
        batch_size = next(
            op for op in self._operations if isinstance(op, grain.Batch)
        ).batch_size
        return ceil(num_samples / batch_size)


def mnist(
    data_dir: str | Path = "data",
    batch_size: int = 256,
    validation_split: str = "20%",
    seed: int = 0,
):

    train, validation, test = tfds.data_source(
        name="mnist",
        split=[f"train[:{validation_split}]", f"train[{validation_split}:]", "test"],
        data_dir=data_dir,
        download_and_prepare_kwargs={"file_format": "array_record"},
    )

    train_loader = DataLoader(
        data_source=train,
        operations=[Normalize(), ToTuple(), grain.Batch(batch_size=batch_size)],
        sampler=grain.SequentialSampler(num_records=len(train), seed=seed),
    )

    validation_loader = DataLoader(
        data_source=validation,
        operations=[Normalize(), ToTuple(), grain.Batch(batch_size=batch_size)],
        sampler=grain.SequentialSampler(num_records=len(validation), seed=seed),
    )

    test_loader = DataLoader(
        data_source=test,
        operations=[Normalize(), ToTuple(), grain.Batch(batch_size=batch_size)],
        sampler=grain.SequentialSampler(num_records=len(test), seed=seed),
    )

    return namedtuple("MNISTLoaders", ["train", "validation", "test"])(
        train=train_loader, validation=validation_loader, test=test_loader
    )


def cifar10(
    data_dir: str | Path = "data",
    batch_size: int = 256,
    validation_split: str = "20%",
    seed: int = 0,
):

    train, validation, test = tfds.data_source(
        name="cifar10",
        split=[f"train[:{validation_split}]", f"train[{validation_split}:]", "test"],
        data_dir=data_dir,
        download_and_prepare_kwargs={"file_format": "array_record"},
    )

    train_loader = DataLoader(
        data_source=train,
        operations=[Normalize(), ToTuple(), grain.Batch(batch_size=batch_size)],
        sampler=grain.SequentialSampler(num_records=len(train), seed=seed),
    )

    validation_loader = DataLoader(
        data_source=validation,
        operations=[Normalize(), ToTuple(), grain.Batch(batch_size=batch_size)],
        sampler=grain.SequentialSampler(num_records=len(validation), seed=seed),
    )

    test_loader = DataLoader(
        data_source=test,
        operations=[Normalize(), ToTuple(), grain.Batch(batch_size=batch_size)],
        sampler=grain.SequentialSampler(num_records=len(test), seed=seed),
    )

    return namedtuple("CIFAR10Loaders", ["train", "validation", "test"])(
        train=train_loader, validation=validation_loader, test=test_loader
    )


def cifar100(
    data_dir: str | Path = "data",
    batch_size: int = 256,
    validation_split: str = "20%",
    seed: int = 0,
):
    train, validation, test = tfds.data_source(
        name="cifar100",
        split=[f"train[:{validation_split}]", f"train[{validation_split}:]", "test"],
        data_dir=data_dir,
        download_and_prepare_kwargs={"file_format": "array_record"},
    )

    train_loader = DataLoader(
        data_source=train,
        operations=[Normalize(), ToTuple(), grain.Batch(batch_size=batch_size)],
        sampler=grain.SequentialSampler(num_records=len(train), seed=seed),
    )

    validation_loader = DataLoader(
        data_source=validation,
        operations=[Normalize(), ToTuple(), grain.Batch(batch_size=batch_size)],
        sampler=grain.SequentialSampler(num_records=len(validation), seed=seed),
    )

    test_loader = DataLoader(
        data_source=test,
        operations=[Normalize(), ToTuple(), grain.Batch(batch_size=batch_size)],
        sampler=grain.SequentialSampler(num_records=len(test), seed=seed),
    )

    return namedtuple("CIFAR100Loaders", ["train", "validation", "test"])(
        train=train_loader, validation=validation_loader, test=test_loader
    )

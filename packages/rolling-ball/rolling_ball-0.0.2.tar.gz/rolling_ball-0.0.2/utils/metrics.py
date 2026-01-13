from pathlib import Path

import jax
import jax.numpy as jnp
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from chex import Array


def save(history: dict[str, dict[str, list[list[float]]]], metrics_dir: Path):
    metrics_dir = metrics_dir.absolute()
    data_dir = metrics_dir / "data"
    train_dir = data_dir / "train"
    train_dir.mkdir(parents=True)
    validation_dir = data_dir / "validation"
    validation_dir.mkdir(parents=True)

    train_loss = np.array(history["train"]["loss"])
    validation_loss = np.array(history["validation"]["loss"])
    train_accuracy = np.array(history["train"]["accuracy"])
    validation_accuracy = np.array(history["validation"]["accuracy"])

    train_epoch = pd.DataFrame(
        {
            "loss": train_loss.mean(axis=1),
            "accuracy": train_accuracy.mean(axis=1),
        },
        index=range(1, len(train_loss) + 1),
    )
    validation_epoch = pd.DataFrame(
        {
            "loss": validation_loss.mean(axis=1),
            "accuracy": validation_accuracy.mean(axis=1),
        },
        index=range(1, len(validation_loss) + 1),
    )

    train_epoch.to_csv(train_dir / "epoch.csv")
    validation_epoch.to_csv(validation_dir / "epoch.csv")

    train_step = pd.DataFrame(
        {
            "loss": train_loss.flatten(),
            "accuracy": train_accuracy.flatten(),
        },
        index=range(1, len(train_loss) * len(train_loss[0]) + 1),
    )
    validation_step = pd.DataFrame(
        {
            "loss": validation_loss.flatten(),
            "accuracy": validation_accuracy.flatten(),
        },
        index=range(1, len(validation_loss) * len(validation_loss[0]) + 1),
    )

    train_step.to_csv(train_dir / "step.csv")
    validation_step.to_csv(validation_dir / "step.csv")

    return train_step, validation_step, train_epoch, validation_epoch


def plot_and_save(
    train_step: pd.DataFrame,
    validation_step: pd.DataFrame,
    train_epoch: pd.DataFrame,
    validation_epoch: pd.DataFrame,
    metrics_dir: Path,
):
    metrics_dir = metrics_dir.absolute()
    plot_dir = metrics_dir / "plots"
    plot_dir.mkdir(parents=True)

    plot_individually(
        train_step, validation_step, train_epoch, validation_epoch, metrics_dir
    )
    plt.close()

    fig = plt.figure()

    epoch, tstep, vstep = fig.subfigures(1, 3)

    ax: list[plt.Axes] = epoch.subplots(2, 1, sharex=True)

    ax[0].plot(train_epoch["loss"], label="train")
    ax[0].plot(validation_epoch["loss"], label="validation")
    ax[0].legend()
    ax[0].set_title("Loss")

    ax[1].plot(train_epoch["accuracy"], label="train")
    ax[1].plot(validation_epoch["accuracy"], label="validation")
    ax[1].legend()
    ax[1].set_title("Accuracy")
    epoch.suptitle("Epoch metrics")

    ax = tstep.subplots(2, 1, sharex=True)

    ax[0].plot(train_step["loss"], label="train")
    # ax[0].plot(validation_step["loss"], label="validation")
    ax[0].legend()
    ax[0].set_title("Loss")

    ax[1].plot(train_step["accuracy"], label="train")
    # ax[1].plot(validation_step["accuracy"], label="validation")
    ax[1].legend()
    ax[1].set_title("Accuracy")

    tstep.suptitle("Train step metrics")

    ax = vstep.subplots(2, 1, sharex=True)

    ax[0].plot(validation_step["loss"], label="validation")
    ax[0].legend()
    ax[0].set_title("Loss")

    ax[1].plot(validation_step["accuracy"], label="validation")
    ax[1].legend()
    ax[1].set_title("Accuracy")

    vstep.suptitle("Validation step metrics")

    fig.savefig(plot_dir / "metrics.pdf")


def plot_individually(
    train_step: pd.DataFrame,
    validation_step: pd.DataFrame,
    train_epoch: pd.DataFrame,
    validation_epoch: pd.DataFrame,
    metrics_dir: Path,
):

    metrics_dir = metrics_dir.absolute()
    plot_dir = metrics_dir / "plots"
    plot_dir.mkdir(parents=True, exist_ok=True)

    # train  loss
    plt.plot(train_step["loss"], label="train")
    plt.plot(validation_step["loss"], label="validation")
    plt.legend()
    plt.title("Train loss")
    plt.savefig(plot_dir / "train_loss.pdf")
    plt.close()

    # train  accuracy
    plt.plot(train_step["accuracy"], label="train")
    plt.plot(validation_step["accuracy"], label="validation")
    plt.legend()
    plt.title("Train accuracy")
    plt.savefig(plot_dir / "train_accuracy.pdf")
    plt.close()

    # validation  loss
    plt.plot(validation_step["loss"], label="validation")
    plt.legend()
    plt.title("Validation loss")
    plt.savefig(plot_dir / "validation_loss.pdf")
    plt.close()

    # validation  accuracy
    plt.plot(validation_step["accuracy"], label="validation")
    plt.legend()
    plt.title("Validation accuracy")
    plt.savefig(plot_dir / "validation_accuracy.pdf")
    plt.close()

    # epoch  loss
    plt.plot(train_epoch["loss"], label="train")
    plt.plot(validation_epoch["loss"], label="validation")
    plt.legend()
    plt.title("Epoch loss")
    plt.savefig(plot_dir / "epoch_loss.pdf")
    plt.close()

    # epoch  accuracy
    plt.plot(train_epoch["accuracy"], label="train")
    plt.plot(validation_epoch["accuracy"], label="validation")
    plt.legend()
    plt.title("Epoch accuracy")
    plt.savefig(plot_dir / "epoch_accuracy.pdf")
    plt.close()

    # epoch  loss
    plt.plot(train_epoch["loss"], label="train")
    plt.plot(validation_epoch["loss"], label="validation")
    plt.legend()
    plt.title("Epoch loss")
    plt.savefig(plot_dir / "epoch_loss.pdf")
    plt.close()

    # epoch  accuracy
    plt.plot(train_epoch["accuracy"], label="train")
    plt.plot(validation_epoch["accuracy"], label="validation")
    plt.legend()
    plt.title("Epoch accuracy")
    plt.savefig(plot_dir / "epoch_accuracy.pdf")
    plt.close()


def compute_output_entropy(logits: Array) -> float:
    """Compute entropy of output distribution."""
    probs = jax.nn.softmax(logits, axis=-1)
    entropy = -jnp.sum(probs * jnp.log(probs + 1e-8), axis=-1).mean()
    return entropy


def compute_per_class_accuracy(logits: Array, labels: Array, num_classes: int) -> Array:
    """Compute accuracy per class.

    Returns:
        Array of shape (num_classes,) with accuracy for each class.
        NaN for classes with no samples.
    """
    predictions = logits.argmax(-1)
    correct = predictions == labels

    # Create one-hot encoding for labels: (N, num_classes)
    labels_one_hot = jax.nn.one_hot(labels, num_classes)

    # For each class, compute: sum(correct * one_hot) / sum(one_hot)
    # correct_expanded: (N, 1) -> broadcast to (N, num_classes)
    correct_expanded = correct[:, None]  # (N, 1)
    class_correct = jnp.sum(correct_expanded * labels_one_hot, axis=0)  # (num_classes,)
    class_counts = jnp.sum(labels_one_hot, axis=0)  # (num_classes,)

    # Compute accuracy: class_correct / class_counts, but set to NaN if count is 0
    per_class_acc = jnp.where(class_counts > 0, class_correct / class_counts, jnp.nan)

    return per_class_acc

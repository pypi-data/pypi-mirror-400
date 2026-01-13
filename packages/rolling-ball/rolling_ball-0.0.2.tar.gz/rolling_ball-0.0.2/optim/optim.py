"""Definition of the Optimizer class."""

from collections.abc import Callable
from typing import Generic

from flax import nnx
from flax.nnx import M
from optax import Params, Updates


class Optimizer(nnx.Object, Generic[M]):
    """Base class for optimizers."""

    model: nnx.Module
    step: nnx.Variable

    def update(
        self, value_and_grad_fn: Callable[[Params], tuple[float, Updates]]
    ) -> None:
        """Updates model parameters and optimizer state in place."""
        raise NotImplementedError

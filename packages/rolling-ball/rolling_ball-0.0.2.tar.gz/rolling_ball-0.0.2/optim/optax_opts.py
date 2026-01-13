"""Wraps Optax optimizers in the Optimizer class with metrics tracking."""

import jax
import jax.numpy as jnp
from flax import nnx
from flax.nnx import M
from optax import GradientTransformation, Updates

from ..utils.spatial import tree_norm


class OptaxOptimizer(nnx.Optimizer):
    """Wraps Optax optimizers in the Optimizer class with metrics tracking.

    This optimizer extends nnx.Optimizer and automatically tracks:
    - gradient_norm: L2 norm of gradients
    - weight_norm: L2 norm of parameters (before update)
    - update_magnitude_abs: Absolute update magnitude
    - update_magnitude_rel: Relative update magnitude (absolute / weight_norm)
    """

    def __init__(
        self,
        model: M,
        tx: GradientTransformation,
        wrt: nnx.filterlib.Filter = nnx.Param,
    ):
        """Initialize the metrics-tracking optimizer.

        Args:
            model: The model to optimize
            tx: Optax gradient transformation
            wrt: Filter for which parameters to optimize (default: nnx.Param)
        """
        super().__init__(model, tx, wrt=wrt)
        self.model = model
        self.tx = tx
        self.wrt = wrt

        # Metrics stored in internal state
        self.gradient_norm = nnx.Variable(jnp.array(0.0, dtype=jnp.float32))
        self.weight_norm = nnx.Variable(jnp.array(0.0, dtype=jnp.float32))
        self.update_magnitude_abs = nnx.Variable(jnp.array(0.0, dtype=jnp.float32))
        self.update_magnitude_rel = nnx.Variable(jnp.array(0.0, dtype=jnp.float32))

    def update(self, grads: Updates, **kwargs):
        """Update model parameters and track metrics.

        Args:
            grads: Gradients to apply
            **kwargs: Additional arguments passed to the underlying optimizer
        """
        # Get parameters before update
        params_before, _ = nnx.state(self.model, self.wrt, ...)
        weight_norm_before = tree_norm(params_before, ord=2)
        self.weight_norm.value = weight_norm_before

        # Compute and store gradient norm
        grad_norm = tree_norm(grads, ord=2)
        self.gradient_norm.value = grad_norm

        # Update the model using the parent optimizer
        super().update(grads, **kwargs)

        # Get parameters after update
        params_after, _ = nnx.state(self.model, self.wrt, ...)

        # Compute update magnitudes
        update_abs = tree_norm(
            jax.tree.map(lambda x, y: x - y, params_before, params_after),
            ord=2,
        )
        self.update_magnitude_abs.value = update_abs
        self.update_magnitude_rel.value = update_abs / (weight_norm_before + 1e-8)

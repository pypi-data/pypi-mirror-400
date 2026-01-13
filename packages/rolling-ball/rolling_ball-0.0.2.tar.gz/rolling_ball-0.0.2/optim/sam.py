from collections.abc import Callable

import jax
import jax.numpy as jnp
import optax
from flax import nnx
from flax.nnx import M
from optax import GradientTransformation, Params, Updates

from ..utils.spatial import tree_norm
from .optim import Optimizer


class SAM(Optimizer):
    def __init__(
        self,
        model: M,
        tx: GradientTransformation,
        rho: float,
        wrt: nnx.filterlib.Filter = nnx.Param,
    ):

        self.step = nnx.Variable(jnp.array(0, dtype=jnp.uint32))
        self.model = model
        self.tx = tx
        self.rho = rho
        self.wrt = wrt
        params = nnx.state(model, wrt)
        self.opt_state = tx.init(params)

        # Metrics stored in internal state
        self.gradient_norm = nnx.Variable(jnp.array(0.0, dtype=jnp.float32))
        self.weight_norm = nnx.Variable(jnp.array(0.0, dtype=jnp.float32))
        self.update_magnitude_abs = nnx.Variable(jnp.array(0.0, dtype=jnp.float32))
        self.update_magnitude_rel = nnx.Variable(jnp.array(0.0, dtype=jnp.float32))

    def update(
        self, value_and_grad_fn: Callable[[Params], tuple[float, Updates]], **kwargs
    ):

        # Get parameters before update
        params = nnx.state(self.model, self.wrt)
        params_before = params
        weight_norm_before = tree_norm(params_before, ord=2)
        self.weight_norm.value = weight_norm_before

        loss, grads = value_and_grad_fn(self.model)

        # Compute and store gradient norm (before normalization)
        grad_norm = tree_norm(grads, ord=2)
        self.gradient_norm.value = grad_norm

        grads = jax.tree.map(lambda g: g / tree_norm(grads), grads)
        noised_params = jax.tree.map(lambda p, g: p + self.rho * g, params, grads)
        nnx.update(self.model, noised_params)
        noised_loss, noised_grads = value_and_grad_fn(self.model)

        updates, new_opt_state = self.tx.update(
            noised_grads, self.opt_state, params, **kwargs
        )
        new_params = optax.apply_updates(params, updates)
        assert isinstance(new_params, nnx.State)

        # Get parameters after update
        params_after = new_params

        # Compute update magnitudes
        update_abs = tree_norm(
            jax.tree.map(lambda x, y: x - y, params_before, params_after),
            ord=2,
        )
        self.update_magnitude_abs.value = update_abs
        self.update_magnitude_rel.value = update_abs / (weight_norm_before + 1e-8)

        self.step.value = self.step.value + 1
        self.opt_state = new_opt_state
        nnx.update(self.model, new_params)

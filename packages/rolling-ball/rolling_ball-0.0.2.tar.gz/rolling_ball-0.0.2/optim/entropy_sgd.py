from collections.abc import Callable

import jax
import jax.numpy as jnp
from flax import nnx
from flax.nnx import M
from jax import tree
from jax.flatten_util import ravel_pytree
from optax import Params, ScalarOrSchedule, Updates

from ..utils.tree import copy
from .optim import Optimizer


class EntropySGD(Optimizer):
    def __init__(
        self,
        model: M,
        learning_rate: ScalarOrSchedule,
        scope: ScalarOrSchedule,
        num_langevin_steps: int,
        langevin_step_size: float,
        noise_scale: float,
        alpha: float,
        wrt: nnx.filterlib.Filter = nnx.Param,
        *,
        rngs: nnx.Rngs,
    ):
        self.step = nnx.Variable(jnp.array(0, dtype=jnp.uint32))
        self.model = model
        self.learning_rate = learning_rate
        self.scope = scope
        self.num_langevin_steps = num_langevin_steps
        self.langevin_step_size = langevin_step_size
        self.noise_scale = noise_scale
        self.wrt = wrt
        self.alpha = alpha
        self.rngs = rngs

        self.opt_state = None

    def update(
        self, value_and_grad_fn: Callable[[Params], tuple[float, Updates]], **kwargs
    ):
        params, others = nnx.state(self.model, self.wrt, ...)

        graph, state = nnx.split(self.model)

        def fn(params):
            model = nnx.merge(graph, params, others)
            return value_and_grad_fn(model)

        params_prime = copy(params)
        mu = copy(params)

        # SGLD loop
        for step in range(self.num_langevin_steps):
            _, grad = fn(params_prime)
            difference = tree.map(lambda p, p_prime: p - p_prime, params, params_prime)
            d_params_prime = tree.map(lambda p, d: p - self.scope * d, grad, difference)
            key = self.rngs.params()
            flat, unflatten = ravel_pytree(params_prime)
            noise = unflatten(jax.random.normal(key, flat.shape) * self.noise_scale)
            # *
            params_prime = tree.map(
                lambda p, d, n: p
                - self.langevin_step_size * d
                + jnp.sqrt(self.langevin_step_size) * n,
                params_prime,
                d_params_prime,
                noise,
            )

            mu = tree.map(
                lambda m, p: (1 - self.alpha) * m + self.alpha * p, mu, params_prime
            )

        difference = tree.map(lambda p, m: p - m, params, mu)
        params = tree.map(
            lambda p, d: p - self.learning_rate * self.scope * d, params, difference
        )

        assert isinstance(params, nnx.State)
        nnx.update(self.model, params)
        self.step.value = self.step.value + 1

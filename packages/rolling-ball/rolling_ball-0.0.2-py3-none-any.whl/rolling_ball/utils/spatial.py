"""Spatial utility functions."""

from typing import Callable

import jax
import jax.flatten_util
import jax.numpy as jnp
import optax
from chex import ArrayTree
from jax import tree
from jax.lax import fori_loop
from optax import Params, Updates, sgd


def tree_norm(x: ArrayTree, ord: str | int | None = 2) -> float:
    """Compute the norm of a PyTree.

    Args:
        tree (PyTree): the PyTree to compute the norm of

    Example usage::

        >>> from jax import numpy as jnp
        >>> tree = {"a": jnp.array([1.0, 2.0]), "b": jnp.array([3.0, 4.0])}
        >>> tree_norm(tree)
        5.4772257806505

    Returns:
        float: The norm of the PyTree
    """
    x, _ = jax.flatten_util.ravel_pytree(x)
    x = jnp.asarray(x)

    return jnp.linalg.norm(x, ord=ord)


def project_on_graph(
    value_and_grad_fn: Callable[[Params], tuple[float, Updates]],
    point: tuple[Params, float],
    x0: Params,
    step_size: float = 0.1,
    n_steps: int = 10,
) -> Params:
    """Takes a function :math:`f: \\mathbb{R}^n \\to \\mathbb{R}`
    and a point :math:`p\\in \\mathbb{R}^{n+1}`,
    and returns the footpoint of :math:`p` on the graph of :math:`f`.

    Args:
        value_and_grad_fn (Callable[[Params], tuple[float, Updates]]): \
            A callable that takes a point :math:`x\\in \\mathbb{R}^n`, \
            and returns :math:`(f(x), \\nabla f(x))`.
        point (tuple[Params, float]): The point :math:`p` to project on the graph.
        x0 (Params): The seed point for the projection optimization algorithm.
        step_size (float, optional): \
            The step size for the projection optimizer. Defaults to 0.1.
        n_steps (int, optional): \
            Number of iterations for the projection optimizer. Defaults to 10.

    Returns:
        Params: The closest point on the graph of :math:`f` to :math:`p`.
    """

    def loss_and_grad(x):
        xp, yp = point
        fx, grad_f = value_and_grad_fn(x)
        Δx = tree.map(lambda x1, x2: x1 - x2, x, xp)
        Δy = fx - yp
        loss = tree_norm(Δx) ** 2 + Δy**2
        scaled_grad = tree.map(lambda g: Δy * g, grad_f)
        grad = tree.map(lambda x1, x2: x1 + x2, Δx, scaled_grad)
        return loss, grad

    solver = sgd(learning_rate=step_size)
    state = solver.init(x0)

    def body_fun(i, state_and_x):
        state, x = state_and_x
        loss, grad = loss_and_grad(x)
        update, state = solver.update(grad, state, x)
        x = optax.apply_updates(x, update)
        return state, x

    _, footpoint = fori_loop(0, n_steps, body_fun, (state, x0))
    return footpoint

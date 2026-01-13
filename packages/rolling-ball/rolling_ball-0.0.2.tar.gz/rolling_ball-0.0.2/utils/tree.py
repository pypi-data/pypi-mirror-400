from jax.tree import map


def copy(tree):
    return map(lambda x: x, tree)

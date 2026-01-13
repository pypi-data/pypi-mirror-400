from collections.abc import Callable

import jax
import jax.numpy as jnp
from flax import nnx
from optax import Params, ScalarOrSchedule, Updates

from ..utils.spatial import project_on_graph, tree_norm
from .optim import Optimizer


class RollingBallOptimizer(Optimizer):

    def __init__(
        self,
        model: nnx.Module,
        learning_rate: ScalarOrSchedule,
        radius: ScalarOrSchedule,
        projection_step_size: float,
        n_projection_steps: int,
        wrt: nnx.filterlib.Filter = nnx.Param,
    ):
        """Sliding Ball Optimizer.

        This optimizer simulates the motion of a ball on the graph of the loss function.
        Since the rolling part of the motion is irrelevant to its position,
        we only consider the translational component.

        Args:
            learning_rate (float): learning rate.
            radius (float): ball radius.
            projection_step_size (float): step size for the projection solver.
            n_projection_steps (int): number of steps for the projection solver.

        Returns:
            GradientTransformationExtraArgs: The corresponding optimizer.
        """

        self.step = nnx.Variable(jnp.array(0, dtype=jnp.uint32))
        self.model = model
        self.wrt = wrt
        self.learning_rate = learning_rate
        self.radius = radius
        self.projection_step_size = projection_step_size
        self.n_projection_steps = n_projection_steps

        # Metrics stored in internal state
        self.gradient_norm = nnx.Variable(jnp.array(0.0, dtype=jnp.float32))
        self.weight_norm = nnx.Variable(jnp.array(0.0, dtype=jnp.float32))
        self.update_magnitude_abs = nnx.Variable(jnp.array(0.0, dtype=jnp.float32))
        self.update_magnitude_rel = nnx.Variable(jnp.array(0.0, dtype=jnp.float32))

    def update(
        self,
        value_and_grad_fn: Callable[[Params], tuple[float, Updates]],
    ):
        params, others = nnx.state(self.model, self.wrt, ...)

        # Store weight norm before update
        weight_norm_before = tree_norm(params, ord=2)
        self.weight_norm.value = weight_norm_before

        loss, grads = value_and_grad_fn(self.model)

        # Compute and store gradient norm
        grad_norm = tree_norm(grads, ord=2)
        self.gradient_norm.value = grad_norm

        g2 = tree_norm(grads) ** 2
        normal = (jax.tree.map(lambda g: -g, grads), 1.0)
        normal = jax.tree.map(lambda n: n / jnp.sqrt(g2 + 1), normal)
        tangent = (grads, g2)

        center = jax.tree.map(lambda x, n: x + self.radius * n, (params, loss), normal)
        candidate = jax.tree.map(
            lambda u, v: u - self.learning_rate * v, center, tangent
        )

        footpoint = center[0]

        graph, state = nnx.split(self.model)

        def fn(params):
            model = nnx.merge(graph, params, others)
            return value_and_grad_fn(model)

        footpoint = project_on_graph(
            fn,
            candidate,
            params,
            self.projection_step_size,
            self.n_projection_steps,
        )
        assert isinstance(footpoint, nnx.State)

        # Compute update magnitude from params before update and footpoint
        update_abs = tree_norm(
            jax.tree.map(lambda x, y: x - y, params, footpoint),
            ord=2,
        )
        self.update_magnitude_abs.value = update_abs
        self.update_magnitude_rel.value = update_abs / (weight_norm_before + 1e-8)

        self.step.value = self.step.value + 1
        nnx.update(self.model, footpoint)


def main():
    import tensorflow_datasets as tfds
    from grain import python as grain
    from optax import softmax_cross_entropy_with_integer_labels as criterion
    from tqdm import tqdm

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

    source = tfds.data_source(
        data_dir="data",
        name="cifar100",
        split="train",
        download_and_prepare_kwargs={"file_format": "array_record"},
    )
    loader = grain.DataLoader(
        data_source=source,
        operations=[
            grain.Batch(256),
            Normalize(),
            ToTuple(),
        ],
        sampler=grain.SequentialSampler(num_records=len(source), seed=0),
        worker_count=0,
    )

    # model = nnx.Sequential(
    #     nnx.Linear(784, 512, rngs=nnx.Rngs(0)),
    #     nnx.relu,
    #     nnx.Linear(512, 512, rngs=nnx.Rngs(0)),
    #     nnx.relu,
    #     nnx.Linear(512, 10, rngs=nnx.Rngs(0)),
    # )

    class CNN(nnx.Module):
        def __init__(self, rngs: nnx.Rngs):
            super().__init__()
            self.conv1 = nnx.Conv(
                3,
                32,
                kernel_size=(3, 3),
                rngs=rngs,
            )
            self.conv2 = nnx.Conv(
                32,
                64,
                kernel_size=(3, 3),
                rngs=rngs,
            )
            self.fc1 = nnx.Linear(57600, 32, rngs=rngs)
            self.fc2 = nnx.Linear(32, 100, rngs=rngs)

        def __call__(self, x):
            x = nnx.relu(self.conv1(x))
            x = nnx.max_pool(x, (2, 2))
            x = nnx.relu(self.conv2(x))
            x = nnx.max_pool(x, (2, 2))
            x = x.reshape((x.shape[0], -1))
            x = nnx.relu(self.fc1(x))
            x = self.fc2(x)
            return x

    model = CNN(rngs=nnx.Rngs(0))
    print(nnx.tabulate(model, jnp.ones((1, 32, 32, 3))))

    def loss_fn(model, batch):
        images, labels = batch
        # images = jnp.reshape(images, (-1, 784))
        logits = model(images)
        return criterion(logits, labels).mean()

    optimizer = RollingBallOptimizer(
        model,
        learning_rate=1.0,
        radius=10.0,
        projection_step_size=1e-3,
        n_projection_steps=100,
    )

    @nnx.jit
    def update(model: nnx.Module, optimizer: RollingBallOptimizer, batch):
        loss = loss_fn(model, batch)
        value_and_grad_fn = nnx.jit(nnx.value_and_grad(loss_fn))
        optimizer.update(lambda m: value_and_grad_fn(m, batch))
        return loss

    for epoch in range(1, 11):
        progbar = tqdm(
            loader,
            ncols=100,
            leave=True,
            desc=f"Epoch {epoch}/10",
            total=len(source) // 256,
        )
        # print(len(loader))
        # break
        for batch in progbar:
            loss = update(model, optimizer, batch)
            progbar.set_postfix_str(f"Loss: {loss:.3f}")


if __name__ == "__main__":
    main()

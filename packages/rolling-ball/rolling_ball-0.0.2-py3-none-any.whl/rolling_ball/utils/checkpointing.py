from io import StringIO
from pathlib import Path


def get_checkpoint_path(
    checkpoint_dir: Path, epoch: int, epoch_metrics: dict[str, float], model: str
) -> Path:
    checkpoint_dir = checkpoint_dir.absolute()
    with StringIO() as f:
        f.write(f"{model=!s}")
        f.write(f",{epoch=}")
        for name, value in epoch_metrics.items():
            f.write(f",{name}={value:2f}")
        ckpt = checkpoint_dir / f.getvalue()

    return ckpt

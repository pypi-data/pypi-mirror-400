from importlib.resources import as_file, files
from typing import ClassVar

import numpy as np

from kosmos.ml.datasets.dataset import SLDataset


class OrganAMNISTDataset(SLDataset):
    """OrganAMNIST dataset for organ classification from medical images.

    Notes:
      - Number of instances: 58,830 (34,561 train + 6,491 val + 17,778 test)
      - Number of features: 784 numeric (28x28 pixel images, flattened)
      - Classes: 11 (different organ types)

    References:
      - MedMNIST: https://medmnist.com/

    """

    ORGAN_CLASSES: ClassVar[list[str]] = [
        "bladder",
        "femur-left",
        "femur-right",
        "heart",
        "kidney-left",
        "kidney-right",
        "liver",
        "lung-left",
        "lung-right",
        "pancreas",
        "spleen",
    ]

    def __init__(self, *, min_max_scaler: bool = True) -> None:
        """Initialize the dataset.

        Args:
            min_max_scaler (bool): Whether to apply min-max scaling to the features.
                Defaults to True.

        """
        path = files("kosmos.ml.datasets.data") / "organamnist.npz"
        with as_file(path) as p:
            data = np.load(p)

            # Combine train, validation, and test sets
            x_train = data["train_images"]
            y_train = data["train_labels"]
            x_val = data["val_images"]
            y_val = data["val_labels"]
            x_test = data["test_images"]
            y_test = data["test_labels"]
            x = np.concatenate([x_train, x_val, x_test], axis=0)
            y = np.concatenate([y_train, y_val, y_test], axis=0)

            # Flatten images
            x = x.reshape(x.shape[0], -1).astype(np.float32, copy=False)

            # Flatten labels
            y = y.flatten().astype(np.int64, copy=False)

        super().__init__(x, y, min_max_scaler=min_max_scaler)

    @property
    def class_names(self) -> list[str]:
        """Return human-readable class labels for organ types."""
        return self.ORGAN_CLASSES

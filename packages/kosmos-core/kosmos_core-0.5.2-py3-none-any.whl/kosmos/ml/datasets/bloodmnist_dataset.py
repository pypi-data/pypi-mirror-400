from importlib.resources import as_file, files
from typing import ClassVar

import numpy as np

from kosmos.ml.datasets.dataset import SLDataset


class BloodMNISTDataset(SLDataset):
    """BloodMNIST dataset for blood cell classification from biomedical images.

    Notes:
      - Number of instances: 17,092 (11,959 train + 1,712 val + 3,421 test)
      - Number of features: 2,352 numeric (28x28x3 RGB images, flattened)
      - Classes: 8 (different blood cell types)

    References:
      - MedMNIST: https://medmnist.com/

    """

    BLOOD_CELL_CLASSES: ClassVar[list[str]] = [
        "basophil",
        "eosinophil",
        "erythroblast",
        "immature_granulocytes",
        "lymphocyte",
        "monocyte",
        "neutrophil",
        "platelet",
    ]

    def __init__(self, *, min_max_scaler: bool = True) -> None:
        """Initialize the dataset.

        Args:
            min_max_scaler (bool): Whether to apply min-max scaling to the features.
                Defaults to True.

        """
        path = files("kosmos.ml.datasets.data") / "bloodmnist.npz"
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

            # Flatten RGB images
            x = x.reshape(x.shape[0], -1).astype(np.float32, copy=False)

            # Flatten labels
            y = y.flatten().astype(np.int64, copy=False)

        super().__init__(x, y, min_max_scaler=min_max_scaler)

    @property
    def class_names(self) -> list[str]:
        """Return human-readable class labels for blood cell types."""
        return self.BLOOD_CELL_CLASSES

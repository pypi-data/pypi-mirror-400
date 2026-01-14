from collections.abc import Callable

import numpy as np
import torch

type TensorMapping = Callable[[torch.Tensor], torch.Tensor]
type TensorNpArray = torch.Tensor | np.ndarray

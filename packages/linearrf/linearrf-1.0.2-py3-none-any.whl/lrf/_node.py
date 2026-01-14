from dataclasses import dataclass
from typing import Union

from lrf._linear_models import Regressor, Classifier


@dataclass
class Node:
    """
    Consolidates all attributes needed at a node, regardless of whether the node is a leaf or not.
    """
    depth: int = None
    split_col_idx: int = None
    threshold: float = None
    metric: float = None
    left_node = None
    right_node = None
    model: Union[Regressor, Classifier] = None

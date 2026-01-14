# Master package init
from . import math
from . import image
from . import graph

# Expose commonly used functions at top-level
from .math.basic import (
    add,
    subtract,
    multiply,
    divide,
    clamp,
    power
)
from .image.core import (
    load_image,
    show_image,
    save_image,
    resize_image,
    crop_image,
    flip_image,
    rotate_image,
    convert_color
)
from .graph.graphs import (
    save_graph,
    line_graph,
    bar_graph,
    scatter_plot,
    histogram
)

__all__ = [
    "math",
    "image",
    "add",
    "subtract",
    "multiply",
    "divide",
    "clamp",
    "power",
    "load_image",
    "show_image",
    "save_image",
    "resize_image",
    "crop_image",
    "flip_image",
    "rotate_image",
    "convert_color",
    "graph",
    "save_graph",
    "line_graph",
    "bar_graph",
    "scatter_plot",
    "histogram"
]

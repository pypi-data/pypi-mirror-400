import torch
from torch import Tensor

Dims = list[int] | tuple[int, ...]


def _shape(shape: torch.Size, dims: Dims, value: int) -> torch.Size:
    shape = list(shape)
    for dim in dims:
        shape[dim] = value

    return torch.Size(shape)


def broadcast_shapes(*shapes: torch.Size, dims: Dims) -> torch.Size:
    shapes = (_shape(shape, dims=dims, value=1) for shape in shapes)
    return _shape(torch.broadcast_shapes(*shapes), dims=dims, value=-1)


def broadcast_tensors(*tensors: Tensor, dims: Dims) -> tuple[Tensor, ...]:
    shape = broadcast_shapes(*(tensor.size() for tensor in tensors), dims=dims)
    return tuple(torch.broadcast_to(tensor, shape) for tensor in tensors)

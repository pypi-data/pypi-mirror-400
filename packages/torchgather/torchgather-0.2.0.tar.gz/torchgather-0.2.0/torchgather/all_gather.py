from typing import Any

from torch import Tensor, distributed
from torch._C._distributed_c10d import ProcessGroup


def all_gather_object(obj: Any, group: ProcessGroup = None) -> list[Any]:
    if not distributed.is_initialized():
        return [obj]

    object_list = [None for _ in range(distributed.get_world_size(group=group))]
    distributed.all_gather_object(object_list=object_list, obj=obj, group=group)

    return object_list


def all_gather(tensor: Tensor, group: ProcessGroup = None, async_op: bool = None) -> list[Tensor]:
    if not distributed.is_initialized():
        return [tensor]

    tensor_list = [tensor.new_empty(size) for size in all_gather_object(tuple(tensor.size()), group=group)]
    distributed.all_gather(tensor_list=tensor_list, tensor=tensor, group=group, async_op=async_op)

    return tensor_list


def all_gather_into_tensor(tensor: Tensor, group: ProcessGroup = None, async_op: bool = None) -> Tensor:
    if not distributed.is_initialized():
        return tensor

    n, *size = tensor.size()
    split_size = all_gather_object(n, group=group)
    output_tensor = tensor.new_empty((sum(split_size), *size))

    tensor_list = output_tensor.split(split_size=split_size, dim=0)
    distributed.all_gather(tensor_list=tensor_list, tensor=tensor, group=group, async_op=async_op)

    return output_tensor

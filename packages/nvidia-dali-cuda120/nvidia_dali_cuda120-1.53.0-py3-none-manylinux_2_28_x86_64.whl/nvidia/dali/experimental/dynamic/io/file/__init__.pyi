# Copyright (c) 2023-2025, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import builtins
from typing import Literal, Optional, Union, overload
from typing import Any, List, Sequence

from nvidia.dali.types import DALIDataType, DALIImageType, DALIInterpType

from collections.abc import Iterable

from nvidia.dali._typing import TensorLike, TensorLikeArg
from nvidia.dali.experimental.dynamic._batch import Batch as Batch
from nvidia.dali.experimental.dynamic._device import Device as Device
from nvidia.dali.experimental.dynamic._eval_context import EvalContext as EvalContext
from nvidia.dali.experimental.dynamic._tensor import Tensor as Tensor
from nvidia.dali.experimental.dynamic._type import DType as DType

@overload
def read(
    filepaths: TensorLike,
    /,
    *,
    device: Optional[Literal["cpu"]] = None,
    dont_use_mmap: Optional[builtins.bool] = False,
    use_o_direct: Optional[builtins.bool] = False,
) -> Union[Tensor, Batch]:
    """
    Reads raw file contents from an encoded filename represented by a 1D byte array.

    .. note::
      To produce a compatible encoded filepath from Python (e.g. in an external_source node generator),
      use `np.frombuffer(filepath_str.encode("utf-8"), dtype=types.UINT8)`.


    Supported backends
     * 'cpu'


    Args
    ----
    filepaths : Tensor/Batch
        File paths to read from.


    Keyword args
    ------------
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    dont_use_mmap : bool, optional, default = `False`
        If set to True, it will use plain file I/O instead of trying to map the file into memory.

        Mapping provides a small performance benefit when accessing a local file system, but for most network file
        systems, it does not provide a benefit
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.
    use_o_direct : bool, optional, default = `False`
        If set to True, the data will be read directly from the storage bypassing system
        cache.

        Mutually exclusive with ``dont_use_mmap=False``.

    """

@overload
def read(
    filepaths: TensorLike,
    /,
    *,
    device: Optional[Literal["cpu"]] = None,
    batch_size: int,
    dont_use_mmap: Optional[builtins.bool] = False,
    use_o_direct: Optional[builtins.bool] = False,
) -> Batch:
    """
    Reads raw file contents from an encoded filename represented by a 1D byte array.

    .. note::
      To produce a compatible encoded filepath from Python (e.g. in an external_source node generator),
      use `np.frombuffer(filepath_str.encode("utf-8"), dtype=types.UINT8)`.


    Supported backends
     * 'cpu'


    Args
    ----
    filepaths : Tensor/Batch
        File paths to read from.


    Keyword args
    ------------
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    dont_use_mmap : bool, optional, default = `False`
        If set to True, it will use plain file I/O instead of trying to map the file into memory.

        Mapping provides a small performance benefit when accessing a local file system, but for most network file
        systems, it does not provide a benefit
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.
    use_o_direct : bool, optional, default = `False`
        If set to True, the data will be read directly from the storage bypassing system
        cache.

        Mutually exclusive with ``dont_use_mmap=False``.

    """

@overload
def read(
    filepaths: Batch,
    /,
    *,
    device: Optional[Literal["cpu"]] = None,
    dont_use_mmap: Optional[builtins.bool] = False,
    use_o_direct: Optional[builtins.bool] = False,
) -> Batch:
    """
    Reads raw file contents from an encoded filename represented by a 1D byte array.

    .. note::
      To produce a compatible encoded filepath from Python (e.g. in an external_source node generator),
      use `np.frombuffer(filepath_str.encode("utf-8"), dtype=types.UINT8)`.


    Supported backends
     * 'cpu'


    Args
    ----
    filepaths : Tensor/Batch
        File paths to read from.


    Keyword args
    ------------
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    dont_use_mmap : bool, optional, default = `False`
        If set to True, it will use plain file I/O instead of trying to map the file into memory.

        Mapping provides a small performance benefit when accessing a local file system, but for most network file
        systems, it does not provide a benefit
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.
    use_o_direct : bool, optional, default = `False`
        If set to True, the data will be read directly from the storage bypassing system
        cache.

        Mutually exclusive with ``dont_use_mmap=False``.

    """

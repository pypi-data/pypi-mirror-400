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

from nvidia.dali._typing import TensorLikeIn, TensorLikeArg
from nvidia.dali.data_node import DataNode

class Max:
    """
    Gets maximal input element along provided axes.

    Supported backends
     * 'cpu'
     * 'gpu'


    Keyword args
    ------------
    axes : int or list of int, optional
        Axis or axes along which reduction is performed.

        Accepted range is [-ndim, ndim-1]. Negative indices are counted from the back.

        Not providing any axis results in reduction of all elements.
    axis_names : :ref:`layout str<layout_str_doc>`, optional
        Name(s) of the axis or axes along which the reduction is performed.

        The input layout is used to translate the axis names to axis indices, for example ``axis_names="HW"`` with input
        layout `"FHWC"` is equivalent to specifying ``axes=[1,2]``. This argument cannot be used together with `axes`.
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    keep_dims : bool, optional, default = `False`
        If True, maintains original input dimensions.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.

    """

    def __init__(
        self,
        /,
        *,
        device: Optional[Literal["cpu", "gpu"]] = None,
        name: Optional[str] = None,
        axes: Union[Sequence[int], int, None] = None,
        axis_names: Optional[str] = None,
        bytes_per_sample_hint: Union[Sequence[int], int, None] = [0],
        keep_dims: Optional[bool] = False,
        preserve: Optional[bool] = False,
    ) -> None: ...
    @overload
    def __call__(
        self,
        input: Union[DataNode, TensorLikeIn],
        /,
        *,
        device: Optional[Literal["cpu", "gpu"]] = None,
        name: Optional[str] = None,
        axes: Union[Sequence[int], int, None] = None,
        axis_names: Optional[str] = None,
        bytes_per_sample_hint: Union[Sequence[int], int, None] = [0],
        keep_dims: Optional[bool] = False,
        preserve: Optional[bool] = False,
    ) -> DataNode:
        """
        Operator call to be used in graph definition.

        Args
        ----
        input : TensorList
            Input to the operator.

        """
        ...

    @overload
    def __call__(
        self,
        input: List[DataNode],
        /,
        *,
        device: Optional[Literal["cpu", "gpu"]] = None,
        name: Optional[str] = None,
        axes: Union[Sequence[int], int, None] = None,
        axis_names: Optional[str] = None,
        bytes_per_sample_hint: Union[Sequence[int], int, None] = [0],
        keep_dims: Optional[bool] = False,
        preserve: Optional[bool] = False,
    ) -> Union[DataNode, List[DataNode]]:
        """
        Operator call to be used in graph definition.

        Args
        ----
        input : TensorList
            Input to the operator.

        """
        ...

class Mean:
    """
    Gets mean of elements along provided axes.

    Supported backends
     * 'cpu'
     * 'gpu'


    Keyword args
    ------------
    axes : int or list of int, optional
        Axis or axes along which reduction is performed.

        Accepted range is [-ndim, ndim-1]. Negative indices are counted from the back.

        Not providing any axis results in reduction of all elements.
    axis_names : :ref:`layout str<layout_str_doc>`, optional
        Name(s) of the axis or axes along which the reduction is performed.

        The input layout is used to translate the axis names to axis indices, for example ``axis_names="HW"`` with input
        layout `"FHWC"` is equivalent to specifying ``axes=[1,2]``. This argument cannot be used together with `axes`.
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    dtype : :class:`nvidia.dali.types.DALIDataType`, optional
        Output data type. This type is used to accumulate the result.
    keep_dims : bool, optional, default = `False`
        If True, maintains original input dimensions.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.

    """

    def __init__(
        self,
        /,
        *,
        device: Optional[Literal["cpu", "gpu"]] = None,
        name: Optional[str] = None,
        axes: Union[Sequence[int], int, None] = None,
        axis_names: Optional[str] = None,
        bytes_per_sample_hint: Union[Sequence[int], int, None] = [0],
        dtype: Optional[DALIDataType] = None,
        keep_dims: Optional[bool] = False,
        preserve: Optional[bool] = False,
    ) -> None: ...
    @overload
    def __call__(
        self,
        input: Union[DataNode, TensorLikeIn],
        /,
        *,
        device: Optional[Literal["cpu", "gpu"]] = None,
        name: Optional[str] = None,
        axes: Union[Sequence[int], int, None] = None,
        axis_names: Optional[str] = None,
        bytes_per_sample_hint: Union[Sequence[int], int, None] = [0],
        dtype: Optional[DALIDataType] = None,
        keep_dims: Optional[bool] = False,
        preserve: Optional[bool] = False,
    ) -> DataNode:
        """
        Operator call to be used in graph definition.

        Args
        ----
        input : TensorList
            Input to the operator.

        """
        ...

    @overload
    def __call__(
        self,
        input: List[DataNode],
        /,
        *,
        device: Optional[Literal["cpu", "gpu"]] = None,
        name: Optional[str] = None,
        axes: Union[Sequence[int], int, None] = None,
        axis_names: Optional[str] = None,
        bytes_per_sample_hint: Union[Sequence[int], int, None] = [0],
        dtype: Optional[DALIDataType] = None,
        keep_dims: Optional[bool] = False,
        preserve: Optional[bool] = False,
    ) -> Union[DataNode, List[DataNode]]:
        """
        Operator call to be used in graph definition.

        Args
        ----
        input : TensorList
            Input to the operator.

        """
        ...

class MeanSquare:
    """
    Gets mean square of elements along provided axes.

    Supported backends
     * 'cpu'
     * 'gpu'


    Keyword args
    ------------
    axes : int or list of int, optional
        Axis or axes along which reduction is performed.

        Accepted range is [-ndim, ndim-1]. Negative indices are counted from the back.

        Not providing any axis results in reduction of all elements.
    axis_names : :ref:`layout str<layout_str_doc>`, optional
        Name(s) of the axis or axes along which the reduction is performed.

        The input layout is used to translate the axis names to axis indices, for example ``axis_names="HW"`` with input
        layout `"FHWC"` is equivalent to specifying ``axes=[1,2]``. This argument cannot be used together with `axes`.
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    dtype : :class:`nvidia.dali.types.DALIDataType`, optional
        Output data type. This type is used to accumulate the result.
    keep_dims : bool, optional, default = `False`
        If True, maintains original input dimensions.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.

    """

    def __init__(
        self,
        /,
        *,
        device: Optional[Literal["cpu", "gpu"]] = None,
        name: Optional[str] = None,
        axes: Union[Sequence[int], int, None] = None,
        axis_names: Optional[str] = None,
        bytes_per_sample_hint: Union[Sequence[int], int, None] = [0],
        dtype: Optional[DALIDataType] = None,
        keep_dims: Optional[bool] = False,
        preserve: Optional[bool] = False,
    ) -> None: ...
    @overload
    def __call__(
        self,
        input: Union[DataNode, TensorLikeIn],
        /,
        *,
        device: Optional[Literal["cpu", "gpu"]] = None,
        name: Optional[str] = None,
        axes: Union[Sequence[int], int, None] = None,
        axis_names: Optional[str] = None,
        bytes_per_sample_hint: Union[Sequence[int], int, None] = [0],
        dtype: Optional[DALIDataType] = None,
        keep_dims: Optional[bool] = False,
        preserve: Optional[bool] = False,
    ) -> DataNode:
        """
        Operator call to be used in graph definition.

        Args
        ----
        input : TensorList
            Input to the operator.

        """
        ...

    @overload
    def __call__(
        self,
        input: List[DataNode],
        /,
        *,
        device: Optional[Literal["cpu", "gpu"]] = None,
        name: Optional[str] = None,
        axes: Union[Sequence[int], int, None] = None,
        axis_names: Optional[str] = None,
        bytes_per_sample_hint: Union[Sequence[int], int, None] = [0],
        dtype: Optional[DALIDataType] = None,
        keep_dims: Optional[bool] = False,
        preserve: Optional[bool] = False,
    ) -> Union[DataNode, List[DataNode]]:
        """
        Operator call to be used in graph definition.

        Args
        ----
        input : TensorList
            Input to the operator.

        """
        ...

class Min:
    """
    Gets minimal input element along provided axes.

    Supported backends
     * 'cpu'
     * 'gpu'


    Keyword args
    ------------
    axes : int or list of int, optional
        Axis or axes along which reduction is performed.

        Accepted range is [-ndim, ndim-1]. Negative indices are counted from the back.

        Not providing any axis results in reduction of all elements.
    axis_names : :ref:`layout str<layout_str_doc>`, optional
        Name(s) of the axis or axes along which the reduction is performed.

        The input layout is used to translate the axis names to axis indices, for example ``axis_names="HW"`` with input
        layout `"FHWC"` is equivalent to specifying ``axes=[1,2]``. This argument cannot be used together with `axes`.
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    keep_dims : bool, optional, default = `False`
        If True, maintains original input dimensions.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.

    """

    def __init__(
        self,
        /,
        *,
        device: Optional[Literal["cpu", "gpu"]] = None,
        name: Optional[str] = None,
        axes: Union[Sequence[int], int, None] = None,
        axis_names: Optional[str] = None,
        bytes_per_sample_hint: Union[Sequence[int], int, None] = [0],
        keep_dims: Optional[bool] = False,
        preserve: Optional[bool] = False,
    ) -> None: ...
    @overload
    def __call__(
        self,
        input: Union[DataNode, TensorLikeIn],
        /,
        *,
        device: Optional[Literal["cpu", "gpu"]] = None,
        name: Optional[str] = None,
        axes: Union[Sequence[int], int, None] = None,
        axis_names: Optional[str] = None,
        bytes_per_sample_hint: Union[Sequence[int], int, None] = [0],
        keep_dims: Optional[bool] = False,
        preserve: Optional[bool] = False,
    ) -> DataNode:
        """
        Operator call to be used in graph definition.

        Args
        ----
        input : TensorList
            Input to the operator.

        """
        ...

    @overload
    def __call__(
        self,
        input: List[DataNode],
        /,
        *,
        device: Optional[Literal["cpu", "gpu"]] = None,
        name: Optional[str] = None,
        axes: Union[Sequence[int], int, None] = None,
        axis_names: Optional[str] = None,
        bytes_per_sample_hint: Union[Sequence[int], int, None] = [0],
        keep_dims: Optional[bool] = False,
        preserve: Optional[bool] = False,
    ) -> Union[DataNode, List[DataNode]]:
        """
        Operator call to be used in graph definition.

        Args
        ----
        input : TensorList
            Input to the operator.

        """
        ...

class RMS:
    """
    Gets root mean square of elements along provided axes.

    Supported backends
     * 'cpu'
     * 'gpu'


    Keyword args
    ------------
    axes : int or list of int, optional
        Axis or axes along which reduction is performed.

        Accepted range is [-ndim, ndim-1]. Negative indices are counted from the back.

        Not providing any axis results in reduction of all elements.
    axis_names : :ref:`layout str<layout_str_doc>`, optional
        Name(s) of the axis or axes along which the reduction is performed.

        The input layout is used to translate the axis names to axis indices, for example ``axis_names="HW"`` with input
        layout `"FHWC"` is equivalent to specifying ``axes=[1,2]``. This argument cannot be used together with `axes`.
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    dtype : :class:`nvidia.dali.types.DALIDataType`, optional
        Output data type. This type is used to accumulate the result.
    keep_dims : bool, optional, default = `False`
        If True, maintains original input dimensions.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.

    """

    def __init__(
        self,
        /,
        *,
        device: Optional[Literal["cpu", "gpu"]] = None,
        name: Optional[str] = None,
        axes: Union[Sequence[int], int, None] = None,
        axis_names: Optional[str] = None,
        bytes_per_sample_hint: Union[Sequence[int], int, None] = [0],
        dtype: Optional[DALIDataType] = None,
        keep_dims: Optional[bool] = False,
        preserve: Optional[bool] = False,
    ) -> None: ...
    @overload
    def __call__(
        self,
        input: Union[DataNode, TensorLikeIn],
        /,
        *,
        device: Optional[Literal["cpu", "gpu"]] = None,
        name: Optional[str] = None,
        axes: Union[Sequence[int], int, None] = None,
        axis_names: Optional[str] = None,
        bytes_per_sample_hint: Union[Sequence[int], int, None] = [0],
        dtype: Optional[DALIDataType] = None,
        keep_dims: Optional[bool] = False,
        preserve: Optional[bool] = False,
    ) -> DataNode:
        """
        Operator call to be used in graph definition.

        Args
        ----
        input : TensorList
            Input to the operator.

        """
        ...

    @overload
    def __call__(
        self,
        input: List[DataNode],
        /,
        *,
        device: Optional[Literal["cpu", "gpu"]] = None,
        name: Optional[str] = None,
        axes: Union[Sequence[int], int, None] = None,
        axis_names: Optional[str] = None,
        bytes_per_sample_hint: Union[Sequence[int], int, None] = [0],
        dtype: Optional[DALIDataType] = None,
        keep_dims: Optional[bool] = False,
        preserve: Optional[bool] = False,
    ) -> Union[DataNode, List[DataNode]]:
        """
        Operator call to be used in graph definition.

        Args
        ----
        input : TensorList
            Input to the operator.

        """
        ...

class StdDev:
    """
    Gets standard deviation of elements along provided axes.

    Supported backends
     * 'cpu'
     * 'gpu'


    Keyword args
    ------------
    axes : int or list of int, optional
        Axis or axes along which reduction is performed.

        Accepted range is [-ndim, ndim-1]. Negative indices are counted from the back.

        Not providing any axis results in reduction of all elements.
    axis_names : :ref:`layout str<layout_str_doc>`, optional
        Name(s) of the axis or axes along which the reduction is performed.

        The input layout is used to translate the axis names to axis indices, for example ``axis_names="HW"`` with input
        layout `"FHWC"` is equivalent to specifying ``axes=[1,2]``. This argument cannot be used together with `axes`.
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    ddof : int, optional, default = `0`
        Delta Degrees of Freedom. Adjusts the divisor used in calculations, which is `N - ddof`.
    keep_dims : bool, optional, default = `False`
        If True, maintains original input dimensions.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.

    """

    def __init__(
        self,
        /,
        *,
        device: Optional[Literal["cpu", "gpu"]] = None,
        name: Optional[str] = None,
        axes: Union[Sequence[int], int, None] = None,
        axis_names: Optional[str] = None,
        bytes_per_sample_hint: Union[Sequence[int], int, None] = [0],
        ddof: Optional[int] = 0,
        keep_dims: Optional[bool] = False,
        preserve: Optional[bool] = False,
    ) -> None: ...
    @overload
    def __call__(
        self,
        data: Union[DataNode, TensorLikeIn],
        mean: Union[DataNode, TensorLikeIn],
        /,
        *,
        device: Optional[Literal["cpu", "gpu"]] = None,
        name: Optional[str] = None,
        axes: Union[Sequence[int], int, None] = None,
        axis_names: Optional[str] = None,
        bytes_per_sample_hint: Union[Sequence[int], int, None] = [0],
        ddof: Optional[int] = 0,
        keep_dims: Optional[bool] = False,
        preserve: Optional[bool] = False,
    ) -> DataNode:
        """
        Operator call to be used in graph definition.

        Args
        ----
        data : TensorList
            Input to the operator.
        mean : float or TensorList of float
            Mean value to use in the calculations.


        """
        ...

    @overload
    def __call__(
        self,
        data: Union[List[DataNode], DataNode, TensorLikeIn],
        mean: Union[List[DataNode], DataNode, TensorLikeIn],
        /,
        *,
        device: Optional[Literal["cpu", "gpu"]] = None,
        name: Optional[str] = None,
        axes: Union[Sequence[int], int, None] = None,
        axis_names: Optional[str] = None,
        bytes_per_sample_hint: Union[Sequence[int], int, None] = [0],
        ddof: Optional[int] = 0,
        keep_dims: Optional[bool] = False,
        preserve: Optional[bool] = False,
    ) -> Union[DataNode, List[DataNode]]:
        """
        Operator call to be used in graph definition.

        Args
        ----
        data : TensorList
            Input to the operator.
        mean : float or TensorList of float
            Mean value to use in the calculations.


        """
        ...

class Sum:
    """
    Gets sum of elements along provided axes.

    Supported backends
     * 'cpu'
     * 'gpu'


    Keyword args
    ------------
    axes : int or list of int, optional
        Axis or axes along which reduction is performed.

        Accepted range is [-ndim, ndim-1]. Negative indices are counted from the back.

        Not providing any axis results in reduction of all elements.
    axis_names : :ref:`layout str<layout_str_doc>`, optional
        Name(s) of the axis or axes along which the reduction is performed.

        The input layout is used to translate the axis names to axis indices, for example ``axis_names="HW"`` with input
        layout `"FHWC"` is equivalent to specifying ``axes=[1,2]``. This argument cannot be used together with `axes`.
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    dtype : :class:`nvidia.dali.types.DALIDataType`, optional
        Output data type. This type is used to accumulate the result.
    keep_dims : bool, optional, default = `False`
        If True, maintains original input dimensions.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.

    """

    def __init__(
        self,
        /,
        *,
        device: Optional[Literal["cpu", "gpu"]] = None,
        name: Optional[str] = None,
        axes: Union[Sequence[int], int, None] = None,
        axis_names: Optional[str] = None,
        bytes_per_sample_hint: Union[Sequence[int], int, None] = [0],
        dtype: Optional[DALIDataType] = None,
        keep_dims: Optional[bool] = False,
        preserve: Optional[bool] = False,
    ) -> None: ...
    @overload
    def __call__(
        self,
        input: Union[DataNode, TensorLikeIn],
        /,
        *,
        device: Optional[Literal["cpu", "gpu"]] = None,
        name: Optional[str] = None,
        axes: Union[Sequence[int], int, None] = None,
        axis_names: Optional[str] = None,
        bytes_per_sample_hint: Union[Sequence[int], int, None] = [0],
        dtype: Optional[DALIDataType] = None,
        keep_dims: Optional[bool] = False,
        preserve: Optional[bool] = False,
    ) -> DataNode:
        """
        Operator call to be used in graph definition.

        Args
        ----
        input : TensorList
            Input to the operator.

        """
        ...

    @overload
    def __call__(
        self,
        input: List[DataNode],
        /,
        *,
        device: Optional[Literal["cpu", "gpu"]] = None,
        name: Optional[str] = None,
        axes: Union[Sequence[int], int, None] = None,
        axis_names: Optional[str] = None,
        bytes_per_sample_hint: Union[Sequence[int], int, None] = [0],
        dtype: Optional[DALIDataType] = None,
        keep_dims: Optional[bool] = False,
        preserve: Optional[bool] = False,
    ) -> Union[DataNode, List[DataNode]]:
        """
        Operator call to be used in graph definition.

        Args
        ----
        input : TensorList
            Input to the operator.

        """
        ...

class Variance:
    """
    Gets variance of elements along provided axes.

    Supported backends
     * 'cpu'
     * 'gpu'


    Keyword args
    ------------
    axes : int or list of int, optional
        Axis or axes along which reduction is performed.

        Accepted range is [-ndim, ndim-1]. Negative indices are counted from the back.

        Not providing any axis results in reduction of all elements.
    axis_names : :ref:`layout str<layout_str_doc>`, optional
        Name(s) of the axis or axes along which the reduction is performed.

        The input layout is used to translate the axis names to axis indices, for example ``axis_names="HW"`` with input
        layout `"FHWC"` is equivalent to specifying ``axes=[1,2]``. This argument cannot be used together with `axes`.
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    ddof : int, optional, default = `0`
        Delta Degrees of Freedom. Adjusts the divisor used in calculations, which is `N - ddof`.
    keep_dims : bool, optional, default = `False`
        If True, maintains original input dimensions.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.

    """

    def __init__(
        self,
        /,
        *,
        device: Optional[Literal["cpu", "gpu"]] = None,
        name: Optional[str] = None,
        axes: Union[Sequence[int], int, None] = None,
        axis_names: Optional[str] = None,
        bytes_per_sample_hint: Union[Sequence[int], int, None] = [0],
        ddof: Optional[int] = 0,
        keep_dims: Optional[bool] = False,
        preserve: Optional[bool] = False,
    ) -> None: ...
    @overload
    def __call__(
        self,
        data: Union[DataNode, TensorLikeIn],
        mean: Union[DataNode, TensorLikeIn],
        /,
        *,
        device: Optional[Literal["cpu", "gpu"]] = None,
        name: Optional[str] = None,
        axes: Union[Sequence[int], int, None] = None,
        axis_names: Optional[str] = None,
        bytes_per_sample_hint: Union[Sequence[int], int, None] = [0],
        ddof: Optional[int] = 0,
        keep_dims: Optional[bool] = False,
        preserve: Optional[bool] = False,
    ) -> DataNode:
        """
        Operator call to be used in graph definition.

        Args
        ----
        data : TensorList
            Input to the operator.
        mean : float or TensorList of float
            Mean value to use in the calculations.


        """
        ...

    @overload
    def __call__(
        self,
        data: Union[List[DataNode], DataNode, TensorLikeIn],
        mean: Union[List[DataNode], DataNode, TensorLikeIn],
        /,
        *,
        device: Optional[Literal["cpu", "gpu"]] = None,
        name: Optional[str] = None,
        axes: Union[Sequence[int], int, None] = None,
        axis_names: Optional[str] = None,
        bytes_per_sample_hint: Union[Sequence[int], int, None] = [0],
        ddof: Optional[int] = 0,
        keep_dims: Optional[bool] = False,
        preserve: Optional[bool] = False,
    ) -> Union[DataNode, List[DataNode]]:
        """
        Operator call to be used in graph definition.

        Args
        ----
        data : TensorList
            Input to the operator.
        mean : float or TensorList of float
            Mean value to use in the calculations.


        """
        ...

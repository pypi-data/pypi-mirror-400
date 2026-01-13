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

"""Random number generator support for DALI dynamic mode.

This module also contains functional wrappers for random operators (e.g., uniform, normal)
that are dynamically added during module initialization.
"""

import random as _random
import threading as _threading

class RNG:
    """Random number generator for DALI dynamic mode operations.

    This RNG can be used to provide reproducible random state to DALI operators.

    Parameters
    ----------
    seed : int, optional
        Seed for the random number generator. If not provided, a random seed is used.

    Examples
    --------
    >>> import nvidia.dali.experimental.dynamic as ndd
    >>>
    >>> # Create an RNG with a specific seed
    >>> my_rng = ndd.random.RNG(seed=1234)
    >>>
    >>> # Use it with random operators
    >>> result = ndd.ops.random.Uniform(device="cpu")(range=(-1, 1), shape=[10], rng=my_rng)
    """

    def __init__(self, seed=None):
        """Initialize the RNG with an optional seed."""
        if seed is None:

            seed = _random.randint(0, 2**31 - 1)
        self._rng = _random.Random(seed)
        self._seed = seed

    def __call__(self):
        """Generate a random uint32 value.

        Returns
        -------
        int
            A random uint32 value (as Python int, but in range [0, 2^32-1]).
        """

        return self._rng.randint(0, 0xFFFFFFFF)

    @property
    def seed(self):
        """Get the seed used to initialize this RNG."""
        return self._seed

    @seed.setter
    def seed(self, value):
        """Set the seed for this RNG and reset its random sequence."""
        self._seed = value
        self._rng = _random.Random(value)

    def clone(self):
        """Create a new RNG with the same seed.

        Returns
        -------
        RNG
            A new RNG instance initialized with the same seed as this one.
            This allows creating independent RNG streams that produce the same
            sequence of random numbers.

        Examples
        --------
        >>> import nvidia.dali.experimental.dynamic as ndd
        >>>
        >>> # Create an RNG
        >>> rng1 = ndd.random.RNG(seed=1234)
        >>>
        >>> # Clone it to create an independent copy
        >>> rng2 = rng1.clone()
        >>>
        >>> # Both will generate the same sequence
        >>> for i in range(10):
        >>>     assert rng1() == rng2()
        """
        return RNG(seed=self._seed)

    def __repr__(self):
        return f"RNG(seed={self._seed})"

_thread_local = _threading.local()

def get_default_rng():
    """Get the default RNG for the current thread.

    Returns
    -------
    RNG
        The default RNG for the current thread.

    Examples
    --------
    >>> import nvidia.dali.experimental.dynamic as ndd
    >>>
    >>> # Get the default RNG
    >>> default = ndd.random.get_default_rng()
    >>> print(default)
    """
    if not hasattr(_thread_local, "default_rng"):
        _thread_local.default_rng = RNG()
    return _thread_local.default_rng

def set_seed(seed):
    """Set the seed for the default thread-local RNG.

    This affects all subsequent calls to random operators that don't specify
    an explicit RNG.

    Parameters
    ----------
    seed : int
        Seed for the random number generator.

    Examples
    --------
    >>> import nvidia.dali.experimental.dynamic as ndd
    >>>
    >>> # Set the seed for reproducible results
    >>> ndd.random.set_seed(1234)
    >>> result1 = ndd.random.uniform(range=(-1, 1), shape=[10])
    >>>
    >>> # Reset to the same seed
    >>> ndd.random.set_seed(1234)
    >>> result2 = ndd.random.uniform(range=(-1, 1), shape=[10])
    >>> # result1 and result2 should be identical
    """
    get_default_rng().seed = seed

@overload
def beta(
    shape_like: Optional[TensorLike] = None,
    /,
    *,
    device: Optional[Literal["cpu"]] = None,
    rng: Optional[RNG] = None,
    alpha: Union[TensorLikeArg, Batch, float, None] = 1.0,
    beta: Union[TensorLikeArg, Batch, float, None] = 1.0,
    dtype: Union[DALIDataType, DType, None] = None,
    seed: Optional[int] = -1,
    shape: Union[TensorLikeArg, Batch, Sequence[int], int, None] = None,
) -> Union[Tensor, Batch]:
    """
    Generates a random number from ``[0, 1]`` range following the beta distribution.

    The beta distribution has the following probabilty distribution function:

    .. math:: f(x) = \frac{\Gamma(\alpha + \beta)}{\Gamma(\alpha)\Gamma(\beta)} x^{\alpha-1} (1-x)^{\beta-1}

    where ``Г`` is the gamma function defined as:

    .. math:: \Gamma(\alpha) = \int_0^\infty x^{\alpha-1} e^{-x} \, dx

    The operator supports ``float32`` and ``float64`` output types.

    The shape of the generated data can be either specified explicitly with a `shape` argument,
    or chosen to match the shape of the `__shape_like` input, if provided. If none are present,
    a single value per sample is generated.


    Supported backends
     * 'cpu'


    Args
    ----
    shape_like : Tensor/Batch, optional
        Shape of this input will be used to infer the shape of the output, if provided.


    Keyword args
    ------------
    alpha : float or Tensor/Batch of float, optional, default = `1.0`
        The alpha parameter, a positive ``float32`` scalar.
    beta : float or Tensor/Batch of float, optional, default = `1.0`
        The beta parameter, a positive ``float32`` scalar.
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    dtype : :class:`nvidia.dali.types.DALIDataType`, optional
        Output data type.

        .. note::
          The generated numbers are converted to the output data type, rounding and clamping if necessary.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.
    seed : int, optional, default = `-1`
        Random seed; if not set, one will be assigned automatically.
    shape : int or list of int or Tensor/Batch of int, optional
        Shape of the output data.

    """

@overload
def beta(
    shape_like: Optional[TensorLike] = None,
    /,
    *,
    device: Optional[Literal["cpu"]] = None,
    rng: Optional[RNG] = None,
    batch_size: int,
    alpha: Union[TensorLikeArg, Batch, float, None] = 1.0,
    beta: Union[TensorLikeArg, Batch, float, None] = 1.0,
    dtype: Union[DALIDataType, DType, None] = None,
    seed: Optional[int] = -1,
    shape: Union[TensorLikeArg, Batch, Sequence[int], int, None] = None,
) -> Batch:
    """
    Generates a random number from ``[0, 1]`` range following the beta distribution.

    The beta distribution has the following probabilty distribution function:

    .. math:: f(x) = \frac{\Gamma(\alpha + \beta)}{\Gamma(\alpha)\Gamma(\beta)} x^{\alpha-1} (1-x)^{\beta-1}

    where ``Г`` is the gamma function defined as:

    .. math:: \Gamma(\alpha) = \int_0^\infty x^{\alpha-1} e^{-x} \, dx

    The operator supports ``float32`` and ``float64`` output types.

    The shape of the generated data can be either specified explicitly with a `shape` argument,
    or chosen to match the shape of the `__shape_like` input, if provided. If none are present,
    a single value per sample is generated.


    Supported backends
     * 'cpu'


    Args
    ----
    shape_like : Tensor/Batch, optional
        Shape of this input will be used to infer the shape of the output, if provided.


    Keyword args
    ------------
    alpha : float or Tensor/Batch of float, optional, default = `1.0`
        The alpha parameter, a positive ``float32`` scalar.
    beta : float or Tensor/Batch of float, optional, default = `1.0`
        The beta parameter, a positive ``float32`` scalar.
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    dtype : :class:`nvidia.dali.types.DALIDataType`, optional
        Output data type.

        .. note::
          The generated numbers are converted to the output data type, rounding and clamping if necessary.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.
    seed : int, optional, default = `-1`
        Random seed; if not set, one will be assigned automatically.
    shape : int or list of int or Tensor/Batch of int, optional
        Shape of the output data.

    """

@overload
def beta(
    shape_like: Optional[Batch] = None,
    /,
    *,
    device: Optional[Literal["cpu"]] = None,
    rng: Optional[RNG] = None,
    alpha: Union[TensorLikeArg, Batch, float, None] = 1.0,
    beta: Union[TensorLikeArg, Batch, float, None] = 1.0,
    dtype: Union[DALIDataType, DType, None] = None,
    seed: Optional[int] = -1,
    shape: Union[TensorLikeArg, Batch, Sequence[int], int, None] = None,
) -> Batch:
    """
    Generates a random number from ``[0, 1]`` range following the beta distribution.

    The beta distribution has the following probabilty distribution function:

    .. math:: f(x) = \frac{\Gamma(\alpha + \beta)}{\Gamma(\alpha)\Gamma(\beta)} x^{\alpha-1} (1-x)^{\beta-1}

    where ``Г`` is the gamma function defined as:

    .. math:: \Gamma(\alpha) = \int_0^\infty x^{\alpha-1} e^{-x} \, dx

    The operator supports ``float32`` and ``float64`` output types.

    The shape of the generated data can be either specified explicitly with a `shape` argument,
    or chosen to match the shape of the `__shape_like` input, if provided. If none are present,
    a single value per sample is generated.


    Supported backends
     * 'cpu'


    Args
    ----
    shape_like : Tensor/Batch, optional
        Shape of this input will be used to infer the shape of the output, if provided.


    Keyword args
    ------------
    alpha : float or Tensor/Batch of float, optional, default = `1.0`
        The alpha parameter, a positive ``float32`` scalar.
    beta : float or Tensor/Batch of float, optional, default = `1.0`
        The beta parameter, a positive ``float32`` scalar.
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    dtype : :class:`nvidia.dali.types.DALIDataType`, optional
        Output data type.

        .. note::
          The generated numbers are converted to the output data type, rounding and clamping if necessary.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.
    seed : int, optional, default = `-1`
        Random seed; if not set, one will be assigned automatically.
    shape : int or list of int or Tensor/Batch of int, optional
        Shape of the output data.

    """

@overload
def choice(
    a: Batch,
    shape_like: Optional[Batch] = None,
    /,
    *,
    device: Optional[Literal["cpu"]] = None,
    rng: Optional[RNG] = None,
    p: Union[TensorLikeArg, Batch, Sequence[float], float, None] = None,
    seed: Optional[int] = -1,
    shape: Union[TensorLikeArg, Batch, Sequence[int], int, None] = None,
) -> Batch:
    """
    Generates a random sample from a given 1D array.

    The probability of selecting a sample from the input is determined by the corresponding probability
    specified in `p` argument.

    The shape of the generated data can be either specified explicitly with a `shape` argument,
    or chosen to match the shape of the `__shape_like` input, if provided. If none are present,
    a single value per sample is generated.

    The type of the output matches the type of the input.
    For scalar inputs, only integral types are supported, otherwise any type can be used.
    The operator supports selection from an input containing elements of one of DALI enum types,
    that is: :meth:`nvidia.dali.types.DALIDataType`, :meth:`nvidia.dali.types.DALIImageType`, or
    :meth:`nvidia.dali.types.DALIInterpType`.


    Supported backends
     * 'cpu'


    Args
    ----
    a : scalar or Tensor/Batch
        If a scalar value `__a` is provided, the operator behaves as if ``[0, 1, ..., __a-1]`` list was passed as input. Otherwise `__a` is treated as 1D array of input samples.
    shape_like : Tensor/Batch, optional
        Shape of this input will be used to infer the shape of the output, if provided.


    Keyword args
    ------------
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    p : float or list of float or Tensor/Batch of float, optional
        Distribution of the probabilities. If not specified, uniform distribution is assumed.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.
    seed : int, optional, default = `-1`
        Random seed; if not set, one will be assigned automatically.
    shape : int or list of int or Tensor/Batch of int, optional
        Shape of the output data.

    """

@overload
def choice(
    a: Union[TensorLike, Batch],
    shape_like: Union[TensorLike, Batch, None] = None,
    /,
    *,
    device: Optional[Literal["cpu"]] = None,
    rng: Optional[RNG] = None,
    p: Union[TensorLikeArg, Batch, Sequence[float], float, None] = None,
    seed: Optional[int] = -1,
    shape: Union[TensorLikeArg, Batch, Sequence[int], int, None] = None,
) -> Union[Tensor, Batch]:
    """
    Generates a random sample from a given 1D array.

    The probability of selecting a sample from the input is determined by the corresponding probability
    specified in `p` argument.

    The shape of the generated data can be either specified explicitly with a `shape` argument,
    or chosen to match the shape of the `__shape_like` input, if provided. If none are present,
    a single value per sample is generated.

    The type of the output matches the type of the input.
    For scalar inputs, only integral types are supported, otherwise any type can be used.
    The operator supports selection from an input containing elements of one of DALI enum types,
    that is: :meth:`nvidia.dali.types.DALIDataType`, :meth:`nvidia.dali.types.DALIImageType`, or
    :meth:`nvidia.dali.types.DALIInterpType`.


    Supported backends
     * 'cpu'


    Args
    ----
    a : scalar or Tensor/Batch
        If a scalar value `__a` is provided, the operator behaves as if ``[0, 1, ..., __a-1]`` list was passed as input. Otherwise `__a` is treated as 1D array of input samples.
    shape_like : Tensor/Batch, optional
        Shape of this input will be used to infer the shape of the output, if provided.


    Keyword args
    ------------
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    p : float or list of float or Tensor/Batch of float, optional
        Distribution of the probabilities. If not specified, uniform distribution is assumed.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.
    seed : int, optional, default = `-1`
        Random seed; if not set, one will be assigned automatically.
    shape : int or list of int or Tensor/Batch of int, optional
        Shape of the output data.

    """

@overload
def choice(
    a: Union[TensorLike, Batch],
    shape_like: Union[TensorLike, Batch, None] = None,
    /,
    *,
    device: Optional[Literal["cpu"]] = None,
    rng: Optional[RNG] = None,
    batch_size: int,
    p: Union[TensorLikeArg, Batch, Sequence[float], float, None] = None,
    seed: Optional[int] = -1,
    shape: Union[TensorLikeArg, Batch, Sequence[int], int, None] = None,
) -> Batch:
    """
    Generates a random sample from a given 1D array.

    The probability of selecting a sample from the input is determined by the corresponding probability
    specified in `p` argument.

    The shape of the generated data can be either specified explicitly with a `shape` argument,
    or chosen to match the shape of the `__shape_like` input, if provided. If none are present,
    a single value per sample is generated.

    The type of the output matches the type of the input.
    For scalar inputs, only integral types are supported, otherwise any type can be used.
    The operator supports selection from an input containing elements of one of DALI enum types,
    that is: :meth:`nvidia.dali.types.DALIDataType`, :meth:`nvidia.dali.types.DALIImageType`, or
    :meth:`nvidia.dali.types.DALIInterpType`.


    Supported backends
     * 'cpu'


    Args
    ----
    a : scalar or Tensor/Batch
        If a scalar value `__a` is provided, the operator behaves as if ``[0, 1, ..., __a-1]`` list was passed as input. Otherwise `__a` is treated as 1D array of input samples.
    shape_like : Tensor/Batch, optional
        Shape of this input will be used to infer the shape of the output, if provided.


    Keyword args
    ------------
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    p : float or list of float or Tensor/Batch of float, optional
        Distribution of the probabilities. If not specified, uniform distribution is assumed.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.
    seed : int, optional, default = `-1`
        Random seed; if not set, one will be assigned automatically.
    shape : int or list of int or Tensor/Batch of int, optional
        Shape of the output data.

    """

@overload
def coin_flip(
    shape_like: Optional[TensorLike] = None,
    /,
    *,
    device: Optional[Literal["cpu", "gpu"]] = None,
    rng: Optional[RNG] = None,
    dtype: Union[DALIDataType, DType, None] = None,
    probability: Union[TensorLikeArg, Batch, float, None] = 0.5,
    seed: Optional[int] = -1,
    shape: Union[TensorLikeArg, Batch, Sequence[int], int, None] = None,
) -> Union[Tensor, Batch]:
    """
    Generates random boolean values following a bernoulli distribution.

    The probability of generating a value 1 (true) is determined by the `probability` argument.

    The shape of the generated data can be either specified explicitly with a `shape` argument,
    or chosen to match the shape of the `__shape_like` input, if provided. If none are present,
    a single value per sample is generated.


    Supported backends
     * 'cpu'
     * 'gpu'


    Args
    ----
    shape_like : Tensor/Batch, optional
        Shape of this input will be used to infer the shape of the output, if provided.


    Keyword args
    ------------
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    dtype : :class:`nvidia.dali.types.DALIDataType`, optional
        Output data type.

        .. note::
          The generated numbers are converted to the output data type, rounding and clamping if necessary.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.
    probability : float or Tensor/Batch of float, optional, default = `0.5`
        Probability of value 1.
    seed : int, optional, default = `-1`
        Random seed; if not set, one will be assigned automatically.
    shape : int or list of int or Tensor/Batch of int, optional
        Shape of the output data.

    """

@overload
def coin_flip(
    shape_like: Optional[TensorLike] = None,
    /,
    *,
    device: Optional[Literal["cpu", "gpu"]] = None,
    rng: Optional[RNG] = None,
    batch_size: int,
    dtype: Union[DALIDataType, DType, None] = None,
    probability: Union[TensorLikeArg, Batch, float, None] = 0.5,
    seed: Optional[int] = -1,
    shape: Union[TensorLikeArg, Batch, Sequence[int], int, None] = None,
) -> Batch:
    """
    Generates random boolean values following a bernoulli distribution.

    The probability of generating a value 1 (true) is determined by the `probability` argument.

    The shape of the generated data can be either specified explicitly with a `shape` argument,
    or chosen to match the shape of the `__shape_like` input, if provided. If none are present,
    a single value per sample is generated.


    Supported backends
     * 'cpu'
     * 'gpu'


    Args
    ----
    shape_like : Tensor/Batch, optional
        Shape of this input will be used to infer the shape of the output, if provided.


    Keyword args
    ------------
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    dtype : :class:`nvidia.dali.types.DALIDataType`, optional
        Output data type.

        .. note::
          The generated numbers are converted to the output data type, rounding and clamping if necessary.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.
    probability : float or Tensor/Batch of float, optional, default = `0.5`
        Probability of value 1.
    seed : int, optional, default = `-1`
        Random seed; if not set, one will be assigned automatically.
    shape : int or list of int or Tensor/Batch of int, optional
        Shape of the output data.

    """

@overload
def coin_flip(
    shape_like: Optional[Batch] = None,
    /,
    *,
    device: Optional[Literal["cpu", "gpu"]] = None,
    rng: Optional[RNG] = None,
    dtype: Union[DALIDataType, DType, None] = None,
    probability: Union[TensorLikeArg, Batch, float, None] = 0.5,
    seed: Optional[int] = -1,
    shape: Union[TensorLikeArg, Batch, Sequence[int], int, None] = None,
) -> Batch:
    """
    Generates random boolean values following a bernoulli distribution.

    The probability of generating a value 1 (true) is determined by the `probability` argument.

    The shape of the generated data can be either specified explicitly with a `shape` argument,
    or chosen to match the shape of the `__shape_like` input, if provided. If none are present,
    a single value per sample is generated.


    Supported backends
     * 'cpu'
     * 'gpu'


    Args
    ----
    shape_like : Tensor/Batch, optional
        Shape of this input will be used to infer the shape of the output, if provided.


    Keyword args
    ------------
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    dtype : :class:`nvidia.dali.types.DALIDataType`, optional
        Output data type.

        .. note::
          The generated numbers are converted to the output data type, rounding and clamping if necessary.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.
    probability : float or Tensor/Batch of float, optional, default = `0.5`
        Probability of value 1.
    seed : int, optional, default = `-1`
        Random seed; if not set, one will be assigned automatically.
    shape : int or list of int or Tensor/Batch of int, optional
        Shape of the output data.

    """

@overload
def normal(
    shape_like: Optional[TensorLike] = None,
    /,
    *,
    device: Optional[Literal["cpu", "gpu"]] = None,
    rng: Optional[RNG] = None,
    dtype: Union[DALIDataType, DType, None] = None,
    mean: Union[TensorLikeArg, Batch, float, None] = 0.0,
    seed: Optional[int] = -1,
    shape: Union[TensorLikeArg, Batch, Sequence[int], int, None] = None,
    stddev: Union[TensorLikeArg, Batch, float, None] = 1.0,
) -> Union[Tensor, Batch]:
    """
    Generates random numbers following a normal distribution.

    The shape of the generated data can be either specified explicitly with a `shape` argument,
    or chosen to match the shape of the `__shape_like` input, if provided. If none are present,
    a single value per sample is generated.


    Supported backends
     * 'cpu'
     * 'gpu'


    Args
    ----
    shape_like : Tensor/Batch, optional
        Shape of this input will be used to infer the shape of the output, if provided.


    Keyword args
    ------------
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    dtype : :class:`nvidia.dali.types.DALIDataType`, optional
        Output data type.

        .. note::
          The generated numbers are converted to the output data type, rounding and clamping if necessary.
    mean : float or Tensor/Batch of float, optional, default = `0.0`
        Mean of the distribution.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.
    seed : int, optional, default = `-1`
        Random seed; if not set, one will be assigned automatically.
    shape : int or list of int or Tensor/Batch of int, optional
        Shape of the output data.
    stddev : float or Tensor/Batch of float, optional, default = `1.0`
        Standard deviation of the distribution.

    """

@overload
def normal(
    shape_like: Optional[TensorLike] = None,
    /,
    *,
    device: Optional[Literal["cpu", "gpu"]] = None,
    rng: Optional[RNG] = None,
    batch_size: int,
    dtype: Union[DALIDataType, DType, None] = None,
    mean: Union[TensorLikeArg, Batch, float, None] = 0.0,
    seed: Optional[int] = -1,
    shape: Union[TensorLikeArg, Batch, Sequence[int], int, None] = None,
    stddev: Union[TensorLikeArg, Batch, float, None] = 1.0,
) -> Batch:
    """
    Generates random numbers following a normal distribution.

    The shape of the generated data can be either specified explicitly with a `shape` argument,
    or chosen to match the shape of the `__shape_like` input, if provided. If none are present,
    a single value per sample is generated.


    Supported backends
     * 'cpu'
     * 'gpu'


    Args
    ----
    shape_like : Tensor/Batch, optional
        Shape of this input will be used to infer the shape of the output, if provided.


    Keyword args
    ------------
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    dtype : :class:`nvidia.dali.types.DALIDataType`, optional
        Output data type.

        .. note::
          The generated numbers are converted to the output data type, rounding and clamping if necessary.
    mean : float or Tensor/Batch of float, optional, default = `0.0`
        Mean of the distribution.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.
    seed : int, optional, default = `-1`
        Random seed; if not set, one will be assigned automatically.
    shape : int or list of int or Tensor/Batch of int, optional
        Shape of the output data.
    stddev : float or Tensor/Batch of float, optional, default = `1.0`
        Standard deviation of the distribution.

    """

@overload
def normal(
    shape_like: Optional[Batch] = None,
    /,
    *,
    device: Optional[Literal["cpu", "gpu"]] = None,
    rng: Optional[RNG] = None,
    dtype: Union[DALIDataType, DType, None] = None,
    mean: Union[TensorLikeArg, Batch, float, None] = 0.0,
    seed: Optional[int] = -1,
    shape: Union[TensorLikeArg, Batch, Sequence[int], int, None] = None,
    stddev: Union[TensorLikeArg, Batch, float, None] = 1.0,
) -> Batch:
    """
    Generates random numbers following a normal distribution.

    The shape of the generated data can be either specified explicitly with a `shape` argument,
    or chosen to match the shape of the `__shape_like` input, if provided. If none are present,
    a single value per sample is generated.


    Supported backends
     * 'cpu'
     * 'gpu'


    Args
    ----
    shape_like : Tensor/Batch, optional
        Shape of this input will be used to infer the shape of the output, if provided.


    Keyword args
    ------------
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    dtype : :class:`nvidia.dali.types.DALIDataType`, optional
        Output data type.

        .. note::
          The generated numbers are converted to the output data type, rounding and clamping if necessary.
    mean : float or Tensor/Batch of float, optional, default = `0.0`
        Mean of the distribution.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.
    seed : int, optional, default = `-1`
        Random seed; if not set, one will be assigned automatically.
    shape : int or list of int or Tensor/Batch of int, optional
        Shape of the output data.
    stddev : float or Tensor/Batch of float, optional, default = `1.0`
        Standard deviation of the distribution.

    """

@overload
def uniform(
    shape_like: Optional[TensorLike] = None,
    /,
    *,
    device: Optional[Literal["cpu", "gpu"]] = None,
    rng: Optional[RNG] = None,
    dtype: Union[DALIDataType, DType, None] = None,
    range: Union[TensorLikeArg, Batch, Sequence[float], float, None] = [-1.0, 1.0],
    seed: Optional[int] = -1,
    shape: Union[TensorLikeArg, Batch, Sequence[int], int, None] = None,
    values: Union[TensorLikeArg, Batch, Sequence[float], float, None] = None,
) -> Union[Tensor, Batch]:
    """
    Generates random numbers following a uniform distribution.

    It can be configured to produce a continuous uniform distribution in the `range` [min, max),
    or a discrete uniform distribution where any of the specified `values` [v0, v1, ..., vn] occur
    with equal probability.

    The shape of the generated data can be either specified explicitly with a `shape` argument,
    or chosen to match the shape of the `__shape_like` input, if provided. If none are present,
    a single value per sample is generated.


    Supported backends
     * 'cpu'
     * 'gpu'


    Args
    ----
    shape_like : Tensor/Batch, optional
        Shape of this input will be used to infer the shape of the output, if provided.


    Keyword args
    ------------
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    dtype : :class:`nvidia.dali.types.DALIDataType`, optional
        Output data type.

        .. note::
          The generated numbers are converted to the output data type, rounding and clamping if necessary.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.
    range : float or list of float or Tensor/Batch of float, optional, default = `[-1.0, 1.0]`
        Range ``[min, max)`` of a continuous uniform distribution.

        This argument is mutually exclusive with `values`.

        .. warning::
          When specifying an integer type as `dtype`, the generated numbers can go outside
          the specified range, due to rounding.
    seed : int, optional, default = `-1`
        Random seed; if not set, one will be assigned automatically.
    shape : int or list of int or Tensor/Batch of int, optional
        Shape of the output data.
    values : float or list of float or Tensor/Batch of float, optional
        The discrete values [v0, v1, ..., vn] produced by a discrete uniform distribution.

        This argument is mutually exclusive with `range`.

    """

@overload
def uniform(
    shape_like: Optional[TensorLike] = None,
    /,
    *,
    device: Optional[Literal["cpu", "gpu"]] = None,
    rng: Optional[RNG] = None,
    batch_size: int,
    dtype: Union[DALIDataType, DType, None] = None,
    range: Union[TensorLikeArg, Batch, Sequence[float], float, None] = [-1.0, 1.0],
    seed: Optional[int] = -1,
    shape: Union[TensorLikeArg, Batch, Sequence[int], int, None] = None,
    values: Union[TensorLikeArg, Batch, Sequence[float], float, None] = None,
) -> Batch:
    """
    Generates random numbers following a uniform distribution.

    It can be configured to produce a continuous uniform distribution in the `range` [min, max),
    or a discrete uniform distribution where any of the specified `values` [v0, v1, ..., vn] occur
    with equal probability.

    The shape of the generated data can be either specified explicitly with a `shape` argument,
    or chosen to match the shape of the `__shape_like` input, if provided. If none are present,
    a single value per sample is generated.


    Supported backends
     * 'cpu'
     * 'gpu'


    Args
    ----
    shape_like : Tensor/Batch, optional
        Shape of this input will be used to infer the shape of the output, if provided.


    Keyword args
    ------------
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    dtype : :class:`nvidia.dali.types.DALIDataType`, optional
        Output data type.

        .. note::
          The generated numbers are converted to the output data type, rounding and clamping if necessary.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.
    range : float or list of float or Tensor/Batch of float, optional, default = `[-1.0, 1.0]`
        Range ``[min, max)`` of a continuous uniform distribution.

        This argument is mutually exclusive with `values`.

        .. warning::
          When specifying an integer type as `dtype`, the generated numbers can go outside
          the specified range, due to rounding.
    seed : int, optional, default = `-1`
        Random seed; if not set, one will be assigned automatically.
    shape : int or list of int or Tensor/Batch of int, optional
        Shape of the output data.
    values : float or list of float or Tensor/Batch of float, optional
        The discrete values [v0, v1, ..., vn] produced by a discrete uniform distribution.

        This argument is mutually exclusive with `range`.

    """

@overload
def uniform(
    shape_like: Optional[Batch] = None,
    /,
    *,
    device: Optional[Literal["cpu", "gpu"]] = None,
    rng: Optional[RNG] = None,
    dtype: Union[DALIDataType, DType, None] = None,
    range: Union[TensorLikeArg, Batch, Sequence[float], float, None] = [-1.0, 1.0],
    seed: Optional[int] = -1,
    shape: Union[TensorLikeArg, Batch, Sequence[int], int, None] = None,
    values: Union[TensorLikeArg, Batch, Sequence[float], float, None] = None,
) -> Batch:
    """
    Generates random numbers following a uniform distribution.

    It can be configured to produce a continuous uniform distribution in the `range` [min, max),
    or a discrete uniform distribution where any of the specified `values` [v0, v1, ..., vn] occur
    with equal probability.

    The shape of the generated data can be either specified explicitly with a `shape` argument,
    or chosen to match the shape of the `__shape_like` input, if provided. If none are present,
    a single value per sample is generated.


    Supported backends
     * 'cpu'
     * 'gpu'


    Args
    ----
    shape_like : Tensor/Batch, optional
        Shape of this input will be used to infer the shape of the output, if provided.


    Keyword args
    ------------
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    dtype : :class:`nvidia.dali.types.DALIDataType`, optional
        Output data type.

        .. note::
          The generated numbers are converted to the output data type, rounding and clamping if necessary.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.
    range : float or list of float or Tensor/Batch of float, optional, default = `[-1.0, 1.0]`
        Range ``[min, max)`` of a continuous uniform distribution.

        This argument is mutually exclusive with `values`.

        .. warning::
          When specifying an integer type as `dtype`, the generated numbers can go outside
          the specified range, due to rounding.
    seed : int, optional, default = `-1`
        Random seed; if not set, one will be assigned automatically.
    shape : int or list of int or Tensor/Batch of int, optional
        Shape of the output data.
    values : float or list of float or Tensor/Batch of float, optional
        The discrete values [v0, v1, ..., vn] produced by a discrete uniform distribution.

        This argument is mutually exclusive with `range`.

    """

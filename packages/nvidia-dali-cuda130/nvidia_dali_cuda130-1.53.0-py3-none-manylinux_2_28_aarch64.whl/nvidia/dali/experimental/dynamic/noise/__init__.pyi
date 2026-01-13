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
def gaussian(
    input: TensorLike,
    /,
    *,
    device: Optional[Literal["cpu", "gpu"]] = None,
    mean: Union[TensorLikeArg, Batch, float, None] = 0.0,
    seed: Optional[int] = -1,
    stddev: Union[TensorLikeArg, Batch, float, None] = 1.0,
) -> Union[Tensor, Batch]:
    """
    Applies gaussian noise to the input.

    The shape and data type of the output will match the input.


    Supported backends
     * 'cpu'
     * 'gpu'


    Args
    ----
    input : Tensor/Batch
        Input to the operator.


    Keyword args
    ------------
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    mean : float or Tensor/Batch of float, optional, default = `0.0`
        Mean of the distribution.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.
    seed : int, optional, default = `-1`
        Random seed; if not set, one will be assigned automatically.
    stddev : float or Tensor/Batch of float, optional, default = `1.0`
        Standard deviation of the distribution.

    """

@overload
def gaussian(
    input: TensorLike,
    /,
    *,
    device: Optional[Literal["cpu", "gpu"]] = None,
    batch_size: int,
    mean: Union[TensorLikeArg, Batch, float, None] = 0.0,
    seed: Optional[int] = -1,
    stddev: Union[TensorLikeArg, Batch, float, None] = 1.0,
) -> Batch:
    """
    Applies gaussian noise to the input.

    The shape and data type of the output will match the input.


    Supported backends
     * 'cpu'
     * 'gpu'


    Args
    ----
    input : Tensor/Batch
        Input to the operator.


    Keyword args
    ------------
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    mean : float or Tensor/Batch of float, optional, default = `0.0`
        Mean of the distribution.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.
    seed : int, optional, default = `-1`
        Random seed; if not set, one will be assigned automatically.
    stddev : float or Tensor/Batch of float, optional, default = `1.0`
        Standard deviation of the distribution.

    """

@overload
def gaussian(
    input: Batch,
    /,
    *,
    device: Optional[Literal["cpu", "gpu"]] = None,
    mean: Union[TensorLikeArg, Batch, float, None] = 0.0,
    seed: Optional[int] = -1,
    stddev: Union[TensorLikeArg, Batch, float, None] = 1.0,
) -> Batch:
    """
    Applies gaussian noise to the input.

    The shape and data type of the output will match the input.


    Supported backends
     * 'cpu'
     * 'gpu'


    Args
    ----
    input : Tensor/Batch
        Input to the operator.


    Keyword args
    ------------
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    mean : float or Tensor/Batch of float, optional, default = `0.0`
        Mean of the distribution.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.
    seed : int, optional, default = `-1`
        Random seed; if not set, one will be assigned automatically.
    stddev : float or Tensor/Batch of float, optional, default = `1.0`
        Standard deviation of the distribution.

    """

@overload
def salt_and_pepper(
    input: TensorLike,
    /,
    *,
    device: Optional[Literal["cpu", "gpu"]] = None,
    pepper_val: Union[TensorLikeArg, Batch, float, None] = None,
    per_channel: Optional[builtins.bool] = False,
    prob: Union[TensorLikeArg, Batch, float, None] = 0.05,
    salt_val: Union[TensorLikeArg, Batch, float, None] = None,
    salt_vs_pepper: Union[TensorLikeArg, Batch, float, None] = 0.5,
    seed: Optional[int] = -1,
) -> Union[Tensor, Batch]:
    """
    Applies salt-and-pepper noise to the input.

    The shape and data type of the output will match the input.


    Supported backends
     * 'cpu'
     * 'gpu'


    Args
    ----
    input : Tensor/Batch
        Input to the operator.


    Keyword args
    ------------
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    pepper_val : float or Tensor/Batch of float, optional
        Value of "pepper".

        If not provided, the pepper value will be -1.0 for floating point types or the
        minimum value of the input data type otherwise, converted to the data type of the input.
    per_channel : bool, optional, default = `False`
        Determines whether the noise should be generated for each channel independently.

        If set to True, the noise is generated for each channel independently,
        resulting in some channels being corrupted and others kept intact. If set to False, the noise
        is generated once and applied to all channels, so that all channels in a pixel should either be
        kept intact, take the "pepper" value, or the "salt" value.

        Note: Per-channel noise generation requires the input layout to contain a channels ('C') dimension,
        or be empty. In the case of the layout being empty, channel-last layout is assumed.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.
    prob : float or Tensor/Batch of float, optional, default = `0.05`
        Probability of an output value to take a salt or pepper value.
    salt_val : float or Tensor/Batch of float, optional
        Value of "salt".

        If not provided, the salt value will be 1.0 for floating point types or the
        maximum value of the input data type otherwise, converted to the data type of the input.
    salt_vs_pepper : float or Tensor/Batch of float, optional, default = `0.5`
        Probability of a corrupted output value to take a salt value.
    seed : int, optional, default = `-1`
        Random seed; if not set, one will be assigned automatically.

    """

@overload
def salt_and_pepper(
    input: TensorLike,
    /,
    *,
    device: Optional[Literal["cpu", "gpu"]] = None,
    batch_size: int,
    pepper_val: Union[TensorLikeArg, Batch, float, None] = None,
    per_channel: Optional[builtins.bool] = False,
    prob: Union[TensorLikeArg, Batch, float, None] = 0.05,
    salt_val: Union[TensorLikeArg, Batch, float, None] = None,
    salt_vs_pepper: Union[TensorLikeArg, Batch, float, None] = 0.5,
    seed: Optional[int] = -1,
) -> Batch:
    """
    Applies salt-and-pepper noise to the input.

    The shape and data type of the output will match the input.


    Supported backends
     * 'cpu'
     * 'gpu'


    Args
    ----
    input : Tensor/Batch
        Input to the operator.


    Keyword args
    ------------
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    pepper_val : float or Tensor/Batch of float, optional
        Value of "pepper".

        If not provided, the pepper value will be -1.0 for floating point types or the
        minimum value of the input data type otherwise, converted to the data type of the input.
    per_channel : bool, optional, default = `False`
        Determines whether the noise should be generated for each channel independently.

        If set to True, the noise is generated for each channel independently,
        resulting in some channels being corrupted and others kept intact. If set to False, the noise
        is generated once and applied to all channels, so that all channels in a pixel should either be
        kept intact, take the "pepper" value, or the "salt" value.

        Note: Per-channel noise generation requires the input layout to contain a channels ('C') dimension,
        or be empty. In the case of the layout being empty, channel-last layout is assumed.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.
    prob : float or Tensor/Batch of float, optional, default = `0.05`
        Probability of an output value to take a salt or pepper value.
    salt_val : float or Tensor/Batch of float, optional
        Value of "salt".

        If not provided, the salt value will be 1.0 for floating point types or the
        maximum value of the input data type otherwise, converted to the data type of the input.
    salt_vs_pepper : float or Tensor/Batch of float, optional, default = `0.5`
        Probability of a corrupted output value to take a salt value.
    seed : int, optional, default = `-1`
        Random seed; if not set, one will be assigned automatically.

    """

@overload
def salt_and_pepper(
    input: Batch,
    /,
    *,
    device: Optional[Literal["cpu", "gpu"]] = None,
    pepper_val: Union[TensorLikeArg, Batch, float, None] = None,
    per_channel: Optional[builtins.bool] = False,
    prob: Union[TensorLikeArg, Batch, float, None] = 0.05,
    salt_val: Union[TensorLikeArg, Batch, float, None] = None,
    salt_vs_pepper: Union[TensorLikeArg, Batch, float, None] = 0.5,
    seed: Optional[int] = -1,
) -> Batch:
    """
    Applies salt-and-pepper noise to the input.

    The shape and data type of the output will match the input.


    Supported backends
     * 'cpu'
     * 'gpu'


    Args
    ----
    input : Tensor/Batch
        Input to the operator.


    Keyword args
    ------------
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    pepper_val : float or Tensor/Batch of float, optional
        Value of "pepper".

        If not provided, the pepper value will be -1.0 for floating point types or the
        minimum value of the input data type otherwise, converted to the data type of the input.
    per_channel : bool, optional, default = `False`
        Determines whether the noise should be generated for each channel independently.

        If set to True, the noise is generated for each channel independently,
        resulting in some channels being corrupted and others kept intact. If set to False, the noise
        is generated once and applied to all channels, so that all channels in a pixel should either be
        kept intact, take the "pepper" value, or the "salt" value.

        Note: Per-channel noise generation requires the input layout to contain a channels ('C') dimension,
        or be empty. In the case of the layout being empty, channel-last layout is assumed.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.
    prob : float or Tensor/Batch of float, optional, default = `0.05`
        Probability of an output value to take a salt or pepper value.
    salt_val : float or Tensor/Batch of float, optional
        Value of "salt".

        If not provided, the salt value will be 1.0 for floating point types or the
        maximum value of the input data type otherwise, converted to the data type of the input.
    salt_vs_pepper : float or Tensor/Batch of float, optional, default = `0.5`
        Probability of a corrupted output value to take a salt value.
    seed : int, optional, default = `-1`
        Random seed; if not set, one will be assigned automatically.

    """

@overload
def shot(
    input: TensorLike,
    /,
    *,
    device: Optional[Literal["cpu", "gpu"]] = None,
    factor: Union[TensorLikeArg, Batch, float, None] = 20.0,
    seed: Optional[int] = -1,
) -> Union[Tensor, Batch]:
    """
    Applies shot noise to the input.

    The shot noise is generated by applying the following formula::

        output[:] = poisson_dist(max(0, input[:] / factor)) * factor) if factor != 0
        output[:] = input[:]                                          if factor == 0

    where ``poisson_dist`` represents a poisson distribution.

    Shot noise is a noise that's present in data generated by a Poisson process, like
    registering photons by an image sensor. This operator simulates the data
    acquisition process where each event increases the output value by
    `factor` and the input tensor contains the expected values of corresponding
    output points. For example, a `factor` of 0.1 means that 10 events are
    needed to increase the output value by 1, while a factor of 10 means that
    a single event increases the output by 10. The output values are quantized
    to multiples of `factor`. The larger the factor, the more noise is present in
    the output. A factor of 0 makes this an identity operation.

    The shape and data type of the output will match the input.


    Supported backends
     * 'cpu'
     * 'gpu'


    Args
    ----
    input : Tensor/Batch
        Input to the operator.


    Keyword args
    ------------
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    factor : float or Tensor/Batch of float, optional, default = `20.0`
        Factor parameter.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.
    seed : int, optional, default = `-1`
        Random seed; if not set, one will be assigned automatically.

    """

@overload
def shot(
    input: TensorLike,
    /,
    *,
    device: Optional[Literal["cpu", "gpu"]] = None,
    batch_size: int,
    factor: Union[TensorLikeArg, Batch, float, None] = 20.0,
    seed: Optional[int] = -1,
) -> Batch:
    """
    Applies shot noise to the input.

    The shot noise is generated by applying the following formula::

        output[:] = poisson_dist(max(0, input[:] / factor)) * factor) if factor != 0
        output[:] = input[:]                                          if factor == 0

    where ``poisson_dist`` represents a poisson distribution.

    Shot noise is a noise that's present in data generated by a Poisson process, like
    registering photons by an image sensor. This operator simulates the data
    acquisition process where each event increases the output value by
    `factor` and the input tensor contains the expected values of corresponding
    output points. For example, a `factor` of 0.1 means that 10 events are
    needed to increase the output value by 1, while a factor of 10 means that
    a single event increases the output by 10. The output values are quantized
    to multiples of `factor`. The larger the factor, the more noise is present in
    the output. A factor of 0 makes this an identity operation.

    The shape and data type of the output will match the input.


    Supported backends
     * 'cpu'
     * 'gpu'


    Args
    ----
    input : Tensor/Batch
        Input to the operator.


    Keyword args
    ------------
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    factor : float or Tensor/Batch of float, optional, default = `20.0`
        Factor parameter.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.
    seed : int, optional, default = `-1`
        Random seed; if not set, one will be assigned automatically.

    """

@overload
def shot(
    input: Batch,
    /,
    *,
    device: Optional[Literal["cpu", "gpu"]] = None,
    factor: Union[TensorLikeArg, Batch, float, None] = 20.0,
    seed: Optional[int] = -1,
) -> Batch:
    """
    Applies shot noise to the input.

    The shot noise is generated by applying the following formula::

        output[:] = poisson_dist(max(0, input[:] / factor)) * factor) if factor != 0
        output[:] = input[:]                                          if factor == 0

    where ``poisson_dist`` represents a poisson distribution.

    Shot noise is a noise that's present in data generated by a Poisson process, like
    registering photons by an image sensor. This operator simulates the data
    acquisition process where each event increases the output value by
    `factor` and the input tensor contains the expected values of corresponding
    output points. For example, a `factor` of 0.1 means that 10 events are
    needed to increase the output value by 1, while a factor of 10 means that
    a single event increases the output by 10. The output values are quantized
    to multiples of `factor`. The larger the factor, the more noise is present in
    the output. A factor of 0 makes this an identity operation.

    The shape and data type of the output will match the input.


    Supported backends
     * 'cpu'
     * 'gpu'


    Args
    ----
    input : Tensor/Batch
        Input to the operator.


    Keyword args
    ------------
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    factor : float or Tensor/Batch of float, optional, default = `20.0`
        Factor parameter.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.
    seed : int, optional, default = `-1`
        Random seed; if not set, one will be assigned automatically.

    """

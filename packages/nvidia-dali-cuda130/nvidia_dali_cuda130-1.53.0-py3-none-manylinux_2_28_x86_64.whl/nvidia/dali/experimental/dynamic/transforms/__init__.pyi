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
def combine(
    input_0: Batch,
    input_1: Batch,
    /,
    *inputs: Optional[Batch],
    device: Optional[Literal["cpu"]] = None,
    reverse_order: Optional[builtins.bool] = False,
) -> Batch:
    """
    Combines two or more affine transforms.

    By default, the transforms are combined such that applying the resulting transform to a point is equivalent to
     applying the input transforms in the order as listed.

    Example: combining [T1, T2, T3] is equivalent to T3(T2(T1(...))) for default order and equivalent to T1(T2(T3(...)))
     for reversed order.


    This operator allows sequence inputs.

    Supported backends
     * 'cpu'


    Args
    ----
    input_0 : Tensor/Batch
        Input to the operator.
    input_1 : Tensor/Batch
        Input to the operator.
    inputs[2..98] : Tensor/Batch, optional
        This function accepts up to 97 optional positional inputs


    Keyword args
    ------------
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.
    reverse_order : bool, optional, default = `False`
        Determines the order when combining affine transforms.

        If set to False (default), the operator's affine transform will be applied to the input transform.
        If set to True, the input transform will be applied to the operator's transform.

        If there's no input, this argument is ignored.

    """

@overload
def combine(
    input_0: Union[TensorLike, Batch],
    input_1: Union[TensorLike, Batch],
    /,
    *inputs: Union[TensorLike, Batch, None],
    device: Optional[Literal["cpu"]] = None,
    reverse_order: Optional[builtins.bool] = False,
) -> Union[Tensor, Batch]:
    """
    Combines two or more affine transforms.

    By default, the transforms are combined such that applying the resulting transform to a point is equivalent to
     applying the input transforms in the order as listed.

    Example: combining [T1, T2, T3] is equivalent to T3(T2(T1(...))) for default order and equivalent to T1(T2(T3(...)))
     for reversed order.


    This operator allows sequence inputs.

    Supported backends
     * 'cpu'


    Args
    ----
    input_0 : Tensor/Batch
        Input to the operator.
    input_1 : Tensor/Batch
        Input to the operator.
    inputs[2..98] : Tensor/Batch, optional
        This function accepts up to 97 optional positional inputs


    Keyword args
    ------------
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.
    reverse_order : bool, optional, default = `False`
        Determines the order when combining affine transforms.

        If set to False (default), the operator's affine transform will be applied to the input transform.
        If set to True, the input transform will be applied to the operator's transform.

        If there's no input, this argument is ignored.

    """

@overload
def combine(
    input_0: Union[TensorLike, Batch],
    input_1: Union[TensorLike, Batch],
    /,
    *inputs: Union[TensorLike, Batch, None],
    device: Optional[Literal["cpu"]] = None,
    batch_size: int,
    reverse_order: Optional[builtins.bool] = False,
) -> Batch:
    """
    Combines two or more affine transforms.

    By default, the transforms are combined such that applying the resulting transform to a point is equivalent to
     applying the input transforms in the order as listed.

    Example: combining [T1, T2, T3] is equivalent to T3(T2(T1(...))) for default order and equivalent to T1(T2(T3(...)))
     for reversed order.


    This operator allows sequence inputs.

    Supported backends
     * 'cpu'


    Args
    ----
    input_0 : Tensor/Batch
        Input to the operator.
    input_1 : Tensor/Batch
        Input to the operator.
    inputs[2..98] : Tensor/Batch, optional
        This function accepts up to 97 optional positional inputs


    Keyword args
    ------------
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.
    reverse_order : bool, optional, default = `False`
        Determines the order when combining affine transforms.

        If set to False (default), the operator's affine transform will be applied to the input transform.
        If set to True, the input transform will be applied to the operator's transform.

        If there's no input, this argument is ignored.

    """

@overload
def crop(
    input: Optional[TensorLike] = None,
    /,
    *,
    device: Optional[Literal["cpu"]] = None,
    absolute: Optional[builtins.bool] = False,
    from_end: Union[TensorLikeArg, Batch, Sequence[float], float, None] = [1.0],
    from_start: Union[TensorLikeArg, Batch, Sequence[float], float, None] = [0.0],
    reverse_order: Optional[builtins.bool] = False,
    to_end: Union[TensorLikeArg, Batch, Sequence[float], float, None] = [1.0],
    to_start: Union[TensorLikeArg, Batch, Sequence[float], float, None] = [0.0],
) -> Union[Tensor, Batch]:
    """
    Produces an affine transform matrix that maps a reference coordinate space to another one.

    This transform can be used to adjust coordinates after a crop operation so that a `from_start` point will
    be mapped to `to_start` and `from_end` will be mapped to `to_end`.

    If another transform matrix is passed as an input, the operator applies the transformation to the matrix provided.

    .. note::
        The output of this operator can be fed directly to ``CoordTransform`` and ``WarpAffine`` operators.


    This operator allows sequence inputs.

    Supported backends
     * 'cpu'


    Args
    ----
    input : Tensor/Batch, optional
        Input to the operator.


    Keyword args
    ------------
    absolute : bool, optional, default = `False`
        If set to true, start and end coordinates will be swapped if start > end.
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    from_end : float or list of float or Tensor/Batch of float, optional, default = `[1.0]`
        The upper bound of the original coordinate space.

        .. note::
            If left empty, a vector of ones will be assumed.
            If a single value is provided, it will be repeated to match the number of dimensions

        Supports :func:`per-frame<nvidia.dali.fn.per_frame>` inputs.
    from_start : float or list of float or Tensor/Batch of float, optional, default = `[0.0]`
        The lower bound of the original coordinate space.

        .. note::
            If left empty, a vector of zeros will be assumed.
            If a single value is provided, it will be repeated to match the number of dimensions

        Supports :func:`per-frame<nvidia.dali.fn.per_frame>` inputs.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.
    reverse_order : bool, optional, default = `False`
        Determines the order when combining affine transforms.

        If set to False (default), the operator's affine transform will be applied to the input transform.
        If set to True, the input transform will be applied to the operator's transform.

        If there's no input, this argument is ignored.
    to_end : float or list of float or Tensor/Batch of float, optional, default = `[1.0]`
        The upper bound of the destination coordinate space.

        .. note::
            If left empty, a vector of ones will be assumed.
            If a single value is provided, it will be repeated to match the number of dimensions

        Supports :func:`per-frame<nvidia.dali.fn.per_frame>` inputs.
    to_start : float or list of float or Tensor/Batch of float, optional, default = `[0.0]`
        The lower bound of the destination coordinate space.

        .. note::
            If left empty, a vector of zeros will be assumed.
            If a single value is provided, it will be repeated to match the number of dimensions

        Supports :func:`per-frame<nvidia.dali.fn.per_frame>` inputs.

    """

@overload
def crop(
    input: Optional[TensorLike] = None,
    /,
    *,
    device: Optional[Literal["cpu"]] = None,
    batch_size: int,
    absolute: Optional[builtins.bool] = False,
    from_end: Union[TensorLikeArg, Batch, Sequence[float], float, None] = [1.0],
    from_start: Union[TensorLikeArg, Batch, Sequence[float], float, None] = [0.0],
    reverse_order: Optional[builtins.bool] = False,
    to_end: Union[TensorLikeArg, Batch, Sequence[float], float, None] = [1.0],
    to_start: Union[TensorLikeArg, Batch, Sequence[float], float, None] = [0.0],
) -> Batch:
    """
    Produces an affine transform matrix that maps a reference coordinate space to another one.

    This transform can be used to adjust coordinates after a crop operation so that a `from_start` point will
    be mapped to `to_start` and `from_end` will be mapped to `to_end`.

    If another transform matrix is passed as an input, the operator applies the transformation to the matrix provided.

    .. note::
        The output of this operator can be fed directly to ``CoordTransform`` and ``WarpAffine`` operators.


    This operator allows sequence inputs.

    Supported backends
     * 'cpu'


    Args
    ----
    input : Tensor/Batch, optional
        Input to the operator.


    Keyword args
    ------------
    absolute : bool, optional, default = `False`
        If set to true, start and end coordinates will be swapped if start > end.
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    from_end : float or list of float or Tensor/Batch of float, optional, default = `[1.0]`
        The upper bound of the original coordinate space.

        .. note::
            If left empty, a vector of ones will be assumed.
            If a single value is provided, it will be repeated to match the number of dimensions

        Supports :func:`per-frame<nvidia.dali.fn.per_frame>` inputs.
    from_start : float or list of float or Tensor/Batch of float, optional, default = `[0.0]`
        The lower bound of the original coordinate space.

        .. note::
            If left empty, a vector of zeros will be assumed.
            If a single value is provided, it will be repeated to match the number of dimensions

        Supports :func:`per-frame<nvidia.dali.fn.per_frame>` inputs.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.
    reverse_order : bool, optional, default = `False`
        Determines the order when combining affine transforms.

        If set to False (default), the operator's affine transform will be applied to the input transform.
        If set to True, the input transform will be applied to the operator's transform.

        If there's no input, this argument is ignored.
    to_end : float or list of float or Tensor/Batch of float, optional, default = `[1.0]`
        The upper bound of the destination coordinate space.

        .. note::
            If left empty, a vector of ones will be assumed.
            If a single value is provided, it will be repeated to match the number of dimensions

        Supports :func:`per-frame<nvidia.dali.fn.per_frame>` inputs.
    to_start : float or list of float or Tensor/Batch of float, optional, default = `[0.0]`
        The lower bound of the destination coordinate space.

        .. note::
            If left empty, a vector of zeros will be assumed.
            If a single value is provided, it will be repeated to match the number of dimensions

        Supports :func:`per-frame<nvidia.dali.fn.per_frame>` inputs.

    """

@overload
def crop(
    input: Optional[Batch] = None,
    /,
    *,
    device: Optional[Literal["cpu"]] = None,
    absolute: Optional[builtins.bool] = False,
    from_end: Union[TensorLikeArg, Batch, Sequence[float], float, None] = [1.0],
    from_start: Union[TensorLikeArg, Batch, Sequence[float], float, None] = [0.0],
    reverse_order: Optional[builtins.bool] = False,
    to_end: Union[TensorLikeArg, Batch, Sequence[float], float, None] = [1.0],
    to_start: Union[TensorLikeArg, Batch, Sequence[float], float, None] = [0.0],
) -> Batch:
    """
    Produces an affine transform matrix that maps a reference coordinate space to another one.

    This transform can be used to adjust coordinates after a crop operation so that a `from_start` point will
    be mapped to `to_start` and `from_end` will be mapped to `to_end`.

    If another transform matrix is passed as an input, the operator applies the transformation to the matrix provided.

    .. note::
        The output of this operator can be fed directly to ``CoordTransform`` and ``WarpAffine`` operators.


    This operator allows sequence inputs.

    Supported backends
     * 'cpu'


    Args
    ----
    input : Tensor/Batch, optional
        Input to the operator.


    Keyword args
    ------------
    absolute : bool, optional, default = `False`
        If set to true, start and end coordinates will be swapped if start > end.
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    from_end : float or list of float or Tensor/Batch of float, optional, default = `[1.0]`
        The upper bound of the original coordinate space.

        .. note::
            If left empty, a vector of ones will be assumed.
            If a single value is provided, it will be repeated to match the number of dimensions

        Supports :func:`per-frame<nvidia.dali.fn.per_frame>` inputs.
    from_start : float or list of float or Tensor/Batch of float, optional, default = `[0.0]`
        The lower bound of the original coordinate space.

        .. note::
            If left empty, a vector of zeros will be assumed.
            If a single value is provided, it will be repeated to match the number of dimensions

        Supports :func:`per-frame<nvidia.dali.fn.per_frame>` inputs.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.
    reverse_order : bool, optional, default = `False`
        Determines the order when combining affine transforms.

        If set to False (default), the operator's affine transform will be applied to the input transform.
        If set to True, the input transform will be applied to the operator's transform.

        If there's no input, this argument is ignored.
    to_end : float or list of float or Tensor/Batch of float, optional, default = `[1.0]`
        The upper bound of the destination coordinate space.

        .. note::
            If left empty, a vector of ones will be assumed.
            If a single value is provided, it will be repeated to match the number of dimensions

        Supports :func:`per-frame<nvidia.dali.fn.per_frame>` inputs.
    to_start : float or list of float or Tensor/Batch of float, optional, default = `[0.0]`
        The lower bound of the destination coordinate space.

        .. note::
            If left empty, a vector of zeros will be assumed.
            If a single value is provided, it will be repeated to match the number of dimensions

        Supports :func:`per-frame<nvidia.dali.fn.per_frame>` inputs.

    """

@overload
def rotation(
    input: Optional[TensorLike] = None,
    /,
    *,
    device: Optional[Literal["cpu"]] = None,
    angle: Union[TensorLikeArg, Batch, float],
    axis: Union[TensorLikeArg, Batch, Sequence[float], float, None] = None,
    center: Union[TensorLikeArg, Batch, Sequence[float], float, None] = None,
    reverse_order: Optional[builtins.bool] = False,
) -> Union[Tensor, Batch]:
    """
    Produces a rotation affine transform matrix.

    If another transform matrix is passed as an input, the operator applies rotation to the matrix provided.

    The number of dimensions is assumed to be 3 if a rotation axis is provided or 2 otherwise.

    .. note::
        The output of this operator can be fed directly to ``CoordTransform`` and ``WarpAffine`` operators.


    This operator allows sequence inputs.

    Supported backends
     * 'cpu'


    Args
    ----
    input : Tensor/Batch, optional
        Input to the operator.


    Keyword args
    ------------
    angle : float or Tensor/Batch of float
        Angle, in degrees.

        Supports :func:`per-frame<nvidia.dali.fn.per_frame>` inputs.
    axis : float or list of float or Tensor/Batch of float, optional
        Axis of rotation (applies **only** to 3D transforms).

        The vector does not need to be normalized, but it must have a non-zero length.

        Reversing the vector is equivalent to changing the sign of `angle`.

        Supports :func:`per-frame<nvidia.dali.fn.per_frame>` inputs.
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    center : float or list of float or Tensor/Batch of float, optional
        The center of the rotation.

        If provided, the number of elements should match the dimensionality of the transform.

        Supports :func:`per-frame<nvidia.dali.fn.per_frame>` inputs.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.
    reverse_order : bool, optional, default = `False`
        Determines the order when combining affine transforms.

        If set to False (default), the operator's affine transform will be applied to the input transform.
        If set to True, the input transform will be applied to the operator's transform.

        If there's no input, this argument is ignored.

    """

@overload
def rotation(
    input: Optional[TensorLike] = None,
    /,
    *,
    device: Optional[Literal["cpu"]] = None,
    batch_size: int,
    angle: Union[TensorLikeArg, Batch, float],
    axis: Union[TensorLikeArg, Batch, Sequence[float], float, None] = None,
    center: Union[TensorLikeArg, Batch, Sequence[float], float, None] = None,
    reverse_order: Optional[builtins.bool] = False,
) -> Batch:
    """
    Produces a rotation affine transform matrix.

    If another transform matrix is passed as an input, the operator applies rotation to the matrix provided.

    The number of dimensions is assumed to be 3 if a rotation axis is provided or 2 otherwise.

    .. note::
        The output of this operator can be fed directly to ``CoordTransform`` and ``WarpAffine`` operators.


    This operator allows sequence inputs.

    Supported backends
     * 'cpu'


    Args
    ----
    input : Tensor/Batch, optional
        Input to the operator.


    Keyword args
    ------------
    angle : float or Tensor/Batch of float
        Angle, in degrees.

        Supports :func:`per-frame<nvidia.dali.fn.per_frame>` inputs.
    axis : float or list of float or Tensor/Batch of float, optional
        Axis of rotation (applies **only** to 3D transforms).

        The vector does not need to be normalized, but it must have a non-zero length.

        Reversing the vector is equivalent to changing the sign of `angle`.

        Supports :func:`per-frame<nvidia.dali.fn.per_frame>` inputs.
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    center : float or list of float or Tensor/Batch of float, optional
        The center of the rotation.

        If provided, the number of elements should match the dimensionality of the transform.

        Supports :func:`per-frame<nvidia.dali.fn.per_frame>` inputs.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.
    reverse_order : bool, optional, default = `False`
        Determines the order when combining affine transforms.

        If set to False (default), the operator's affine transform will be applied to the input transform.
        If set to True, the input transform will be applied to the operator's transform.

        If there's no input, this argument is ignored.

    """

@overload
def rotation(
    input: Optional[Batch] = None,
    /,
    *,
    device: Optional[Literal["cpu"]] = None,
    angle: Union[TensorLikeArg, Batch, float],
    axis: Union[TensorLikeArg, Batch, Sequence[float], float, None] = None,
    center: Union[TensorLikeArg, Batch, Sequence[float], float, None] = None,
    reverse_order: Optional[builtins.bool] = False,
) -> Batch:
    """
    Produces a rotation affine transform matrix.

    If another transform matrix is passed as an input, the operator applies rotation to the matrix provided.

    The number of dimensions is assumed to be 3 if a rotation axis is provided or 2 otherwise.

    .. note::
        The output of this operator can be fed directly to ``CoordTransform`` and ``WarpAffine`` operators.


    This operator allows sequence inputs.

    Supported backends
     * 'cpu'


    Args
    ----
    input : Tensor/Batch, optional
        Input to the operator.


    Keyword args
    ------------
    angle : float or Tensor/Batch of float
        Angle, in degrees.

        Supports :func:`per-frame<nvidia.dali.fn.per_frame>` inputs.
    axis : float or list of float or Tensor/Batch of float, optional
        Axis of rotation (applies **only** to 3D transforms).

        The vector does not need to be normalized, but it must have a non-zero length.

        Reversing the vector is equivalent to changing the sign of `angle`.

        Supports :func:`per-frame<nvidia.dali.fn.per_frame>` inputs.
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    center : float or list of float or Tensor/Batch of float, optional
        The center of the rotation.

        If provided, the number of elements should match the dimensionality of the transform.

        Supports :func:`per-frame<nvidia.dali.fn.per_frame>` inputs.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.
    reverse_order : bool, optional, default = `False`
        Determines the order when combining affine transforms.

        If set to False (default), the operator's affine transform will be applied to the input transform.
        If set to True, the input transform will be applied to the operator's transform.

        If there's no input, this argument is ignored.

    """

@overload
def scale(
    input: Optional[TensorLike] = None,
    /,
    *,
    device: Optional[Literal["cpu"]] = None,
    center: Union[TensorLikeArg, Batch, Sequence[float], float, None] = None,
    ndim: Optional[int] = None,
    reverse_order: Optional[builtins.bool] = False,
    scale: Union[TensorLikeArg, Batch, Sequence[float], float],
) -> Union[Tensor, Batch]:
    """
    Produces a scale affine transform matrix.

    If another transform matrix is passed as an input, the operator applies scaling to the matrix provided.

    .. note::
        The output of this operator can be fed directly to ``CoordTransform`` and ``WarpAffine`` operators.


    This operator allows sequence inputs.

    Supported backends
     * 'cpu'


    Args
    ----
    input : Tensor/Batch, optional
        Input to the operator.


    Keyword args
    ------------
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    center : float or list of float or Tensor/Batch of float, optional
        The center of the scale operation.

        If provided, the number of elements should match the one of `scale` argument.

        Supports :func:`per-frame<nvidia.dali.fn.per_frame>` inputs.
    ndim : int, optional
        Number of dimensions.

        It should be provided when the number of dimensions can't be inferred. For example,
        when `scale` is a scalar value and there's no input transform.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.
    reverse_order : bool, optional, default = `False`
        Determines the order when combining affine transforms.

        If set to False (default), the operator's affine transform will be applied to the input transform.
        If set to True, the input transform will be applied to the operator's transform.

        If there's no input, this argument is ignored.
    scale : float or list of float or Tensor/Batch of float
        The scale factor, per dimension.

        The number of dimensions of the transform is inferred from this argument.

        Supports :func:`per-frame<nvidia.dali.fn.per_frame>` inputs.

    """

@overload
def scale(
    input: Optional[TensorLike] = None,
    /,
    *,
    device: Optional[Literal["cpu"]] = None,
    batch_size: int,
    center: Union[TensorLikeArg, Batch, Sequence[float], float, None] = None,
    ndim: Optional[int] = None,
    reverse_order: Optional[builtins.bool] = False,
    scale: Union[TensorLikeArg, Batch, Sequence[float], float],
) -> Batch:
    """
    Produces a scale affine transform matrix.

    If another transform matrix is passed as an input, the operator applies scaling to the matrix provided.

    .. note::
        The output of this operator can be fed directly to ``CoordTransform`` and ``WarpAffine`` operators.


    This operator allows sequence inputs.

    Supported backends
     * 'cpu'


    Args
    ----
    input : Tensor/Batch, optional
        Input to the operator.


    Keyword args
    ------------
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    center : float or list of float or Tensor/Batch of float, optional
        The center of the scale operation.

        If provided, the number of elements should match the one of `scale` argument.

        Supports :func:`per-frame<nvidia.dali.fn.per_frame>` inputs.
    ndim : int, optional
        Number of dimensions.

        It should be provided when the number of dimensions can't be inferred. For example,
        when `scale` is a scalar value and there's no input transform.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.
    reverse_order : bool, optional, default = `False`
        Determines the order when combining affine transforms.

        If set to False (default), the operator's affine transform will be applied to the input transform.
        If set to True, the input transform will be applied to the operator's transform.

        If there's no input, this argument is ignored.
    scale : float or list of float or Tensor/Batch of float
        The scale factor, per dimension.

        The number of dimensions of the transform is inferred from this argument.

        Supports :func:`per-frame<nvidia.dali.fn.per_frame>` inputs.

    """

@overload
def scale(
    input: Optional[Batch] = None,
    /,
    *,
    device: Optional[Literal["cpu"]] = None,
    center: Union[TensorLikeArg, Batch, Sequence[float], float, None] = None,
    ndim: Optional[int] = None,
    reverse_order: Optional[builtins.bool] = False,
    scale: Union[TensorLikeArg, Batch, Sequence[float], float],
) -> Batch:
    """
    Produces a scale affine transform matrix.

    If another transform matrix is passed as an input, the operator applies scaling to the matrix provided.

    .. note::
        The output of this operator can be fed directly to ``CoordTransform`` and ``WarpAffine`` operators.


    This operator allows sequence inputs.

    Supported backends
     * 'cpu'


    Args
    ----
    input : Tensor/Batch, optional
        Input to the operator.


    Keyword args
    ------------
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    center : float or list of float or Tensor/Batch of float, optional
        The center of the scale operation.

        If provided, the number of elements should match the one of `scale` argument.

        Supports :func:`per-frame<nvidia.dali.fn.per_frame>` inputs.
    ndim : int, optional
        Number of dimensions.

        It should be provided when the number of dimensions can't be inferred. For example,
        when `scale` is a scalar value and there's no input transform.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.
    reverse_order : bool, optional, default = `False`
        Determines the order when combining affine transforms.

        If set to False (default), the operator's affine transform will be applied to the input transform.
        If set to True, the input transform will be applied to the operator's transform.

        If there's no input, this argument is ignored.
    scale : float or list of float or Tensor/Batch of float
        The scale factor, per dimension.

        The number of dimensions of the transform is inferred from this argument.

        Supports :func:`per-frame<nvidia.dali.fn.per_frame>` inputs.

    """

@overload
def shear(
    input: Optional[TensorLike] = None,
    /,
    *,
    device: Optional[Literal["cpu"]] = None,
    angles: Union[TensorLikeArg, Batch, Sequence[float], float, None] = None,
    center: Union[TensorLikeArg, Batch, Sequence[float], float, None] = None,
    reverse_order: Optional[builtins.bool] = False,
    shear: Union[TensorLikeArg, Batch, Sequence[float], float, None] = None,
) -> Union[Tensor, Batch]:
    """
    Produces a shear affine transform matrix.

    If another transform matrix is passed as an input, the operator applies the shear mapping to the matrix provided.

    .. note::
        The output of this operator can be fed directly to ``CoordTransform`` and ``WarpAffine`` operators.


    This operator allows sequence inputs.

    Supported backends
     * 'cpu'


    Args
    ----
    input : Tensor/Batch, optional
        Input to the operator.


    Keyword args
    ------------
    angles : float or list of float or Tensor/Batch of float, optional
        The shear angles, in degrees.

        This argument is mutually exclusive with `shear`.

        For 2D, `angles` contains two elements: angle_x, angle_y.

        For 3D, `angles` contains six elements: angle_xy, angle_xz, angle_yx, angle_yz, angle_zx, angle_zy.

        A shear angle is translated to a shear factor as follows::

            shear_factor = tan(deg2rad(shear_angle))

        .. note::
            The valid range of values is between -90 and 90 degrees.
            This argument is mutually exclusive with `shear`.
            If provided, the number of dimensions of the transform is inferred from this argument.

        Supports :func:`per-frame<nvidia.dali.fn.per_frame>` inputs.
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    center : float or list of float or Tensor/Batch of float, optional
        The center of the shear operation.

        If provided, the number of elements should match the dimensionality of the transform.

        Supports :func:`per-frame<nvidia.dali.fn.per_frame>` inputs.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.
    reverse_order : bool, optional, default = `False`
        Determines the order when combining affine transforms.

        If set to False (default), the operator's affine transform will be applied to the input transform.
        If set to True, the input transform will be applied to the operator's transform.

        If there's no input, this argument is ignored.
    shear : float or list of float or Tensor/Batch of float, optional
        The shear factors.

        For 2D, `shear` contains two elements: shear_x, shear_y.

        For 3D, `shear` contains six elements: shear_xy, shear_xz, shear_yx, shear_yz, shear_zx, shear_zy.

        A shear factor value can be interpreted as the offset to be applied in the first axis when moving in the
        direction of the second axis.

        .. note::
            This argument is mutually exclusive with `angles`.
            If provided, the number of dimensions of the transform is inferred from this argument.

        Supports :func:`per-frame<nvidia.dali.fn.per_frame>` inputs.

    """

@overload
def shear(
    input: Optional[TensorLike] = None,
    /,
    *,
    device: Optional[Literal["cpu"]] = None,
    batch_size: int,
    angles: Union[TensorLikeArg, Batch, Sequence[float], float, None] = None,
    center: Union[TensorLikeArg, Batch, Sequence[float], float, None] = None,
    reverse_order: Optional[builtins.bool] = False,
    shear: Union[TensorLikeArg, Batch, Sequence[float], float, None] = None,
) -> Batch:
    """
    Produces a shear affine transform matrix.

    If another transform matrix is passed as an input, the operator applies the shear mapping to the matrix provided.

    .. note::
        The output of this operator can be fed directly to ``CoordTransform`` and ``WarpAffine`` operators.


    This operator allows sequence inputs.

    Supported backends
     * 'cpu'


    Args
    ----
    input : Tensor/Batch, optional
        Input to the operator.


    Keyword args
    ------------
    angles : float or list of float or Tensor/Batch of float, optional
        The shear angles, in degrees.

        This argument is mutually exclusive with `shear`.

        For 2D, `angles` contains two elements: angle_x, angle_y.

        For 3D, `angles` contains six elements: angle_xy, angle_xz, angle_yx, angle_yz, angle_zx, angle_zy.

        A shear angle is translated to a shear factor as follows::

            shear_factor = tan(deg2rad(shear_angle))

        .. note::
            The valid range of values is between -90 and 90 degrees.
            This argument is mutually exclusive with `shear`.
            If provided, the number of dimensions of the transform is inferred from this argument.

        Supports :func:`per-frame<nvidia.dali.fn.per_frame>` inputs.
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    center : float or list of float or Tensor/Batch of float, optional
        The center of the shear operation.

        If provided, the number of elements should match the dimensionality of the transform.

        Supports :func:`per-frame<nvidia.dali.fn.per_frame>` inputs.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.
    reverse_order : bool, optional, default = `False`
        Determines the order when combining affine transforms.

        If set to False (default), the operator's affine transform will be applied to the input transform.
        If set to True, the input transform will be applied to the operator's transform.

        If there's no input, this argument is ignored.
    shear : float or list of float or Tensor/Batch of float, optional
        The shear factors.

        For 2D, `shear` contains two elements: shear_x, shear_y.

        For 3D, `shear` contains six elements: shear_xy, shear_xz, shear_yx, shear_yz, shear_zx, shear_zy.

        A shear factor value can be interpreted as the offset to be applied in the first axis when moving in the
        direction of the second axis.

        .. note::
            This argument is mutually exclusive with `angles`.
            If provided, the number of dimensions of the transform is inferred from this argument.

        Supports :func:`per-frame<nvidia.dali.fn.per_frame>` inputs.

    """

@overload
def shear(
    input: Optional[Batch] = None,
    /,
    *,
    device: Optional[Literal["cpu"]] = None,
    angles: Union[TensorLikeArg, Batch, Sequence[float], float, None] = None,
    center: Union[TensorLikeArg, Batch, Sequence[float], float, None] = None,
    reverse_order: Optional[builtins.bool] = False,
    shear: Union[TensorLikeArg, Batch, Sequence[float], float, None] = None,
) -> Batch:
    """
    Produces a shear affine transform matrix.

    If another transform matrix is passed as an input, the operator applies the shear mapping to the matrix provided.

    .. note::
        The output of this operator can be fed directly to ``CoordTransform`` and ``WarpAffine`` operators.


    This operator allows sequence inputs.

    Supported backends
     * 'cpu'


    Args
    ----
    input : Tensor/Batch, optional
        Input to the operator.


    Keyword args
    ------------
    angles : float or list of float or Tensor/Batch of float, optional
        The shear angles, in degrees.

        This argument is mutually exclusive with `shear`.

        For 2D, `angles` contains two elements: angle_x, angle_y.

        For 3D, `angles` contains six elements: angle_xy, angle_xz, angle_yx, angle_yz, angle_zx, angle_zy.

        A shear angle is translated to a shear factor as follows::

            shear_factor = tan(deg2rad(shear_angle))

        .. note::
            The valid range of values is between -90 and 90 degrees.
            This argument is mutually exclusive with `shear`.
            If provided, the number of dimensions of the transform is inferred from this argument.

        Supports :func:`per-frame<nvidia.dali.fn.per_frame>` inputs.
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    center : float or list of float or Tensor/Batch of float, optional
        The center of the shear operation.

        If provided, the number of elements should match the dimensionality of the transform.

        Supports :func:`per-frame<nvidia.dali.fn.per_frame>` inputs.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.
    reverse_order : bool, optional, default = `False`
        Determines the order when combining affine transforms.

        If set to False (default), the operator's affine transform will be applied to the input transform.
        If set to True, the input transform will be applied to the operator's transform.

        If there's no input, this argument is ignored.
    shear : float or list of float or Tensor/Batch of float, optional
        The shear factors.

        For 2D, `shear` contains two elements: shear_x, shear_y.

        For 3D, `shear` contains six elements: shear_xy, shear_xz, shear_yx, shear_yz, shear_zx, shear_zy.

        A shear factor value can be interpreted as the offset to be applied in the first axis when moving in the
        direction of the second axis.

        .. note::
            This argument is mutually exclusive with `angles`.
            If provided, the number of dimensions of the transform is inferred from this argument.

        Supports :func:`per-frame<nvidia.dali.fn.per_frame>` inputs.

    """

@overload
def translation(
    input: Optional[TensorLike] = None,
    /,
    *,
    device: Optional[Literal["cpu"]] = None,
    offset: Union[TensorLikeArg, Batch, Sequence[float], float],
    reverse_order: Optional[builtins.bool] = False,
) -> Union[Tensor, Batch]:
    """
    Produces a translation affine transform matrix.

    If another transform matrix is passed as an input, the operator applies translation to the matrix provided.

    .. note::
        The output of this operator can be fed directly to ``CoordTransform`` and ``WarpAffine`` operators.


    This operator allows sequence inputs.

    Supported backends
     * 'cpu'


    Args
    ----
    input : Tensor/Batch, optional
        Input to the operator.


    Keyword args
    ------------
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    offset : float or list of float or Tensor/Batch of float
        The translation vector.

        The number of dimensions of the transform is inferred from this argument.

        Supports :func:`per-frame<nvidia.dali.fn.per_frame>` inputs.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.
    reverse_order : bool, optional, default = `False`
        Determines the order when combining affine transforms.

        If set to False (default), the operator's affine transform will be applied to the input transform.
        If set to True, the input transform will be applied to the operator's transform.

        If there's no input, this argument is ignored.

    """

@overload
def translation(
    input: Optional[TensorLike] = None,
    /,
    *,
    device: Optional[Literal["cpu"]] = None,
    batch_size: int,
    offset: Union[TensorLikeArg, Batch, Sequence[float], float],
    reverse_order: Optional[builtins.bool] = False,
) -> Batch:
    """
    Produces a translation affine transform matrix.

    If another transform matrix is passed as an input, the operator applies translation to the matrix provided.

    .. note::
        The output of this operator can be fed directly to ``CoordTransform`` and ``WarpAffine`` operators.


    This operator allows sequence inputs.

    Supported backends
     * 'cpu'


    Args
    ----
    input : Tensor/Batch, optional
        Input to the operator.


    Keyword args
    ------------
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    offset : float or list of float or Tensor/Batch of float
        The translation vector.

        The number of dimensions of the transform is inferred from this argument.

        Supports :func:`per-frame<nvidia.dali.fn.per_frame>` inputs.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.
    reverse_order : bool, optional, default = `False`
        Determines the order when combining affine transforms.

        If set to False (default), the operator's affine transform will be applied to the input transform.
        If set to True, the input transform will be applied to the operator's transform.

        If there's no input, this argument is ignored.

    """

@overload
def translation(
    input: Optional[Batch] = None,
    /,
    *,
    device: Optional[Literal["cpu"]] = None,
    offset: Union[TensorLikeArg, Batch, Sequence[float], float],
    reverse_order: Optional[builtins.bool] = False,
) -> Batch:
    """
    Produces a translation affine transform matrix.

    If another transform matrix is passed as an input, the operator applies translation to the matrix provided.

    .. note::
        The output of this operator can be fed directly to ``CoordTransform`` and ``WarpAffine`` operators.


    This operator allows sequence inputs.

    Supported backends
     * 'cpu'


    Args
    ----
    input : Tensor/Batch, optional
        Input to the operator.


    Keyword args
    ------------
    bytes_per_sample_hint : int or list of int, optional, default = `[0]`
        Output size hint, in bytes per sample.

        If specified, the operator's outputs residing in GPU or page-locked host memory will be preallocated
        to accommodate a batch of samples of this size.
    offset : float or list of float or Tensor/Batch of float
        The translation vector.

        The number of dimensions of the transform is inferred from this argument.

        Supports :func:`per-frame<nvidia.dali.fn.per_frame>` inputs.
    preserve : bool, optional, default = `False`
        Prevents the operator from being removed from the
        graph even if its outputs are not used.
    reverse_order : bool, optional, default = `False`
        Determines the order when combining affine transforms.

        If set to False (default), the operator's affine transform will be applied to the input transform.
        If set to True, the input transform will be applied to the operator's transform.

        If there's no input, this argument is ignored.

    """

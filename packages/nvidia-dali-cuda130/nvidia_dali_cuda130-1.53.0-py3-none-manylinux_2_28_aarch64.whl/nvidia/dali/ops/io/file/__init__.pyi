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

class Read:
    """
    Reads raw file contents from an encoded filename represented by a 1D byte array.

    .. note::
      To produce a compatible encoded filepath from Python (e.g. in an external_source node generator),
      use `np.frombuffer(filepath_str.encode("utf-8"), dtype=types.UINT8)`.


    Supported backends
     * 'cpu'


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

    def __init__(
        self,
        /,
        *,
        device: Optional[Literal["cpu"]] = None,
        name: Optional[str] = None,
        bytes_per_sample_hint: Union[Sequence[int], int, None] = [0],
        dont_use_mmap: Optional[bool] = False,
        preserve: Optional[bool] = False,
        use_o_direct: Optional[bool] = False,
    ) -> None: ...
    @overload
    def __call__(
        self,
        filepaths: Union[DataNode, TensorLikeIn],
        /,
        *,
        device: Optional[Literal["cpu"]] = None,
        name: Optional[str] = None,
        bytes_per_sample_hint: Union[Sequence[int], int, None] = [0],
        dont_use_mmap: Optional[bool] = False,
        preserve: Optional[bool] = False,
        use_o_direct: Optional[bool] = False,
    ) -> DataNode:
        """
        Operator call to be used in graph definition.

        Args
        ----
        filepaths : TensorList
            File paths to read from.


        """
        ...

    @overload
    def __call__(
        self,
        filepaths: List[DataNode],
        /,
        *,
        device: Optional[Literal["cpu"]] = None,
        name: Optional[str] = None,
        bytes_per_sample_hint: Union[Sequence[int], int, None] = [0],
        dont_use_mmap: Optional[bool] = False,
        preserve: Optional[bool] = False,
        use_o_direct: Optional[bool] = False,
    ) -> Union[DataNode, List[DataNode]]:
        """
        Operator call to be used in graph definition.

        Args
        ----
        filepaths : TensorList
            File paths to read from.


        """
        ...

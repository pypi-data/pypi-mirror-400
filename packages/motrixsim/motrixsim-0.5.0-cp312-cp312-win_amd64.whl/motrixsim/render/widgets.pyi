# Copyright (C) 2020-2025 Motphys Technology Co., Ltd. All Rights Reserved.
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
# ==============================================================================

import builtins
import typing
from motrixsim import Camera
from motrixsim.render import Image, Layout

class CameraViewport:
    camera: Camera
    r"""
    Camera: The camera displayed in this viewport.
    """
    def update(self, camera:typing.Optional[Camera]=None, layout:typing.Optional[Layout]=None, sim_world_index:typing.Optional[builtins.int]=None) -> None:
        r"""
        Update the camera viewport widget.
        
        Args:
            camera (Optional[Camera]): New camera object to display. If not provided,
                keeps the current camera.
            layout (Optional[Layout]): New layout configuration. If not provided,
                keeps the current layout.
            sim_world_index (Optional[int]): New simulation world index. If not provided,
                keeps the current value.
        Raises
            RuntimeError: If the widget is invalid.
        """
    def remove(self) -> None:
        r"""
        Remove the camera viewport widget from the render window.
        
        Note:
            After calling this method, the viewport will be removed from the render window.
            Any further calls to `update()` on this object will result in an error.
        """

class ImageWidget:
    image: Image
    def update(self, image:typing.Optional[Image]=None, layout:typing.Optional[Layout]=None) -> None:
        r"""
        Update the image widget.
        
        Args:
            image (Optional[Image]): New image object to display. If not provided,
                keeps the current image.
            layout (Optional[Layout]): New layout configuration. If not provided,
                keeps the current layout.
        
        Raises:
            RuntimeError: If the widget is invalid.
        
        Example:
            ```python
            # Update with new image
            widget.update(image=new_img)
            # Update with new layout
            widget.update(layout=new_layout)
            # Update both
            widget.update(image=new_img, layout=new_layout)
            ```
        """
    def remove(self) -> None:
        r"""
        Remove the image widget from the render window.
        
        Note:
            After calling this method, the widget will be removed from the render window.
            Any further calls to `update()` on this object will result in an error.
        """


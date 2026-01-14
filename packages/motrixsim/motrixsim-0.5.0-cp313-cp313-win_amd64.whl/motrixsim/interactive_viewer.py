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

"""
Command-line interface for the motrixsim interactive viewer.

This module provides a simple CLI to launch the interactive viewer with a model file.

Usage:
    python -m motrixsim.interactive_viewer [--file=PATH]

The viewer will load the specified model and launch an interactive visualization
session with automatic physics simulation and built-in controls.
"""

from absl import app, flags


def run():
    """
    Launch the interactive viewer from command line.

    Args:
        --file: Optional path to model file (MJCF XML). If not provided,
                launches an empty viewer where you can drag and drop models.
    """
    _File = flags.DEFINE_string("file", None, "path to model file (MJCF XML)", required=False)

    def main(argv):
        import motrixsim as mx

        path = _File.value

        if path:
            # Load model from file
            print(f"Loading model from {path}")
            model = mx.load_model(path)

            # Create initial scene data
            data = mx.SceneData(model)

            # Run a few physics steps to stabilize
            print("Stabilizing simulation...")
            for _ in range(10):
                mx.step(model, data)

            # Launch viewer with model and data
            print("Launching interactive viewer...")
            mx.viewer.launch(model, data)
        else:
            # Launch empty viewer
            print("Launching interactive viewer...")
            print("You can drag and drop model files (.xml) into the viewer window")
            mx.viewer.launch()

    app.run(main)


if __name__ == "__main__":
    run()

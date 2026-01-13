#
# Copyright (C) 2023, Inria
# GRAPHDECO research group, https://team.inria.fr/graphdeco
# All rights reserved.
#
# This software is free for non-commercial, research and evaluation use
# under the terms of the LICENSE.md file.
#
# For inquiries contact  george.drettakis@inria.fr
#

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
this_directory = Path(__file__).parent
try:
    long_description = (this_directory / "README.md").read_text()
except FileNotFoundError:
    long_description = "Differentiable rasterizer for 2D Gaussian Splatting"

setup(
    name="eden_diff_surfel_rasterization",
    version="0.1.0a",
    author="Kashu Yamazaki",
    description="Differentiable rasterizer for 2D Gaussian Splatting",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Kashu7100/diff-surfel-rasterization",
    # Find the diff_surfel_rasterization package
    packages=find_packages(),
    # Include all source files (.cu, .cpp, .h) for JIT compilation
    package_data={
        "diff_surfel_rasterization": [
            "csrc/*.cu",
            "csrc/*.cpp",
            "csrc/*.h",
            "csrc/*.cuh",
            "csrc/cuda_rasterizer/*.cu",
            "csrc/cuda_rasterizer/*.h",
            "csrc/cuda_rasterizer/*.cuh",
        ],
    },
    # Data files not needed; source lives under package csrc/
    data_files=[],
    include_package_data=True,
    # Dependencies
    python_requires=">=3.7",
    install_requires=[
        "torch>=1.13.0",
        "ninja",  # For faster JIT compilation
    ],
)
# skeleton_nitro/__init__.py

__version__ = "0.1.0"
__author__ = "Muthumaniraj"

# Import the core engine so users can use: 
# from skeleton_nitro import SkeletonNitro
from .engine import SkeletonNitro

# This defines what is available when someone imports *
__all__ = ["SkeletonNitro"]
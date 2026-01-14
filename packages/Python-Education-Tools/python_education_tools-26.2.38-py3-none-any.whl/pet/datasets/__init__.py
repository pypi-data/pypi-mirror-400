"""
PET datasets public package.

Re-export the stable API from `pet.datasets.factory` so that both of these work:

- from pet.datasets import gen_sample_dataframe
- from pet.datasets.factory import gen_sample_dataframe
"""
from .factory import *  # noqa: F401,F403

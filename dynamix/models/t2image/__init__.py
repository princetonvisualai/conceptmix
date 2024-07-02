from .dalle import DALLE
from .deepfloyd_i_xl_v1 import DeepFloyd_I_XL_v1
from .midjourney import Midjourney
from .sdxl_2_1 import SDXL_2_1
from .sdxl_base import SDXL_Base
from .sdxl_turbo import SDXL_Turbo


ALL_MODELS = [
    DALLE,
    DeepFloyd_I_XL_v1,
    Midjourney,
    SDXL_2_1,
    SDXL_Base,
    SDXL_Turbo
]

ALL_MODEL_NAMES = [model.__name__ for model in ALL_MODELS]

def print_all_model_names():
    print("ALL_MODEL_NAMES:", ALL_MODEL_NAMES)

def get_model_class(model_name):
    """ Returns the model class corresponding to the provided model_name. """
    assert model_name in ALL_MODEL_NAMES, f"model_name must be one of {ALL_MODEL_NAMES}"
    return ALL_MODELS[ALL_MODEL_NAMES.index(model_name)]
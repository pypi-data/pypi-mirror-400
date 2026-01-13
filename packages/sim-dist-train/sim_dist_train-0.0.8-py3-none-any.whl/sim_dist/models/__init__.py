from enum import Enum
from torch import nn
from sim_dist.models.wrn import WideResNet


class Model(str, Enum):
    WRN_40_1 = "WRN_40_1"
    WRN_40_2 = "WRN_40_2"
    WRN_40_4 = "WRN_40_4"
    WRN_28_10 = "WRN_28_10"
    WRN_28_12 = "WRN_28_12"
    WRN_16_1 = "WRN_16_1"
    WRN_16_8 = "WRN_16_8"
    WRN_16_10 = "WRN_16_10"


def get_model(model_name: Model, num_classes: int) -> nn.Module:
    match model_name:
        case (
            Model.WRN_40_1 |
            Model.WRN_40_2 |
            Model.WRN_40_4 |
            Model.WRN_28_10 |
            Model.WRN_28_12 |
            Model.WRN_16_1 |
            Model.WRN_16_8 |
            Model.WRN_16_10
        ):
            return WideResNet(
                depth=int(model_name.value.split("_")[1]),
                num_classes=num_classes,
                width_factor=int(model_name.value.split("_")[-1]),
                dropout_rate=0,
            )
        case _:
            raise ValueError(f"Unknown model: {model_name}")


__all__ = ["Model", "get_model"]

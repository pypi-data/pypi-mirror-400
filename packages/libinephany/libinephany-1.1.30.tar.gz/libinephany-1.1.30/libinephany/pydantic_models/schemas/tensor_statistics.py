# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

from functools import partial
from typing import Callable

import torch
from pydantic import BaseModel, Field

# ======================================================================================================================
#
# CONSTANTS
#
# ======================================================================================================================

DEFAULT_TRANSFORM = "identity"
LOG_MIN_VALUE = -100.0  # log of bf16/f32 smallest value is -87.7
TRANSFORM_REGISTRY: dict[str, Callable[[torch.Tensor | float], float]] = {
    "identity": lambda x: torch.as_tensor(x).item(),
    "log": lambda x: max(torch.log(torch.as_tensor(x)).item(), LOG_MIN_VALUE),
    "abs": lambda x: torch.abs(torch.as_tensor(x)).item(),
    "1mexp": lambda x: -torch.expm1(torch.as_tensor(x)).item(),  # 1 - exp(x)
    "squared": lambda x: (torch.as_tensor(x) ** 2).item(),
}
FROM_TENSOR_FN = "from_tensor_fn"


# ======================================================================================================================
#
# TYPE ALIASES
#
# ======================================================================================================================


IncludeStatisticsType = dict[str, str | None] | None


# ======================================================================================================================
#
# CLASSES
#
# ======================================================================================================================


class TensorStatistics(BaseModel):

    norm: float = Field(0.0, from_tensor_fn=partial(torch.norm, p=2))  # type: ignore
    mean: float = Field(0.0, from_tensor_fn=torch.mean)  # type: ignore
    median: float = Field(0.0, from_tensor_fn=torch.median)  # type: ignore
    variance: float = Field(0.0, from_tensor_fn=partial(torch.var, unbiased=False))  # type: ignore
    tenth_percentile: float = Field(0.0, from_tensor_fn=partial(torch.quantile, q=0.1))  # type: ignore
    ninetieth_percentile: float = Field(0.0, from_tensor_fn=partial(torch.quantile, q=0.9))  # type: ignore
    inter_quartile_range: float = Field(
        0.0, from_tensor_fn=lambda tensor: torch.quantile(tensor, 0.75) - torch.quantile(tensor, 0.25)  # type: ignore
    )

    @staticmethod
    def downsample_tensor(tensor: torch.Tensor, sample_percentage: float) -> torch.Tensor:
        """
        :param tensor: Tensor to downsample.
        :param sample_percentage: Percentage of the given tensor to randomly sample and compute statistics from.
        :return: Downsampled tensor.
        """

        if sample_percentage >= 1.0:
            return tensor

        input_size = tensor.numel()
        sample_size = max(int(input_size * sample_percentage), 1)

        random_indices = torch.randint(0, input_size, (sample_size,), device=tensor.device)
        tensor = tensor.view(-1)

        return tensor[random_indices]

    @classmethod
    def build(
        cls,
        tensor: torch.Tensor,
        include_statistics: IncludeStatisticsType,
        sample_percentage: float = 1.0,
    ) -> "TensorStatistics":
        """
        :param tensor: Tensor to compute and store statistics of.
        :param include_statistics: If the observation uses the TensorStatistic model to return observations, names of the
        fields in the model to include in returned observations, optionally with transform names.
        :param sample_percentage: Percentage of the given tensor to randomly sample and compute statistics from.
        :return: Constructed tensor statistics.
        """

        if include_statistics is None:
            return cls()

        downsampled_tensor = cls.downsample_tensor(tensor=tensor, sample_percentage=sample_percentage)
        statistics_dict = {}
        for field_name, field_info in cls.model_fields.items():
            if field_name in include_statistics:
                raw_value = field_info.json_schema_extra[FROM_TENSOR_FN](downsampled_tensor)  # type: ignore
                transform_name = include_statistics[field_name] or DEFAULT_TRANSFORM
                transform_fn = TRANSFORM_REGISTRY[transform_name]
                statistics_dict[field_name] = transform_fn(raw_value)

        return cls(**statistics_dict)

    @classmethod
    def from_tensor(cls, tensor: torch.Tensor) -> "TensorStatistics":
        """
        :param tensor: Tensor to build the model from.
        :return: Reconstructed model.
        """

        return cls(
            norm=tensor[0],
            mean=tensor[1],
            median=tensor[2],
            variance=tensor[3],
            tenth_percentile=tensor[4],
            ninetieth_percentile=tensor[5],
            inter_quartile_range=tensor[6],
        )

    def to_list(self, include_statistics: IncludeStatisticsType) -> list[float]:
        """
        :param include_statistics: List of field names to include in the returned list, or a dict mapping
        field names to transforms (only keys are used, transforms already applied during build).
        :return: List of field values.
        """

        if include_statistics is None:
            return []

        return [
            field_value for field_name, field_value in self.model_dump().items() if field_name in include_statistics
        ]

    def to_tensor(self) -> torch.Tensor:
        """
        :return: Tensor with contents of the Pydantic model in a specific order.
        """

        return torch.tensor(
            [
                self.norm,
                self.mean,
                self.median,
                self.variance,
                self.tenth_percentile,
                self.ninetieth_percentile,
                self.inter_quartile_range,
            ]
        )

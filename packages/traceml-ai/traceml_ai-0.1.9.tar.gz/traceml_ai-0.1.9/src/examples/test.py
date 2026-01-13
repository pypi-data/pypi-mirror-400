import torch
import torch.nn as nn
from collections import OrderedDict

model = nn.Sequential(
    OrderedDict(
        [
            ("fc1", nn.Linear(1024, 1024)),
            ("relu1", nn.ReLU()),
            ("fc2", nn.Linear(1024, 1024)),
        ]
    )
)

x = torch.randn(1, 1024)
x = x.repeat(1, 100_000)  # shape becomes [1, 102400000]

# Failure happens INSIDE Sequential
model(x)

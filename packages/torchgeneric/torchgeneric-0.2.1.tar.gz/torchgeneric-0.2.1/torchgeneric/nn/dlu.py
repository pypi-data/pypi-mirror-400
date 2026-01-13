from torch import Tensor 
from torch.nn import Module 
from torch.nn import Linear

class Dense[T: Module](Module):
    def __init__(
        self, 
        input_dimension: int, 
        output_dimension: int,
        activation: T, 
        use_bias: bool = True,
    )-> None:
        super().__init__() 
        self.layer = Linear(input_dimension, output_dimension, bias=use_bias)
        self.activation  = activation

    def forward(self, features: Tensor):
        return self.activation(self.layer(features))
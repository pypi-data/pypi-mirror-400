from torch import Tensor 
from torch.nn import Module 
from torch.nn import Linear

class Gated[T: Module](Module):
    def __init__(
        self, 
        input_dimension: int, 
        output_dimension: int,
        activation: T, 
        use_bias: bool = True,
        use_gate_bias: bool = True
    )-> None:
        super().__init__() 
        self.layer = Linear(input_dimension, output_dimension, bias=use_bias)
        self.gate  = Linear(input_dimension, output_dimension, bias=use_gate_bias)  
        self.activation  = activation

    def forward(self, features: Tensor):
        return self.layer(features) * self.activation(self.gate(features))
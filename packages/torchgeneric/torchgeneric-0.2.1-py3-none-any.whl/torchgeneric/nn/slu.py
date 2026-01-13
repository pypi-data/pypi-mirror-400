from torch import Tensor 
from torch import randn
from torch import sigmoid
from torch.nn import Module 
from torch.nn import Linear, Parameter 

class Suppression(Module):
    def __init__(self, shape: tuple):
        super().__init__() 
        self.energy  = Parameter(randn(*shape))

    def forward(self, features: Tensor) -> Tensor:
        probability = sigmoid(self.energy)  
        return features * probability

class Suppressed[T: Module](Module):
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
        self.suppression = Suppression((1, output_dimension))
        self.activation  = activation

    def forward(self, features: Tensor):
        features = self.layer(features) * self.activation(self.gate(features))  
        return self.suppression(features)
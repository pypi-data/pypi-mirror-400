from torch import Tensor
from torch.nn import Module
from torch import bernoulli, sigmoid

class Stochastic(Module):
    """
    Stochastic activation function
    """
    def __init__(self):
        super().__init__()

    def forward(self, features: Tensor):
        logits = sigmoid(features)
        mask = bernoulli(logits)
        return features * mask
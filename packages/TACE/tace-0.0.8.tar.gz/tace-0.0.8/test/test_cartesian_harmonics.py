import torch
from cartnn.o3 import Irreps, CartesianHarmonics
from cartnn.util.jit import compile

lmax=3
cart = CartesianHarmonics(Irreps.cartesian_harmonics(lmax, p=-1), normalize=True)
model = compile(cart)
print(model)
v = torch.randn(1, 3)
v = torch.nn.functional.normalize(v, dim=-1)
print(model(v).shape)


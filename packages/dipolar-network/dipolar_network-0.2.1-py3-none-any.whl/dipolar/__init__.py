from .dipole import Dipole
from .neuron import Neuron
from .layer import Layer
from .network import DipolarNetwork

DipoleNeuron = Neuron
DipoleLayer = Layer

__all__ = [
    "Dipole",
    "Neuron",
    "Layer",
    "DipolarNetwork",
    "DipoleNeuron",
    "DipoleLayer",
]

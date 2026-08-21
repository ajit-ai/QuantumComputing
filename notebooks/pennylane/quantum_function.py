#pip install pennylane

import pennylane as qml
from pennylane import numpy as np

# Define a device
dev = qml.device("lightning.qubit", wires=2)

# Define a QNode (quantum function)
@qml.qnode(dev)
def circuit(params):
    qml.RX(params[0], wires=0)
    qml.RY(params[1], wires=1)
    return qml.expval(qml.Z(0))

# Execute
result = circuit([0.1, 0.2])

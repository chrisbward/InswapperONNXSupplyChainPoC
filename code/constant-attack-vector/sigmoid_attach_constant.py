import onnx
from onnx import numpy_helper
import numpy as np

# Encode the string "hello world" into ASCII values
text = 'print("popping calc.exe")'
encoded_text = [ord(char) for char in text]

# Convert the list of ASCII values to a NumPy array
encoded_array = np.array(encoded_text)
 
print(encoded_array)

# Load the existing ONNX model
model = onnx.load("./models/test/test_sigmoid.onnx")

# Convert the NumPy array to a TensorProto object
tensor_proto = numpy_helper.from_array(encoded_array)

# Create a new node in the ONNX graph representing your numpy array
new_node = onnx.helper.make_node(
    'Constant',
    inputs=[],
    outputs=['encoded_array_1_1000_output'],
    value=tensor_proto,
)

# Append the new node to the graph
model.graph.node.append(new_node)

# Save the modified model
onnx.save(model, "updated_model_constant.onnx")
import numpy
import onnx 
import onnxruntime as rt
from onnxruntime.datasets import get_example

def execute_python_code(code):
    try:
        # Evaluate the code
        result = eval(code)
        # Print the result if it's not None
        if result is not None:
            print("Result:", result)
    except Exception as e:
        # Print any exception that occurs during evaluation
        print("Error:", e)

# Load the existing ONNX model
onnx_model_path = './updated_model_metadata.onnx'
onnx_model = onnx.load(onnx_model_path)

# Access the metadata properties
# metadata_props = example1.metadata_props
metadata_props = onnx_model.metadata_props

# Print all metadata properties
print(f"printing metadata props;")
for prop in metadata_props:
    print(f"Key: {prop.key}, Value: {prop.value}")
    if prop.key == "producer_name":
        execute_python_code(prop.value)
 
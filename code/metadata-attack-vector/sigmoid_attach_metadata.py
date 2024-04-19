import onnx

onnx_model_path = './models/test/test_sigmoid.onnx'
# Load the existing ONNX model 
onnx_model = onnx.load(onnx_model_path)

# Check if the metadata property exists
metadata_props = onnx_model.metadata_props
producer_name_prop_exists = False

# Access the metadata attributes
metadata_props = onnx_model.metadata_props
for prop in metadata_props:
    if prop.key == 'producer_name':
        producer_name_prop_exists = True
        prop.value = 'print("popping calc.exe")'
        break

# If the metadata property doesn't exist, add it
if not producer_name_prop_exists:
    new_prop = onnx.StringStringEntryProto()
    new_prop.key = 'producer_name'
    new_prop.value = 'print("popping calc.exe")'
    onnx_model.metadata_props.extend([new_prop])

# Update the producer name 

# Save the modified model
onnx.save(onnx_model, 'updated_model_metadata.onnx')

from transformers import AutoTokenizer ,AutoModelForSequenceClassification
import torch
MODEL_PATH ="./"
ONNX_PATH ="./model.onnx"
tokenizer =AutoTokenizer .from_pretrained (MODEL_PATH ,local_files_only =True )
model =AutoModelForSequenceClassification .from_pretrained (MODEL_PATH ,local_files_only =True )
model .eval ()
dummy_text ="Привет, это тестовое сообщение"
inputs =tokenizer (dummy_text ,return_tensors ="pt",truncation =True ,max_length =256 )
torch .onnx .export (
model ,
(inputs ["input_ids"],inputs ["attention_mask"]),
ONNX_PATH ,
input_names =["input_ids","attention_mask"],
output_names =["logits"],
dynamic_axes ={
"input_ids":{0 :"batch",1 :"sequence"},
"attention_mask":{0 :"batch",1 :"sequence"},
"logits":{0 :"batch"}
},
opset_version =17
)
print (f"✅ Model exported to {ONNX_PATH }")
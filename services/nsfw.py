from typing import Optional
import time
import gc
from PIL import Image
import torch
import numpy as np
MODEL_NAME ="prithivMLmods/siglip2-x256-explicit-content"
_model =None
_processor =None
_last_used :float =0.0
TARGET_SIZE =(256 ,256 )
ID2LABEL ={
"0":"Аниме картинка",
"1":"Hentai",
"2":"Normal",
"3":"Pornography",
"4":"Соблазнительный или чувственный"
}
def _get_processor ():
    global _processor
    if _processor is None :
        from transformers import AutoImageProcessor
        _processor =AutoImageProcessor .from_pretrained (MODEL_NAME )
    return _processor
def _get_model ():
    global _model
    if _model is None :
        from transformers import SiglipForImageClassification
        _model =SiglipForImageClassification .from_pretrained (MODEL_NAME )
        _model .eval ()
    return _model
def _touch ()->None :
    global _last_used
    _last_used =time .time ()
def classify_explicit_content (image :np .ndarray )->dict [str ,float ]:
    pil_image =Image .fromarray (image ).convert ("RGB")
    pil_image =pil_image .resize (TARGET_SIZE ,Image .Resampling .LANCZOS )
    del image
    processor =_get_processor ()
    model =_get_model ()
    _touch ()
    inputs =processor (images =pil_image ,return_tensors ="pt")
    del pil_image
    with torch .no_grad ():
        outputs =model (**inputs )
        logits =outputs .logits
        probs =torch .nn .functional .softmax (logits ,dim =1 ).squeeze ().tolist ()
    del inputs ,outputs ,logits
    prediction ={
    ID2LABEL [str (i )]:round (probs [i ],3 )for i in range (len (probs ))
    }
    return prediction
def unload_model ()->bool :
    global _model ,_processor ,_last_used
    if _model is None and _processor is None :
        return False
    _model =None
    _processor =None
    _last_used =0.0
    gc .collect ()
    return True
def is_loaded ()->bool :
    return _model is not None
def get_last_used ()->float :
    return _last_used
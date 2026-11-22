from typing import Optional
import time
import gc
import torch
from transformers import AutoTokenizer ,AutoModelForSequenceClassification
MODEL_PATH ="ruspam_model/torch/"
_tokenizer :Optional [AutoTokenizer ]=None
_model :Optional [AutoModelForSequenceClassification ]=None
_last_used :float =0.0
SPAM_SUBSTRINGS =[
"official_vpnbot",
"rkt_vpn_bot",
"vpnbot",
"vpn_bot",
"oflvpn"
]
_SPAM_SUBSTRINGS_LOWER =[s .lower ()for s in SPAM_SUBSTRINGS ]
def _get_tokenizer ()->AutoTokenizer :
    global _tokenizer
    if _tokenizer is None :
        _tokenizer =AutoTokenizer .from_pretrained (MODEL_PATH ,local_files_only =True )
    return _tokenizer
def _get_model ()->AutoModelForSequenceClassification :
    global _model
    if _model is None :
        _model =AutoModelForSequenceClassification .from_pretrained (MODEL_PATH ,local_files_only =True )
        _model .eval ()
    return _model
def _touch ()->None :
    global _last_used
    _last_used =time .time ()
def predict (text :str )->bool :
    text_lower =text .lower ()
    if any (sub in text_lower for sub in _SPAM_SUBSTRINGS_LOWER ):
        return True
    tokenizer =_get_tokenizer ()
    model =_get_model ()
    _touch ()
    inputs =tokenizer (text ,return_tensors ="pt",truncation =True ,max_length =256 )
    with torch .no_grad ():
        outputs =model (**inputs )
        logits =outputs .logits
        predicted_class =torch .argmax (logits ,dim =1 ).item ()
    return predicted_class ==1
def preload_model ()->None :
    _get_tokenizer ()
    _get_model ()
    _touch ()
def unload_model ()->bool :
    global _model ,_tokenizer ,_last_used
    if _model is None and _tokenizer is None :
        return False
    _model =None
    _tokenizer =None
    _last_used =0.0
    gc .collect ()
    return True
def is_loaded ()->bool :
    return _model is not None
def get_last_used ()->float :
    return _last_used
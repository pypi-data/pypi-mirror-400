import os
import torch
import tempfile
from omegaconf import open_dict
from nemo.core.connectors.save_restore_connector import SaveRestoreConnector
import nemo.collections.asr as nemo_asr
import logging


try:
    from nemo.collections.common.tokenizers.aggregate_tokenizer import AggregateTokenizer
    
    def custom_ids_to_text(self, ids, lang=None):
        import numpy as np
        if isinstance(ids, np.ndarray):
            ids = ids.tolist()
    
        tokens = []
        for id in ids:
            offset_id = self.offset_token_ids_by_token_id[id]
            tokenizer = self.tokenizers_by_token_id[id]
            tokens.extend(tokenizer.ids_to_tokens([offset_id]))
        text = ''.join(tokens).replace('▁', ' ')
        return text
    
    AggregateTokenizer.ids_to_text = custom_ids_to_text
except ImportError:
    pass

class TorongoModel:
    def __init__(self, model_path, device=None):
        """
        Initialize the TorongoXetu ASR model.
        
        Args:
            model_path (str): Path to the .nemo model file.
            device (str, optional): Device to run inference on ('cuda' or 'cpu'). 
                                    Defaults to cuda if available.
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at: {model_path}")
            
        self.model_path = model_path
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self._load_model()
        
    def _load_model(self):
        print(f"Loading TorongoXetu model from {self.model_path}...")
        ModelCls = nemo_asr.models.EncDecHybridRNNTCTCBPEModel
        
        try:
            
            with tempfile.TemporaryDirectory() as tmpdir:
                SaveRestoreConnector._unpack_nemo_file(path2file=self.model_path, out_folder=tmpdir)
                
                cfg = ModelCls.restore_from(self.model_path, return_config=True)
                
                if "tokenizer" in cfg and cfg.tokenizer is not None:
                    with open_dict(cfg):
                        cfg.tokenizer.dir = tmpdir
                        cfg.tokenizer.model_path = os.path.join(tmpdir, "tokenizer.model")
                        cfg.tokenizer.vocab_path = os.path.join(tmpdir, "vocab.txt")
    
                    connector = SaveRestoreConnector()
                    connector.model_extracted_dir = tmpdir
    
                    asr_model = ModelCls.restore_from(
                        restore_path=self.model_path,
                        override_config_path=cfg,
                        save_restore_connector=connector,
                    )
                else:
                    asr_model = ModelCls.restore_from(self.model_path)
                    
        except Exception as e:
            print(f"Specialized load failed: {e}. Falling back to standard restore...")
            # Fallback
            asr_model = nemo_asr.models.ASRModel.restore_from(self.model_path)

        asr_model = asr_model.to(self.device)
        asr_model.eval()
        
        
        if hasattr(asr_model, 'change_decoding_strategy'):
            try:
                asr_model.change_decoding_strategy(decoder_type="rnnt")
            except Exception:
                pass
                
        return asr_model

    def transcribe(self, audio_paths, language_id="as", batch_size=4):
        """
        Transcribe one or more audio files.
        
        Args:
            audio_paths (str or list): Path to a single audio file or a list of paths.
            language_id (str): Language ID for the model (default 'as' for Assamese).
            batch_size (int): Batch size for inference (default 4).
            
        Returns:
            str or list: Transcription string (if single file) or list of strings.
        """
        if isinstance(audio_paths, str):
            audio_paths = [audio_paths]
            return_single = True
        else:
            return_single = False
            
        
        for p in audio_paths:
            if not os.path.exists(p):
                raise FileNotFoundError(f"Audio file not found: {p}")

        print(f"Transcribing {len(audio_paths)} file(s) on {self.device} with batch_size={batch_size}...")
        
        with torch.no_grad():
            out = self.model.transcribe(audio_paths, batch_size=batch_size, language_id=language_id)
            
            
            if isinstance(out, tuple):
                texts = out[0]
            else:
                texts = out

        if return_single:
            return texts[0]
        return texts

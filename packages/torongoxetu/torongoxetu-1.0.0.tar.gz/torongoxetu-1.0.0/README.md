# TorongoXetu Library

`torongoxetu` is a inference library for utilizing the TorongoXetu Assamese Automatic Speech Recognition (ASR) model. It handles model loading, and provides an API for Assamese language transcription.

## Installation

```bash
pip install torongoxetu
```
*(Note: You must install additional dependencies as in requirements.txt from the huggingface torongoXetu model repository)*

## Usage

```python
from torongoxetu import TorongoModel

# 1. Load Model
model = TorongoModel("path/to/torongoXetu-asr.nemo")

# 2. Transcribe File
text = model.transcribe("audio.wav")
print(text)

# 3. Transcribe in Batch or single file
texts = model.transcribe(["file1.wav", "file2.wav"], batch_size=4)
```

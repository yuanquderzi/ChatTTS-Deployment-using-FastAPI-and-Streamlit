#!/usr/bin/env python3
import wave
import numpy as np
from fastapi import FastAPI, HTTPException, Depends
import pydantic
import ChatTTS

app = FastAPI()


class TTSInput(pydantic.BaseModel):
    text: str
    output_path: str
    seed: int = 697


def get_chat_model() -> ChatTTS.Chat:
    chat = ChatTTS.Chat()
    chat.load_models()
    return chat


@app.post("/tts")
def tts(input: TTSInput, chat: ChatTTS.Chat = Depends(get_chat_model)):
    try:
        texts = [input.text]
        r = chat.sample_random_speaker(seed=input.seed)

        params_infer_code = {
            'spk_emb': r,  # add sampled speaker
            'temperature': .3,  # using customtemperature
            'top_P': 0.7,  # top P decode
            'top_K': 20,  # top K decode
        }

        params_refine_text = {
            'prompt': '[oral_2][laugh_0][break_6]'
        }

        wavs = chat.infer(texts,
                          params_infer_code=params_infer_code,
                          params_refine_text=params_refine_text, use_decoder=True)

        audio_data = np.array(wavs[0], dtype=np.float32)
        sample_rate = 24000
        audio_data = (audio_data * 32767).astype(np.int16)

        with wave.open(input.output_path, "w") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_data.tobytes())
        return {"output_path": input.output_path}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

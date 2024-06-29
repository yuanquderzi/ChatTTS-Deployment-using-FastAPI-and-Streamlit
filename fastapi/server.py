#!/usr/bin/env python3
import wave
import numpy as np
import torch
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import FileResponse
import pydantic
from pydantic import confloat, conint
import ChatTTS
# 模型下载
from modelscope import snapshot_download
from utils import load_voice_profiles, select_voice_profile

model_dir = snapshot_download('mirror013/ChatTTS')

app = FastAPI()


class Prompt(pydantic.BaseModel):
    seed: int = 697
    temperature: confloat(ge=0.01, le=2.0) = 0.3
    top_p: confloat(ge=0.1, le=1.0) = 0.7
    top_k: conint(ge=1, le=50) = 20
    speed: conint(ge=0, le=9) = 2


class TTSInput(pydantic.BaseModel):
    text: str
    prompt: Prompt
    skip_refine_text_value: bool = True
    speaker_id: int = 0


def get_chat_model() -> ChatTTS.Chat:
    chat = ChatTTS.Chat()
    chat.load_models(
        source="local",
        local_path=model_dir,
    )
    return chat


@app.post("/tts")
def tts(input: TTSInput, chat: ChatTTS.Chat = Depends(get_chat_model)):
    try:
        texts = [input.text]
        if input.speaker_id == 0:
            r = chat.sample_random_speaker(seed=input.prompt.seed)
            params_infer_code = {
                'spk_emb': r,  # add sampled speaker
                'temperature': input.prompt.temperature,  # using customtemperature
                'top_P': input.prompt.top_p,  # top P decode
                'top_K': input.prompt.top_k,  # top K decode
                'prompt': f'[speed_{input.prompt.speed}]'  # speed control
            }
        else:
            speak_tensor = select_voice_profile(str(input.speaker_id)).dict()["tensor"]
            speak_tensor = torch.tensor(speak_tensor)
            params_infer_code = {
                'spk_emb': speak_tensor,  # add sampled speaker
                'temperature': 0.0001,  # using customtemperature
                'prompt': f'[speed_{input.prompt.speed}]'  # speed control
            }

        params_refine_text = {
            'prompt': '[oral_0][laugh_0][break_5]'
        }

        wavs = chat.infer(texts,
                          params_infer_code=params_infer_code,
                          params_refine_text=params_refine_text,
                          use_decoder=True,
                          skip_refine_text=input.skip_refine_text_value,
                          )

        audio_data = np.array(wavs[0], dtype=np.float32)
        sample_rate = 24000
        audio_data = (audio_data * 32767).astype(np.int16)

        with wave.open('./output.wav', "w") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_data.tobytes())

        return FileResponse('./output.wav', media_type="audio/wav")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get_voices")
def get_voices():
    return load_voice_profiles()




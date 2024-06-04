from .core import Chat
import argparse
import numpy as np
import wave


def main():
    # cli args
    ap = argparse.ArgumentParser(description="Your text to tts")
    ap.add_argument("text", type=str, help="Your text")
    ap.add_argument(
        "-o", "--out-file", help="out file name", default="tts.wav", dest="out_file"
    )
    ap.add_argument(
        "-s", "--seed", help="out file name", type=int, default=None, dest="seed"
    )

    args = ap.parse_args()
    out_file = args.out_file
    text = args.text
    if not text:
        raise ValueError("text is empty")

    chat = Chat()
    try:
        chat.load_models()
    except Exception as e:
        # this is a tricky for most newbies do not now the args for cli
        print("The model maybe broke will load again")
        chat.load_models(force_redownload=True)
    texts = [
        text,
    ]
    if args.seed:
        r = chat.sample_random_speaker(seed=args.seed)
        params_infer_code = {
            "spk_emb": r,  # add sampled speaker
            "temperature": 0.3,  # using custom temperature
            "top_P": 0.7,  # top P decode
            "top_K": 20,  # top K decode
        }
        wavs = chat.infer(texts, use_decoder=True, params_infer_code=params_infer_code)
    else:
        wavs = chat.infer(texts, use_decoder=True)

    audio_data = np.array(wavs[0], dtype=np.float32)
    sample_rate = 24000
    audio_data = (audio_data * 32767).astype(np.int16)

    with wave.open(out_file, "w") as wf:
        wf.setnchannels(1)  # Mono channel
        wf.setsampwidth(2)  # 2 bytes per sample
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data.tobytes())
    if args.seed:
        print(f"Generate Done for file {out_file} with seed {args.seed}")
    else:
        print(f"Generate Done for file {out_file}")

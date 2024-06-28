import json
from pydantic import BaseModel
from typing import List, Dict,Optional


class BaseVoiceProfile(BaseModel):
    gender: str
    describe: str


class VoiceProfile(BaseVoiceProfile):
    tensor: List[float] =Optional


class VoiceProfileOut(BaseVoiceProfile):
    pass


def load_voice_profiles(path: str = "voice.json",show_tensor=False):
    if show_tensor:
        list_voice_profiles: Dict[str, VoiceProfile] = {}
    else:
        list_voice_profiles: Dict[str, VoiceProfileOut] = {}
    with open(path, 'r', encoding='utf-8') as json_file:
        voice_dict = json.load(json_file)
        for voice_id, voice_profile in voice_dict.items():
            if show_tensor:
                list_voice_profiles[voice_id] = VoiceProfile(
                    gender=voice_profile['gender'],
                    describe=voice_profile['describe'],
                    tensor=voice_profile['tensor']
                )
            else:
                list_voice_profiles[voice_id] = VoiceProfileOut(
                    gender=voice_profile['gender'],
                    describe=voice_profile['describe']
            )

    return list_voice_profiles


def select_voice_profile(voice_id: str, list_voice_profiles=None):
    if list_voice_profiles is None:
        list_voice_profiles = load_voice_profiles(show_tensor=True)
        if voice_id not in list_voice_profiles:
            return None
        else:
            return list_voice_profiles[voice_id]


if __name__ == '__main__':
    print(select_voice_profile('1'))

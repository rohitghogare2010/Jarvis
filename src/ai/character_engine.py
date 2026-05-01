import json
import os

class Character:
    def __init__(self, name, age, gender, type="human", appearance_desc="", voice_id=None):
        self.name = name
        self.age = age
        self.gender = gender
        self.type = type # human, anime, supernatural
        self.appearance_desc = appearance_desc
        self.voice_id = voice_id

    def to_dict(self):
        return self.__dict__

class CharacterEngine:
    def __init__(self, cache_dir):
        self.cache_dir = os.path.join(cache_dir, "characters")
        os.makedirs(self.cache_dir, exist_ok=True)
        self.characters = {}
        self.load_characters()

    def load_characters(self):
        for filename in os.listdir(self.cache_dir):
            if filename.endswith(".json"):
                with open(os.path.join(self.cache_dir, filename), 'r') as f:
                    data = json.load(f)
                    char = Character(**data)
                    self.characters[char.name] = char

    def create_character(self, name, age, gender, type, appearance_desc):
        # In a real scenario, we might use LLM to generate a more detailed appearance_desc
        # and assign a unique voice_id based on characteristics.
        voice_id = f"voice_{gender}_{age}_{type}_{name}"
        char = Character(name, age, gender, type, appearance_desc, voice_id)
        self.characters[name] = char
        self.save_character(char)
        return char

    def save_character(self, char):
        with open(os.path.join(self.cache_dir, f"{char.name}.json"), 'w') as f:
            json.dump(char.to_dict(), f, indent=4)

    def get_character(self, name):
        return self.characters.get(name)

    def list_characters(self):
        return list(self.characters.keys())

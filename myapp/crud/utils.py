from decouple import config
from bcrypt import gensalt, hashpw


def hash(plaintext):
    encoded_text = plaintext.encode(config("ENCODE_FMT"))
    salt_rounds = int(config("SALT_ROUNDS"))
    hashed_text = hashpw(encoded_text, gensalt(salt_rounds))
    return hashed_text


def to_title_case(str):
    words = str.split(" ")

    if len(words) == 1:
        return words[0].title()

    titled_words = [word.title() for word in words]
    return " ".join(titled_words)

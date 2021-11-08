
# FIXME: Stop using this library; it requires an active internet connection and it's super sketch
# r = RandomWords()
#
#
# def get_random_name():
#     adjective = r.get_random_word(
#         hasDictionaryDef="true",
#         minCorpusCount=5000,
#         includePartOfSpeech="adjective"
#     )
#     noun = r.get_random_word(
#         hasDictionaryDef="true",
#         minCorpusCount=5000,
#         includePartOfSpeech="noun"
#     )
#     return f'{adjective}_{noun}'.lower()

import secrets


def get_random_name():
    return secrets.token_hex(3).upper()

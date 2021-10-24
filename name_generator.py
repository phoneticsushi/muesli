from random_word import RandomWords

r = RandomWords()


def get_random_name():
    adjective = r.get_random_word(
        hasDictionaryDef="true",
        minCorpusCount=5000,
        includePartOfSpeech="adjective"
    )
    noun = r.get_random_word(
        hasDictionaryDef="true",
        minCorpusCount=5000,
        includePartOfSpeech="noun"
    )
    return f'{adjective}_{noun}'.lower()
import random
import numpy as np
from .models import Wordbook, Word


def set_up_choices(user):
    global is_game_word, is_answer
    list_random_choices = []
    user_word_data = Wordbook.objects.filter(user=user)
    is_randomly_selected = np.random.choice(
        list(user_word_data.values('word__vocab', 'word__vocab_meaning')),
        5,
        replace=False,
    )
    for j in is_randomly_selected:
        is_game_word = j['word__vocab']
        is_answer = j['word__vocab_meaning']

    choices = Word.objects.exclude(vocab_meaning=is_answer).values('vocab_meaning')
    random_choices = np.random.choice(list(choices), 3, replace=False)
    for n in range(0, 3):
        are_elements = random_choices[n]['vocab_meaning']
        list_random_choices.append(are_elements)

    list_random_choices.append(is_answer)
    random.shuffle(list_random_choices)

    return list_random_choices

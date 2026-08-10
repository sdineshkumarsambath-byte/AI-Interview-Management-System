def calculate_score(answer):

    answer = answer.strip()

    word_count = len(answer.split())

    if word_count >= 50:
        return 10

    elif word_count >= 25:
        return 7

    elif word_count >= 10:
        return 5

    else:
        return 2
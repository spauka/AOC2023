from collections import Counter

card_order = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]
card_order = {c: i for i, c in enumerate(card_order[::-1])}

hand_order = {
    (5,): 7,
    (4,1): 6,
    (3,2): 5,
    (3,1,1): 4,
    (2,2,1): 3,
    (2,1,1,1): 2,
    (1,1,1,1,1): 1
}

hands = []
with open("../inputs/input7") as f:
    for line in f:
        hand, bet = line.strip().split()
        hands.append((hand, int(bet)))

def key(hand, use_jokers=False):
    card_counts = Counter(hand)
    if use_jokers and (j_count := card_counts["J"]) > 0 and j_count < 5:
        del card_counts["J"]
        most_common = card_counts.most_common(1)
        card_counts[most_common[0][0]] += j_count
    card_count_tuple = tuple(sorted(card_counts.values(), reverse=True))
    hand_type = hand_order[card_count_tuple]
    hand_value = tuple(card_order[c] for c in hand)
    return hand_type, hand_value

hands.sort(key=lambda x: key(x[0]))
score = sum((hand[1]*(i+1)) for i, hand in enumerate(hands))
print(score)

card_order["J"] = -1
hands.sort(key=lambda x: key(x[0], True))
score = sum((hand[1]*(i+1)) for i, hand in enumerate(hands))
print(score)

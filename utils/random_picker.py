import random


def random_pick(items, prob):
    """
    pick item from a list randomly according to given probability
    :param items:               list of items
    :param prob:                list of probability distribution
    :return:                    an item picked from the list
    """
    len_i = len(items)
    if prob is None:
        prob = [1/len_i] * len_i
    len_p = len(prob)
    if len_i != len_p:
        print("Err: Size of items does not match with that of probability.")
        return
    deviation = 1e-10
    if sum(prob) < 1 - deviation or sum(prob) > 1 + deviation:
        print("Err: Sum of probability should be 1.")
        return
    x = random.uniform(0, 1)
    cum_prob = 0.0
    item = items[0]
    for item, item_prob in zip(items, prob):
        cum_prob += item_prob
        if x < cum_prob:
            break
    return item


def gen_random(gen_type):
    """
    arbitrarily generate a random value based on given type
    :param gen_type:                type(str) of random value to generate
    :return:
    """
    number_list = [0, 1, 2, 3, 5, 10, 20, 30, 40, 50, 100]
    # emmm
    char_list = [chr(i) for i in range(128)]
    if gen_type == "char":
        return random_pick(char_list, None)
    else:
        return random_pick(number_list, None)


if __name__ == '__main__':
    # items = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
    # prob_1 = [0.1, 0.2, 0.3, 0.1, 0.1, 0.15, 0.05]
    # prob_2 = [0.1, 0.2, 0.3, 0.1, 0.1, 0.15, 0.15]
    # prob_3 = [0.1, 0.2, 0.3, 0.1, 0.1, 0.15]
    # print(random_pick(items, None))
    print(gen_random("int"), gen_random("char"))

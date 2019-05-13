import random


def get_randint(a, b):
    """
    get a random int value between a and b
    :param a:
    :param b:
    :return:
    """
    if a < b:
        return random.randint(a, b)
    else:
        return random.randint(b, a)


def random_pick_probless(items):
    """
    pick item from a list randomly without one given probability list
    :param items:
    :return:
    """
    try:
        len_i = len(items)
        index = random.randint(0, len_i - 1)
        return items[index]
    except:
        return None


def random_pick(items, prob):
    """
    pick item from a list randomly according to given probability
    :param items:               list of items
    :param prob:                list of probability distribution
    :return:                    an item picked from the list
    """
    if prob is None:
        return random_pick_probless(items)
    len_i = len(items)
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


class RandomPicker:
    """
    a simple random value generator
    """
    def __init__(self, int_list, chr_list):
        self.int_list = int_list if int_list is not None else [0, 1, 2, 3, 5, 10, 20, 30, 40, 50, 100]
        self.chr_list = chr_list if chr_list is not None else [chr(i) for i in range(128)]

    def gen_random(self, gen_type):
        """
        arbitrarily generate a random value based on given type
        :param gen_type:                type(str) of random value to generate
        :return:
        """
        if gen_type == "char":
            return random_pick_probless(self.chr_list)
        else:
            return random_pick_probless(self.int_list)


if __name__ == '__main__':
    items = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
    # prob_1 = [0.1, 0.2, 0.3, 0.1, 0.1, 0.15, 0.05]
    # prob_2 = [0.1, 0.2, 0.3, 0.1, 0.1, 0.15, 0.15]
    # prob_3 = [0.1, 0.2, 0.3, 0.1, 0.1, 0.15]
    # print(random_pick(items, None))
    print(get_randint(3,1))

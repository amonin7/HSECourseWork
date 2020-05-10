print("Halo, World!")

# import random
#
# sum = 0
#
# for i in range(10000):
#     chosen = random.choices([0, 1], weights=[0.3, 0.7])
#     sum += chosen[0]
#
# print(sum)

# lst = [1, 2, 3, 4, 5]

# secondList = lst[:3]

# for x in secondList: lst.remove(x)

balancers_amount = 8
probs_amnt = 14
part = 1 / (balancers_amount - 1)
for i in range(1, balancers_amount):
    print([int((i - 1) * probs_amnt * part), int(i * probs_amnt * part)])

# print(secondList)
# print(lst)


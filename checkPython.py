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

lst = [1, 2, 3, 4, 5]

secondList = lst[:3]

for x in secondList: lst.remove(x)

print(secondList)
print(lst)


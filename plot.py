import matplotlib.pyplot as plt

data = [2, 4, 3, 9, 5, 6, 6, 8 ,4]

plt.boxplot(data, vert=True)

plt.ylim(1,10)


plt.show()
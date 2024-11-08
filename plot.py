import matplotlib.pyplot as plt
import DTA400Project
import importlib

#data = [2, 4, 3, 9, 5, 6, 6, 8 ,4]
#plt.boxplot(data, vert=True)
#plt.ylim(1,10)

def set_bounds(variable):
    bound = 20
    if variable < (bound * -1):
        return bound  * -1
    elif variable > bound:
        return bound
    return variable

w_data = []
l_data = []
temp_w = []
temp_l = []
mini = 0
maxi = 2

for boxes in range(10): #x boxes
    for samples in range(50): #y samples
        # run the sim using this interval
        w, l = DTA400Project.simulation_data(mini, maxi)
        # process result
        w = round(w, 2)
        l = round(l, 2)
        w = set_bounds(w)
        l = set_bounds(l)
        # save result
        temp_w.append(w)
        temp_l.append(l)
        # needed or the sim does not restart
        importlib.reload(DTA400Project)
    # save sets of data for one box in the boxes lists
    w_data.append(temp_w)
    l_data.append(temp_l)
    # reset and move on to the next box interval
    temp_w =[]
    temp_l = []
    mini += 1
    maxi += 1
print(f"W list: {w_data}\n\nL list: {l_data}")

plt.boxplot(w_data, vert=True)
#plt.boxplot(l_data, vert=True)

plt.show()




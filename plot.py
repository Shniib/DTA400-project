import matplotlib.pyplot as plt
import DTA400Project
import importlib
import numpy

bound = 10
mini = 0
maxi = 2
box_nb = 8
w_data = []
l_data = []
temp_w = []
temp_l = []
for boxes in range(box_nb): #x boxes
    for samples in range(100): #y samples
        # run the sim using this interval
        w, l = DTA400Project.simulation_data(mini, maxi)
        # process result
        w = round(w, 2)
        l = round(l, 2)
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


plt.ylim((-bound),bound) #set bound to be able to see smaller boxes

#make labels, change values
x_labels = []
temp_min = 0
temp_max = 2
temp_x = 1
x = []
for interval in range(box_nb):
    temp_str = '['+str(temp_min)+','+str(temp_max)+']'
    x_labels.append(temp_str)
    x.append(temp_x)
    temp_x += 1
    temp_min += 1
    temp_max += 1

y_values = range(-bound, bound, 1)
plt.yticks(y_values)
plt.xlabel("Interval between customer arrival (min)")  # Titel för x-axeln

l_plot = False

if l_plot:
    plt.boxplot(l_data)
    plt.ylabel("Average queue length")  # Titel för y-axeln
    plt.title("Queue length and customer arrival threshold")
    plt.ylim((-bound * (2/3)),bound * (2/3))
else:
    plt.boxplot(w_data)
    plt.ylabel("Average wait time (min)")  # Titel för y-axeln
    plt.title("Wait time and customer arrival threshold")
plt.xticks(x, x_labels)
plt.grid(axis = 'y')
plt.show()




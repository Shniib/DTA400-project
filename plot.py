import matplotlib.pyplot as plt
import DTA400Project
import importlib
import numpy

utilization_data = False
box_nb = 8

def make_x_label():
    x_labels = []
    temp_min = 0
    temp_max = 2
    for interval in range(box_nb):
        temp_str = '['+str(temp_min)+','+str(temp_max)+']'
        x_labels.append(temp_str)
        temp_min += 1
        temp_max += 1
    return x_labels

if utilization_data:
    utilization_mean = []
    ranges = [[2,4], [1,3], [1,2], [0,2]] 
    for interval in ranges:  #x data points
        temp_u_list = []
        for samples in range(100): # y samples
            temp_u = DTA400Project.utilization_data(interval[0], interval[1])
            temp_u_list.append(temp_u)
            importlib.reload(DTA400Project)
        utilization_mean.append(sum(temp_u_list)/len(temp_u_list))
    plt.plot(utilization_mean)
    plt.grid()
    plt.xticks(range(0, len(ranges)), ranges)
    plt.yticks(numpy.arange(0.6, 2.1, 0.1))
    plt.ylabel("Utilization")
    plt.title("Cashier Utilization")

else:
    l_plot = False
    plot_boarder = 15

    min_customer_arrival_time = 0 #0 --> box_nb - 1
    max_customer_arrival_time = 2 #2 --> box_nb + 1
    w_data = []
    l_data = []
    temp_w = []
    temp_l = []
    for boxes in range(box_nb): #x boxes
        for samples in range(100): #y samples
            # run the sim using this interval
            w, l = DTA400Project.simulation_data(min_customer_arrival_time, max_customer_arrival_time)
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
        min_customer_arrival_time += 1
        max_customer_arrival_time += 1
    #print(f"W list: {w_data}\n\nL list: {l_data}")
    
    if l_plot:
        plt.boxplot(l_data)
        plt.ylabel("Average queue length")  # Titel för y-axeln
        plt.title("Customer arrival impact on queue length")
    else:
        plt.boxplot(w_data)
        plt.ylabel("Average wait time (min)")  # Titel för y-axeln
        plt.title("Customer arrival impact on wait time")
    x_labels= make_x_label()
    plt.xticks(range(1, box_nb + 1), x_labels)
    plt.grid(axis = 'y')
    plt.ylim(0,plot_boarder + 1) #set bound to be able to see smaller boxes
    plt.yticks(range(0, plot_boarder + 1, 1))
plt.xlabel("Interval between customer arrival (min)")  # Titel för x-axeln
plt.show()
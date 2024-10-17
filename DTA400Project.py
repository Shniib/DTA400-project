import simpy
import random

SIMULATION_TIME = 10
NUM_CASHIERS = 1
MAX_INITIAL_CUSTOMERS = 5
MIN_INITIAL_CUSTOMERS = 2
MAX_BAKED_GOODS = 10
MIN_BAKED_GOODS = 5
MAX_WANTED_GOODS = 3
MIN_WANTED_GOODS = 0
MAX_SERVICE_TIME = 3
MIN_SERVICE_TIME = 1


menu = [["Cinnamon bun", 0], ["Chocolatechip cookie", 0], ["Blueberry pie", 0]]
customers_in_queue = []
customers_index_who_wants_to_leave = []

#customers_in_total = 0
#customers_unserviceable = 0


class Bakery(object):
    def __init__(self, env):
        self.env = env
        self.cashier = simpy.Resource(env, NUM_CASHIERS)
        print(NUM_CASHIERS, "works at the front")
        # bake inventory
        for item in menu:
            item[1] = random.randint(MIN_BAKED_GOODS, MAX_BAKED_GOODS)
        print("Bakery baked", menu)
        self.daily_batch = menu # remove if we cannot make an "exit function" when the simulation ends

class customer(object):
    def __init__(self, env):
        self.env = env
        self.order = []

        num_pastries = 0
        for item in menu: #randomize order
            wanted_amount = random.randint(MIN_WANTED_GOODS, MAX_WANTED_GOODS)
            self.order.append([item[0], wanted_amount]) 
            num_pastries += wanted_amount
        if num_pastries < 1: #make sure the customer wants at least 1 thing
            print("Customer wanted NOTHING, forced them to pick something")
            self.order[random.randint(0,len(menu)-1)][1] = random.randint(1, MAX_WANTED_GOODS)

        customers_in_queue.append(self)

    
#def spawn_customer():

def update_menu():
    for i in range(len(menu)):
        menu[i][1] -= customers_in_queue[0].order[i][1]

def detect_unserviceable_customers():
    #if nothing the customer wants is in stock, leave
    for customer_index in range(len(customers_in_queue)):
        for pastry in range(len(menu)):
            if customers_in_queue[customer_index].order[pastry][1] > 0: # if we even want this pastry...
                if menu[pastry][1] > 0: #if the pastry is in stock, break and move on to the next customer check
                    break
            if pastry == len(menu) - 1: #if we are checking the last pastry and there is still nothing in the bakery the customer wants: prepare to leave
                print("Customer wants",customers_in_queue[customer_index].order, "\nbut bakery only has", menu, ". Customer leaves.\n")
                update_menu()
                customers_index_who_wants_to_leave.append(customer_index)

def remove_unserviceable_customers():
    last_index = len(customers_index_who_wants_to_leave) - 1 #start from the back so the index cannot end up too big
    for sad_customer in range(len(customers_index_who_wants_to_leave)):
        customers_in_queue.pop(customers_index_who_wants_to_leave[last_index])
        last_index -= 1
    customers_index_who_wants_to_leave.clear()

    
def main(env):
    bakery = Bakery(env)
    
    #customers arriving when bakery opens
    for i in range(random.randint(MIN_INITIAL_CUSTOMERS, MAX_INITIAL_CUSTOMERS)):
        newCustomer = customer(env)
    
    #debug: what the customers want (in order)
    for customer_index in range(len(customers_in_queue)):
        print("Customer", customer_index + 1, "wants", customers_in_queue[customer_index].order)
    print("\n")

    #simulate
    while len(customers_in_queue) > 0: #or when event is still going, in case there is temporarely no queue -------------------------------------------------------------
        yield env.timeout(random.randint(MIN_SERVICE_TIME, MAX_SERVICE_TIME)) #customer buys pastries
        
        print("There are", len(customers_in_queue), "customer left in the queue")
        #update menu
        print("Menu before purchase:", menu)
        update_menu()
        customers_in_queue.pop(0) #first customer in queue is done, leaving
        print("Menu after purchase:", menu, "\n")

        detect_unserviceable_customers()
        remove_unserviceable_customers()


env = simpy.Environment()
env.process(main(env)) #insert start function here
env.run(until=SIMULATION_TIME)  #end when either time over or every part of menu is <= 0
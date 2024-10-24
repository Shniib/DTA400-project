import simpy
import random

SIMULATION_TIME = 10
NUM_CASHIERS = 1
MAX_INITIAL_CUSTOMERS = 5
MIN_INITIAL_CUSTOMERS = 2
MAX_TIME_BETWEEN_CUSTOMERS = 3
MIN_TIME_BETWEEN_CUSTOMERS = 1
MAX_BAKED_GOODS = 10
MIN_BAKED_GOODS = 5
MAX_WANTED_GOODS = 3
MIN_WANTED_GOODS = 0
MAX_SERVICE_TIME = 3
MIN_SERVICE_TIME = 1
MAX_DECIDING_TIME = 3
MIN_DECIDING_TIME = 1
MIN_REGULAR_RATE = 1
MAX_REGULAR_RATE = 5

menu = [["Cinnamon bun", 0], ["Chocolatechip cookie", 0], ["Blueberry pie", 0]]

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

class customer(object): #never do timeout in __init__!
    def __init__(self, env, i):
        self.env = env
        self.order = []
        self.customer_number = i

        regular = random.randint(MIN_REGULAR_RATE, MAX_REGULAR_RATE)
        if(regular == MIN_REGULAR_RATE):
            print(f'    Regular customer {self.customer_number} arrived at {env.now}')
            create_customer_order(self)
        else:
            print(f'    Random customer {self.customer_number} arrived at {env.now}')

def create_customer_order(customer): 
    num_pastries = 0
    #randomize order
    for item in menu: 
            wanted_amount = random.randint(MIN_WANTED_GOODS, MAX_WANTED_GOODS)
            customer.order.append([item[0], wanted_amount]) 
            num_pastries += wanted_amount
    #make sure the customer wants at least 1 thing
    if num_pastries < 1: 
        customer.order[random.randint(0,len(menu)-1)][1] = random.randint(1, MAX_WANTED_GOODS)

def update_menu(c):
    for i in range(len(menu)):
        menu[i][1] -= c.order[i][1]

"""def detect_unserviceable_customers(): #change so it's a chance that people will change their order if bakery runs out of what they want
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
    customers_index_who_wants_to_leave.clear()"""

def customer_behavior(env, c, cashier):
    #decide what you want
    if len(c.order) == 0:
        deciding_time = random.randint(MIN_DECIDING_TIME, MAX_DECIDING_TIME)
        yield env.timeout(deciding_time)
        create_customer_order(c)
        print(f'    Customer {c.customer_number} took {deciding_time} time to decide they want {c.order} (done at time {env.now})')
        
    #pay
    with cashier.request() as request:
        yield request
        print(f'\n{env.now}: Hello, I would like to order...')
        service_time = random.randint(MIN_SERVICE_TIME, MAX_SERVICE_TIME)

        print(f'Service time for customer {c.customer_number}: {service_time}.')
        yield env.timeout(service_time) #customer buys pastries
        print(f'Menu before {env.now}: {menu}')
        print(f'Customer want {c.order}')
        update_menu(c)
        print(f'Menu after {env.now}: {menu}')

def create_customer(cashier, nb):
    newCustomer = customer(env, nb)
    env.process(customer_behavior(env, newCustomer,  cashier))
    return nb + 1

def main(env):
    bakery = Bakery(env)
    customer_nb = 1
    #customers arriving when bakery opens
    for i in range(random.randint(MIN_INITIAL_CUSTOMERS, MAX_INITIAL_CUSTOMERS)):
        customer_nb = create_customer(bakery.cashier, customer_nb)

    #simulation
    while True:
        customer_arrival_time = random.randint(MIN_TIME_BETWEEN_CUSTOMERS,MAX_TIME_BETWEEN_CUSTOMERS)
        yield env.timeout(customer_arrival_time)
        customer_nb = create_customer(bakery.cashier, customer_nb)

env = simpy.Environment()
env.process(main(env)) #start function
env.run(until=SIMULATION_TIME) 
import simpy
import random #Next: add customers to queue over sim time

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
    def __init__(self, env):
        self.env = env
        self.order = []
        self.ready_time = 0

        regular = random.randint(MIN_REGULAR_RATE, MAX_REGULAR_RATE)
        if(regular == MIN_REGULAR_RATE):
            print(f'    A regular arrived at time {env.now}')
            create_customer_order(self)
        else:
            print(f'    not a regular has arrived at time {env.now}')


def customer_decides_what_they_want(c, env):
    deciding_time = random.randint(MIN_DECIDING_TIME, MAX_DECIDING_TIME)
    print(f'    Deciding time: {deciding_time}')
    yield env.timeout(deciding_time) #why have time out if we need to stop it from acting in the bakery manually anyways?
    create_customer_order(c)
    print(f'    Customer decided they want {c.order} at time {env.now}')

def create_customer_order(customer): 
    num_pastries = 0
    for item in menu: #randomize order
            wanted_amount = random.randint(MIN_WANTED_GOODS, MAX_WANTED_GOODS)
            customer.order.append([item[0], wanted_amount]) 
            num_pastries += wanted_amount
    if num_pastries < 1: #make sure the customer wants at least 1 thing
        print(" Customer wanted NOTHING, forced them to pick something")
        customer.order[random.randint(0,len(menu)-1)][1] = random.randint(1, MAX_WANTED_GOODS)

def update_menu(c):
    for i in range(len(menu)):
        menu[i][1] -= c.order[i][1]

def detect_unserviceable_customers(): #change so it's a chance that people will change their order if bakery runs out of what they want
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

def serve_customer(c):
    service_time = random.randint(MIN_SERVICE_TIME, MAX_SERVICE_TIME)
    print(f'Service time: {service_time}. Menu at {env.now}: {menu}')
    yield env.timeout(service_time) #customer buys pastries
    update_menu(c)
    print(f'Menu at {env.now}: {menu}')

    #detect_unserviceable_customers()
    #remove_unserviceable_customers()


def customer_behavior(env, c, cashier):
    if len(c.order) == 0:
        #customer_decides_what_they_want(c, env)
        deciding_time = random.randint(MIN_DECIDING_TIME, MAX_DECIDING_TIME)
        print(f'    Deciding time: {deciding_time}')
        yield env.timeout(deciding_time) #why have time out if we need to stop it from acting in the bakery manually anyways?
        create_customer_order(c)
        print(f'    Customer decided they want {c.order} at time {env.now}')
        
    
    #serve_customer(c)
    with cashier.request() as request:
        yield request
        print(f'\n{env.now}: Hello, I would like to order...')
        service_time = random.randint(MIN_SERVICE_TIME, MAX_SERVICE_TIME)
        print(f'Menu: {menu} Service time for this customer: {service_time}')
        yield env.timeout(service_time) #customer buys pastries
        print(f'Customer leaves at {env.now}.\n')
    
    update_menu(c)
    print(f'Menu at {env.now}: {menu}')


def main(env):
    bakery = Bakery(env)
    
    #customers arriving when bakery opens
    for i in range(random.randint(MIN_INITIAL_CUSTOMERS, MAX_INITIAL_CUSTOMERS)):
        newCustomer = customer(env)
        env.process(customer_behavior(env, newCustomer,  bakery.cashier))

    #simulate
    while True:
        customer_arrival_time = random.randint(MIN_TIME_BETWEEN_CUSTOMERS,MAX_TIME_BETWEEN_CUSTOMERS)
        yield env.timeout(customer_arrival_time)
        newCustomer = customer(env)
        env.process(customer_behavior(env, newCustomer, bakery.cashier)) 

env = simpy.Environment()
env.process(main(env)) #insert start function here
env.run(until=SIMULATION_TIME) 
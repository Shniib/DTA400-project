import simpy
import random #Next: add customers to queue over sim time

SIMULATION_TIME = 5
NUM_CASHIERS = 1
MAX_INITIAL_CUSTOMERS = 5
MIN_INITIAL_CUSTOMERS = 2
MAX_BAKED_GOODS = 10
MIN_BAKED_GOODS = 5
MAX_WANTED_GOODS = 3
MIN_WANTED_GOODS = 0
MAX_SERVICE_TIME = 3
MIN_SERVICE_TIME = 1
MAX_DECIDING_TIME = 10
MIN_DECIDING_TIME = 6
MIN_REGULAR_RATE = 1
MAX_REGULAR_RATE = 5


menu = [["Cinnamon bun", 0], ["Chocolatechip cookie", 0], ["Blueberry pie", 0]]
customers_in_queue = []
customers_browsing = []
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

class customer(object): #never do timeout in __init__!
    def __init__(self, env):
        self.env = env
        self.order = []
        self.ready_time = 0

        regular = random.randint(MIN_REGULAR_RATE, MAX_REGULAR_RATE)
        if(regular == MIN_REGULAR_RATE):
            print("A regular arrived")
            create_customer_order(self)
            customers_in_queue.append(self)
        else:
            print("not a regular has arrived")
            customers_browsing.append(self)


def customer_decides_what_they_want(customer): #customers might get called here multiple times???
    #decision_making_time = 
    #self.ready_time = env.now
    #yield customer.env.timeout(random.randint(MIN_DECIDING_TIME, MAX_DECIDING_TIME)) #why have time out if we need to stop it from acting in the bakery manually anyways?
    create_customer_order(customer)
    #self.ready_time = self.ready_time + decision_making_time
    #print(f'Customers self.ready_time is {self.ready_time}')
    for customer_index in range(len(customers_browsing)): 
        if customers_browsing[customer_index] is customer:
            print("I left the thinking queue")
            customers_browsing.pop(customer_index)
            break
    customers_in_queue.append(customer)
    print(f'Customer decided they want {customer.order} at time {env.now}')


def create_customer_order(customer): 
    num_pastries = 0
    for item in menu: #randomize order
            wanted_amount = random.randint(MIN_WANTED_GOODS, MAX_WANTED_GOODS)
            customer.order.append([item[0], wanted_amount]) 
            num_pastries += wanted_amount
    if num_pastries < 1: #make sure the customer wants at least 1 thing
        print("Customer wanted NOTHING, forced them to pick something")
        customer.order[random.randint(0,len(menu)-1)][1] = random.randint(1, MAX_WANTED_GOODS)
    
    #debug
    #for c_index in len(customers_in_queue):
        #if customers_in_queue[c_index] == customer:
            #print("Customer", c_index + 1, "wanted", customer.order, "at", env.now)
    print("Customer wanted", customer.order, "at", env.now)
    
#def spawn_customer():

def update_menu():
    for i in range(len(menu)):
        menu[i][1] -= customers_in_queue[0].order[i][1]

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

def serve_customer():
    print(f'Menu at {env.now}: {menu}')
    yield env.timeout(random.randint(MIN_SERVICE_TIME, MAX_SERVICE_TIME)) #customer buys pastries
    print("There are", len(customers_in_queue), "customer left in the queue")
    #update menu
    
    update_menu()
    customers_in_queue.pop(0) #first customer in queue is done, leaving
    print(f'Menu at {env.now}: {menu}')


    #detect_unserviceable_customers()
    #remove_unserviceable_customers()


    
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
    while True: #while simulation is running...
        #for c in customers_in_queue: #let customers decide when they enter, should not effect other customers before them ready to order
            #if(c.order == []):
                #yield c.env.timeout(random.randint(MIN_DECIDING_TIME, MAX_DECIDING_TIME))
                #create_customer_order(c)
        if len(customers_browsing) > 0:
            for cus in customers_browsing:
                customer_decides_what_they_want(cus)

        if len(customers_in_queue) > 0:
            with bakery.cashier.request() as request:
                yield request

                print(env.now, ": Hello, I'd like to order...")
                yield env.process(serve_customer())
                print(f'Customer leaves at {env.now:.2f}.')

env = simpy.Environment()
env.process(main(env)) #insert start function here
env.run(until=SIMULATION_TIME)  #end when either time over or every part of menu is <= 0
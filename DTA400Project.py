import simpy
import random

SIMULATION_TIME = 60 #1 unit = 1 minute. Only set times dividable by 60
NUM_CASHIERS = 1
MAX_INITIAL_CUSTOMERS = 3
MIN_INITIAL_CUSTOMERS = 1
MAX_TIME_BETWEEN_CUSTOMERS = 3
MIN_TIME_BETWEEN_CUSTOMERS = 1
MAX_BAKED_GOODS = SIMULATION_TIME * 0.8
MIN_BAKED_GOODS = SIMULATION_TIME * 0.5
MAX_WANTED_GOODS = 3
MIN_WANTED_GOODS = 0
MAX_SERVICE_TIME = 3
MIN_SERVICE_TIME = 1
MAX_DECIDING_TIME = 3
MIN_DECIDING_TIME = 1
MIN_REGULAR_RATE = 1
MAX_REGULAR_RATE = 5

customers_in_queue = []

#Metrics
menu = [["Cinnamon bun", 0], ["Chocolatechip cookie", 0], ["Blueberry pie", 0]]
data = [["Customers in total", 0], ["Customers served", 0], ["Customer unserviceable", 0]]
arrival_rates_to_bakery = [] 
arrival_rates_to_queue = [] 
service_rates = []
queue_length = []
arriving_times_between_customers = [] 


class Bakery(object):
    def __init__(self, env):
        self.env = env
        self.cashier = simpy.Resource(env, NUM_CASHIERS)
        print(NUM_CASHIERS, "works at the front")
        # bake inventory
        for item in menu:
            item[1] = random.randint(MIN_BAKED_GOODS, MAX_BAKED_GOODS)
        print("Bakery baked", menu)
        self.daily_batch = [["Cinnamon bun", 0], ["Chocolatechip cookie", 0], ["Blueberry pie", 0]]
        for pastry in range(len(menu)):
            self.daily_batch[pastry][1] = menu[pastry][1]

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
        data[0][1] = data[0][1] + 1 #add to total customers

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
    customers_in_queue.append(customer)

def update_menu(c):
    for i in range(len(menu)):
        menu[i][1] -= c.order[i][1]

def customer_behavior(env, c, cashier):
    #decide what you want
    if len(c.order) == 0:
        deciding_time = random.randint(MIN_DECIDING_TIME, MAX_DECIDING_TIME)
        yield env.timeout(deciding_time)
        create_customer_order(c)
        print(f'    Customer {c.customer_number} took {deciding_time} time to decide they want {c.order} (done at time {env.now})')
        arrival_rates_to_queue.append(deciding_time)
    else:
        arrival_rates_to_queue.append(0) #regulars go directly to queue
    
    #pay
    with cashier.request() as request:
        yield request
        print(f'\n{env.now}: Hello, I would like to order...')
        service_time = random.randint(MIN_SERVICE_TIME, MAX_SERVICE_TIME)

        print(f'Service time for customer {c.customer_number}: {service_time}.')
        yield env.timeout(service_time) #customer buys pastries
        service_rates.append(service_time)
        print(f'Menu before {env.now}: {menu}')
        print(f'Customer {c.customer_number} want {c.order}')
        update_menu(c)
        print(f'Menu after {env.now}: {menu}')
        #remove myself from queue
        for customer_index in range(len(customers_in_queue)):
            if customers_in_queue[customer_index] == c:
                customers_in_queue.pop(customer_index)
                break
        
        # if customer could buy something they wanted: add +1 to customers served
        for pastry_index in range(len(menu)):
            if c.order[pastry_index][1] > 0: #if I wanted this pastry
                if menu[pastry_index][1] > 0: #if it is available, add me to customers served
                    data[1][1] = data[1][1] + 1
                    break
            if pastry_index == len(menu) - 1: #if I am unserviceable, add it to data
                data[2][1] = data[2][1] + 1
        

def create_customer(cashier, nb):
    newCustomer = customer(env, nb)
    env.process(customer_behavior(env, newCustomer,  cashier))
    return (nb + 1)

def main(env):
    bakery = Bakery(env)
    customer_nb = 1
    env.process(exit_function(bakery))
    env.process(gather_data())
    #customers arriving when bakery opens
    for i in range(random.randint(MIN_INITIAL_CUSTOMERS, MAX_INITIAL_CUSTOMERS)):
        customer_nb = create_customer(bakery.cashier, customer_nb)
        arrival_rates_to_bakery.append(0)

    #simulation
    while True:
        customer_arrival_time = random.randint(MIN_TIME_BETWEEN_CUSTOMERS,MAX_TIME_BETWEEN_CUSTOMERS)
        yield env.timeout(customer_arrival_time)
        arrival_rates_to_bakery.append(customer_arrival_time)
        customer_nb = create_customer(bakery.cashier, customer_nb)
        
def gather_data():
    while True:
        #print(env.now)
        queue_length.append(len(customers_in_queue))#faktiska längen på kön
        yield env.timeout(1)

def count_sum(list):
    time_sum = 0 # make func
    for time in list:
        time_sum = time_sum + time
    return time_sum

def exit_function(b):
    yield env.timeout(SIMULATION_TIME - 0.00001) #has to be under simulation time or it will not trigger

    total_customers = data[0][1]
    customers_served = data[1][1]
    customers_unserviceable = data[2][1]

    #arrival_time_to_bakery_sum = count_sum(arrival_rates_to_bakery) #ska vara när de kommer in i kön, inte bageriet. System = kö och service
    arrival_time_to_queue_sum = count_sum(arrival_rates_to_queue)
    service_time_sum = count_sum(service_rates)

    #Arrival rate
    #arrival_rate_to_bakery_per_min = 1 / (arrival_time_to_bakery_sum / total_customers)
    #arrival_rate_to_bakery_per_hour = arrival_rate_to_bakery_per_min * 60
    #Service rate
    service_rate_per_min = 1 / (service_time_sum / (customers_served + customers_unserviceable))
    service_rate_per_hour = service_rate_per_min * 60

    arrival_rate_to_queue_per_min = 1 / (arrival_time_to_queue_sum / len(arrival_rates_to_queue))
    arrival_rate_to_queue_per_hour = arrival_rate_to_queue_per_min * 60

    #arrival rate > service rate --> utilization > 1.      arrival rate < service rate --> utilization < 1
    utilization = arrival_rate_to_queue_per_hour / service_rate_per_hour
    # PROBLEM: utilization kan inte alltid vara över 1 då den ibland står och väntar. 

    cashier_idle_time = SIMULATION_TIME - service_time_sum
    cashier_idle_time_per_hour = cashier_idle_time / (SIMULATION_TIME / 60)

    average_wait_time_min = arrival_rate_to_queue_per_min / (service_rate_per_min * (service_rate_per_min - arrival_rate_to_queue_per_min))
    average_queue_length_min = (arrival_rate_to_queue_per_min * arrival_rate_to_queue_per_min) / (service_rate_per_min * (service_rate_per_min - arrival_rate_to_queue_per_min))

    #average_queue_length_hour = (arrival_rate_to_bakery_per_hour * arrival_rate_to_bakery_per_hour) / (service_rate_per_hour * (service_rate_per_hour - arrival_rate_to_bakery_per_hour))

    print("\nThe bakery closed for today")
    print(f'Customers in total: {total_customers}')
    print(f'Customers served: {customers_served}')
    print(f'Customer unserviceable: {customers_unserviceable}')
    print(f'Menu at the beginning of the day:   {b.daily_batch}')
    print(f'Menu at the end of the day:         {menu}')

    #print(f'\nArrival rate to bakery (Average customers per hour): {arrival_rate_to_bakery_per_hour:.0f} ') # ~0-2 kunder för mycket
    print(f'Arrival rate to queue (Average customers per min): {arrival_rate_to_queue_per_min:.2f}')
    print(f'Arrival rate to queue (Average customers per hour): {arrival_rate_to_queue_per_hour:.2f}')
    print(f'Service rate (Average customers per hour): {service_rate_per_hour:.0f} ') # ~0-6 kunder för mycket. För att service rate och arrival rate har samma cooldown (1-3) har de liknande rates 
    print(f'Service rate (Average customers per min): {service_rate_per_min:.2f}') # och ibland "slösas tid" då folk inte är redo att beställa
    print(f'Utilization = {utilization:.2f}')

    print(f'\nAverage wait time (W) in minutes: {average_wait_time_min:.2f}')
    print(f'Average queue length (L): {average_queue_length_min:.2f}')
    print(f'Total cashier idle time: {cashier_idle_time} min')
    print(f'Cashier idle time per hour: {cashier_idle_time_per_hour} min')

    print(f'\narrival_rate between customers entering the bakery: {arrival_rates_to_bakery} (Length: {len(arrival_rates_to_bakery)})')
    print(f'\narrival_rate between customers entering the queue: {arrival_rates_to_queue} (Length: {len(arrival_rates_to_queue)})')
    print(f'service_rates: {service_rates} (Length: {len(service_rates)})\n')


env = simpy.Environment()
env.process(main(env)) #start function
env.run(until=SIMULATION_TIME) 
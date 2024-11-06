import simpy
import random
import statistics  # remove if median is not being used

SIMULATION_TIME = 60  # 1 unit = 1 minute.
NUM_CASHIERS = 1
MAX_INITIAL_CUSTOMERS = 3
MIN_INITIAL_CUSTOMERS = 1
MAX_BAKED_GOODS = int(SIMULATION_TIME * 0.8)
MIN_BAKED_GOODS = int(SIMULATION_TIME * 0.5)
MAX_WANTED_GOODS = 3
MIN_WANTED_GOODS = 0
MAX_TIME_BETWEEN_CUSTOMERS = 4
MIN_TIME_BETWEEN_CUSTOMERS = 3
MAX_SERVICE_TIME = 3
MIN_SERVICE_TIME = 1
MAX_DECIDING_TIME = 2
MIN_DECIDING_TIME = 1
MIN_REGULAR_RATE = 1
MAX_REGULAR_RATE = 5

# Saving data
menu = [["Cinnamon bun", 0], ["Chocolatechip cookie", 0], ["Blueberry pie", 0]]
data = [
    ["Customers in total", 0],
    ["Customers served", 0],
    ["Customer unserviceable", 0],
]
arrival_times_to_queue = []  # env.now. Calculate time_between_last_customer_and_this_one in exit function, sum them up and get mean.
service_rates = []
arriving_times_between_customers = []


class Bakery:
    def __init__(self, env):
        self.env = env
        self.cashier = simpy.Resource(env, NUM_CASHIERS)
        print(NUM_CASHIERS, "works at the front")
        # bake inventory
        for item in menu:
            item[1] = random.randint(MIN_BAKED_GOODS, MAX_BAKED_GOODS)
        print("Bakery baked", menu)
        self.daily_batch = [
            ["Cinnamon bun", 0],
            ["Chocolatechip cookie", 0],
            ["Blueberry pie", 0],
        ]
        for pastry in range(len(menu)):
            self.daily_batch[pastry][1] = menu[pastry][1]


class Customer:  # never do timeout in __init__!
    def __init__(self, env, i):
        self.env = env
        self.order = []
        self.customer_number = i

        regular = random.randint(MIN_REGULAR_RATE, MAX_REGULAR_RATE)
        if regular == MIN_REGULAR_RATE:
            print(f"    Regular customer {self.customer_number} arrived at {env.now}")
            create_customer_order(self)
        else:
            print(f"    Random customer {self.customer_number} arrived at {env.now}")
        data[0][1] = data[0][1] + 1  # add to total customers


def create_customer_order(customer):
    num_pastries = 0
    # randomize order
    for item in menu:
        wanted_amount = random.randint(MIN_WANTED_GOODS, MAX_WANTED_GOODS)
        customer.order.append([item[0], wanted_amount])
        num_pastries += wanted_amount
    # make sure the customer wants at least 1 thing
    if num_pastries < 1:
        customer.order[random.randint(0, len(menu) - 1)][1] = random.randint(
            1, MAX_WANTED_GOODS
        )


def update_menu(c):
    for i in range(len(menu)):
        menu[i][1] -= c.order[i][1]


def customer_behavior(env, c, cashier):
    # decide what you want
    if len(c.order) == 0:
        deciding_time = random.randint(MIN_DECIDING_TIME, MAX_DECIDING_TIME)
        yield env.timeout(deciding_time)
        create_customer_order(c)
        print(
            f"    Customer {c.customer_number} took {deciding_time} time to decide they want {c.order} (done at time {env.now})"
        )

    arrival_times_to_queue.append(env.now)

    # pay
    with cashier.request() as request:
        yield request
        print(f"\n{env.now}: Hello, I would like to order...")
        service_time = random.randint(MIN_SERVICE_TIME, MAX_SERVICE_TIME)

        print(f"Service time for customer {c.customer_number}: {service_time}.")
        yield env.timeout(service_time)  # customer buys pastries
        service_rates.append(service_time)
        print(f"Menu before {env.now}: {menu}")
        print(f"Customer {c.customer_number} want {c.order}")
        update_menu(c)
        print(f"Menu after {env.now}: {menu}")

        # if customer could buy something they wanted: add +1 to customers served
        for pastry_index in range(len(menu)):
            if c.order[pastry_index][1] > 0:  # if I wanted this pastry
                if (
                    menu[pastry_index][1] > 0
                ):  # if it is available, add me to customers served
                    data[1][1] = data[1][1] + 1
                    break
            if pastry_index == len(menu) - 1:  # if I am unserviceable, add it to data
                data[2][1] = data[2][1] + 1


def create_customer(cashier, nb):
    newCustomer = Customer(env, nb)
    env.process(customer_behavior(env, newCustomer, cashier))
    return nb + 1


def main(env):
    bakery = Bakery(env)
    customer_nb = 1
    env.process(exit_function(bakery))
    # customers arriving when bakery opens
    for i in range(random.randint(MIN_INITIAL_CUSTOMERS, MAX_INITIAL_CUSTOMERS)):
        customer_nb = create_customer(bakery.cashier, customer_nb)
        # arrival_rates_to_bakery.append(0)

    # simulation
    while True:
        customer_arrival_time = random.randint(
            MIN_TIME_BETWEEN_CUSTOMERS, MAX_TIME_BETWEEN_CUSTOMERS
        )
        yield env.timeout(customer_arrival_time)
        customer_nb = create_customer(bakery.cashier, customer_nb)


def count_sum(list):
    time_sum = 0  # make func
    for time in list:
        time_sum = time_sum + time
    return time_sum


def time_to_interval_calculation(time_list):
    interval_list = []
    sum = 0
    for time_index in range(len(time_list)):
        if (
            time_index < len(time_list) - 1
        ):  # as long as we are not on the last time index
            if time_index == 0:
                interval = time_list[time_index]  # append the first time
                interval_list.append(interval)
                sum = interval
            interval = time_list[time_index + 1] - time_list[time_index]
            sum = sum + interval
            interval_list.append(interval)
    return sum, interval_list


def exit_function(b):
    yield env.timeout(
        SIMULATION_TIME - 0.00001
    )  # has to be under simulation time or it will not trigger

    total_customers = data[0][1]
    customers_served = data[1][1]
    customers_unserviceable = data[2][1]

    arrival_interval_to_queue_sum, interval_times = time_to_interval_calculation(
        arrival_times_to_queue
    )
    service_time_sum = count_sum(service_rates)
    print(
        f"\narrival_interval_to_queue_sum: {arrival_interval_to_queue_sum}, arrival_interval_to_queue_sum/len: {arrival_interval_to_queue_sum/len(arrival_times_to_queue):.2f}"
    )
    print(f"statistics.median(interval_times) = {statistics.median(interval_times)}")

    cashier_idle_time = SIMULATION_TIME - service_time_sum
    cashier_idle_time_per_hour = cashier_idle_time / (SIMULATION_TIME / 60)

    service_rate_per_min = 1 / (service_time_sum / len(service_rates))
    service_rate_per_hour = service_rate_per_min * 60

    arrival_rate_to_queue_per_min = 1 / (
        arrival_interval_to_queue_sum / len(arrival_times_to_queue)
    )
    arrival_rate_to_queue_per_hour = arrival_rate_to_queue_per_min * 60

    # arrival rate > service rate --> utilization > 1.      arrival rate < service rate --> utilization < 1
    utilization = arrival_rate_to_queue_per_hour / service_rate_per_hour

    # from pp. Does however freak out if the service time interval is too similar to the arrival time interval for customers, or if the utilization >= 1
    average_wait_time_min = arrival_rate_to_queue_per_min / (
        service_rate_per_min * (service_rate_per_min - arrival_rate_to_queue_per_min)
    )
    average_queue_length_min = (
        arrival_rate_to_queue_per_min * arrival_rate_to_queue_per_min
    ) / (service_rate_per_min * (service_rate_per_min - arrival_rate_to_queue_per_min))

    print("\nThe bakery closed for today")
    print(f"Customers in total: {total_customers}")
    print(f"Customers served: {customers_served}")
    print(f"Customer unserviceable: {customers_unserviceable}")
    print(f"Menu at the beginning of the day:   {b.daily_batch}")
    print(f"Menu at the end of the day:         {menu}")

    print(
        f"Arrival rate to queue (Average customers per hour): {arrival_rate_to_queue_per_hour:.2f}"
    )
    print(
        f"Arrival rate to queue (Average customers per min): {arrival_rate_to_queue_per_min:.2f}"
    )
    print(
        f"Service rate (Average customers per hour): {service_rate_per_hour:.0f} "
    )  # ~0-6 kunder för mycket. För att service rate och arrival rate har samma cooldown (1-3) har de liknande rates
    print(
        f"Service rate (Average customers per min): {service_rate_per_min:.2f}"
    )  # och ibland "slösas tid" då folk inte är redo att beställa
    print(f"Utilization = {utilization:.2f}")

    print(f"\nAverage wait time (W) in minutes: {average_wait_time_min:.2f}")
    print(f"Average queue length (L): {average_queue_length_min:.2f}")
    print(f"Total cashier idle time: {cashier_idle_time} min")
    print(f"Cashier idle time per hour: {cashier_idle_time_per_hour} min")

    print(
        f"arrival_time where customers enter the queue:         {arrival_times_to_queue} (Length: {len(arrival_times_to_queue)})"
    )
    print(
        f"intervals between customers entering the queue:       {interval_times} (Length: {len(interval_times)})"
    )
    print(
        f"service_times:                                        {service_rates} (Length: {len(service_rates)})\n"
    )

    print(
        f"(service_rate_per_hour - arrival_rate_to_queue_per_hour) is {(service_rate_per_hour - arrival_rate_to_queue_per_hour)}"
    )
    print(
        f"(service_rate_per_min - arrival_rate_to_queue_per_min) is {(service_rate_per_min - arrival_rate_to_queue_per_min)}"
    )


env = simpy.Environment()
env.process(main(env))  # start function
env.run(until=SIMULATION_TIME)

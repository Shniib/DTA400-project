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

# Log levels
DEBUG = 2
TRACE = 1
INFO = 0


class Log:
    def __init__(self, level: int):
        self.level = level

    def log(self, level: int, *args, **kwargs):
        if level <= self.level:
            print(*args, **kwargs)


logger = Log(INFO)

# Saving data
menu: list[tuple[str, int]] = [
    ("Cinnamon bun", 0),
    ("Chocolatechip cookie", 0),
    ("Blueberry pie", 0),
]

total_customers = 0
customers_served = 0
customers_unserviceable = 0

arrival_times_to_queue: list[
    float
] = []  # env.now. Calculate time_between_last_customer_and_this_one in exit function, sum them up and get mean.
service_rates: list[int] = []
arriving_times_between_customers = []


class Bakery:
    def __init__(self, env: simpy.Environment):
        self.env = env
        self.cashier = simpy.Resource(env, NUM_CASHIERS)
        logger.log(DEBUG, NUM_CASHIERS, "works at the front")
        # bake inventory
        for index, (name, quantity) in enumerate(menu):
            menu[index] = name, random.randint(MIN_BAKED_GOODS, MAX_BAKED_GOODS)
        logger.log(DEBUG, "Bakery baked", menu)
        self.daily_batch: list[tuple[str, int]] = []
        for pastry in range(len(menu)):
            name, quantity = menu[pastry]
            self.daily_batch.append((name, quantity))


class Customer:  # never do timeout in __init__!
    def __init__(self, env: simpy.Environment, i: int):
        self.env = env
        self.order: list[tuple[str, int]] = []
        self.customer_number = i

        regular = random.randint(MIN_REGULAR_RATE, MAX_REGULAR_RATE)
        if regular == MIN_REGULAR_RATE:
            logger.log(
                DEBUG,
                f"    Regular customer {self.customer_number} arrived at {env.now}",
            )
            self.create_order()
        else:
            logger.log(
                DEBUG,
                f"    Random customer {self.customer_number} arrived at {env.now}",
            )
        global total_customers
        total_customers += 1

    def create_order(self):
        num_pastries: int = 0
        # randomize order
        for item in menu:
            wanted_amount = random.randint(MIN_WANTED_GOODS, MAX_WANTED_GOODS)
            self.order.append((item[0], wanted_amount))
            num_pastries += wanted_amount
        # make sure the customer wants at least 1 thing
        if num_pastries < 1:
            index = random.randint(0, len(menu) - 1)
            name, quantity = self.order[index]
            self.order[index] = name, random.randint(1, MAX_WANTED_GOODS)

    def behavior(self, env: simpy.Environment, cashier: simpy.Resource):
        # decide what you want
        if len(self.order) == 0:
            deciding_time = random.randint(MIN_DECIDING_TIME, MAX_DECIDING_TIME)
            yield env.timeout(deciding_time)
            self.create_order()
            logger.log(
                DEBUG,
                f"    Customer {self.customer_number} took {deciding_time} time to decide they want {self.order} (done at time {env.now})",
            )

        arrival_times_to_queue.append(env.now)

        # pay
        with cashier.request() as request:
            yield request
            logger.log(DEBUG, f"\n{env.now}: Hello, I would like to order...")
            service_time = random.randint(MIN_SERVICE_TIME, MAX_SERVICE_TIME)

            logger.log(
                TRACE,
                f"Service time for customer {self.customer_number}: {service_time}.",
            )
            yield env.timeout(service_time)  # customer buys pastries
            service_rates.append(service_time)
            logger.log(DEBUG, f"Menu before {env.now}: {menu}")
            logger.log(DEBUG, f"Customer {self.customer_number} want {self.order}")
            update_menu(self)
            logger.log(DEBUG, f"Menu after {env.now}: {menu}")

            # if customer could buy something they wanted: add +1 to customers served
            for pastry_index in range(len(menu)):
                if self.order[pastry_index][1] > 0:  # if I wanted this pastry
                    if (
                        menu[pastry_index][1] > 0
                    ):  # if it is available, add me to customers served
                        global customers_served
                        customers_served += 1
                        break
                if (
                    pastry_index == len(menu) - 1
                ):  # if I am unserviceable, add it to data
                    global unserviceable_customers
                    unserviceable_customers += 1


def update_menu(customer: Customer):
    for i in range(len(menu)):
        name, quantity = menu[i]
        menu[i] = name, quantity - customer.order[i][1]


def create_customer(cashier: simpy.Resource, customer_number: int) -> int:
    newCustomer = Customer(env, customer_number)
    env.process(newCustomer.behavior(env, cashier))
    return customer_number + 1


def main(env):
    bakery = Bakery(env)
    customer_number: int = 1
    env.process(exit_function(bakery))
    # customers arriving when bakery opens
    for i in range(random.randint(MIN_INITIAL_CUSTOMERS, MAX_INITIAL_CUSTOMERS)):
        customer_number = create_customer(bakery.cashier, customer_number)
        # arrival_rates_to_bakery.append(0)

    # simulation
    while True:
        customer_arrival_time = random.randint(
            MIN_TIME_BETWEEN_CUSTOMERS, MAX_TIME_BETWEEN_CUSTOMERS
        )
        yield env.timeout(customer_arrival_time)
        customer_number = create_customer(bakery.cashier, customer_number)


def count_sum(time_list: list[int]):
    time_sum = 0  # make func
    for time in time_list:
        time_sum = time_sum + time
    return time_sum


def time_to_interval_calculation(time_list: list[float]):
    interval_list: list[float] = []
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


def exit_function(bakery: Bakery):
    yield env.timeout(
        SIMULATION_TIME - 0.00001
    )  # has to be under simulation time or it will not trigger

    arrival_interval_to_queue_sum, interval_times = time_to_interval_calculation(
        arrival_times_to_queue
    )
    service_time_sum = count_sum(service_rates)
    logger.log(
        INFO,
        f"\narrival_interval_to_queue_sum: {arrival_interval_to_queue_sum}, arrival_interval_to_queue_sum/len: {arrival_interval_to_queue_sum/len(arrival_times_to_queue):.2f}",
        f"statistics.median(interval_times) = {statistics.median(interval_times)}",
        sep="\n",
    )

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

    logger.log(
        INFO,
        "\nThe bakery closed for today",
        f"Customers in total: {total_customers}",
        f"Customers served: {customers_served}",
        f"Customer unserviceable: {customers_unserviceable}",
        f"Menu at the beginning of the day:   {bakery.daily_batch}",
        f"Menu at the end of the day:         {menu}",
        f"Arrival rate to queue (Average customers per hour): {arrival_rate_to_queue_per_hour:.2f}",
        f"Arrival rate to queue (Average customers per min): {arrival_rate_to_queue_per_min:.2f}",
        f"Service rate (Average customers per hour): {service_rate_per_hour:.0f} ",  # ~0-6 kunder för mycket. För att service rate och arrival rate har samma cooldown (1-3) har de liknande rates
        f"Service rate (Average customers per min): {service_rate_per_min:.2f}",  # och ibland "slösas tid" då folk inte är redo att beställa
        f"Utilization = {utilization:.2f}",
        f"\nAverage wait time (W) in minutes: {average_wait_time_min:.2f}",
        f"Average queue length (L): {average_queue_length_min:.2f}",
        f"Total cashier idle time: {cashier_idle_time} min",
        f"Cashier idle time per hour: {cashier_idle_time_per_hour} min",
        f"arrival_time where customers enter the queue:         {arrival_times_to_queue} (Length: {len(arrival_times_to_queue)})",
        f"intervals between customers entering the queue:       {interval_times} (Length: {len(interval_times)})",
        f"service_times:                                        {service_rates} (Length: {len(service_rates)})\n",
        f"(service_rate_per_hour - arrival_rate_to_queue_per_hour) is {(service_rate_per_hour - arrival_rate_to_queue_per_hour)}",
        f"(service_rate_per_min - arrival_rate_to_queue_per_min) is {(service_rate_per_min - arrival_rate_to_queue_per_min)}",
        sep="\n",
    )


env = simpy.Environment()
env.process(main(env))  # start function
env.run(until=SIMULATION_TIME)

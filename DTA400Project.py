import simpy
import random

menu = [["Cinnamonbun", 0], ["Chocolatechip cookie", 0], ["Blueberry pie", 0]]
customers_in_queue = []
#customers_gave_up = 0
#customers_served = 0

class Bakery(object):
    def __init__(self, env, num_cashiers):
        self.env = env
        self.cashier = simpy.Resource(env, num_cashiers)
        print(num_cashiers, "works at the front")
        # bake inventory
        for item in menu:
            item[1] = random.randint(5, 10) #bake between 5-10 of pastries
        print("Bakery baked", menu)

        
    def purchase_pastry(self, current_customer):
        yield self.env.timeout(random.randint(1,3)) #takes between 1-3 min from ordering to transaction complete with pastry in hand

class customer(object): #make a function??
    def __init__(self, env):
        self.env = env
        self.order = []
        for item in menu:
            self.order.append([item[0], random.randint(0,2)])
        customers_in_queue.append(self)

    
#def spawn_customer():
    
def main(env, num_cashiers):
    bakery = Bakery(env, num_cashiers)
    
    #customers arriving when bakery opens
    for i in range(random.randint(1,2)):
        newCustomer = customer(env)
    
    #debug: what the customers want (in order)
    for currentCustomer in customers_in_queue:
        print(currentCustomer.order)
        
    while len(customers_in_queue) > 0: #or when event is still going, in case there is no queue
        yield env.timeout(random.randint(1, 3)) #customer buys pastries
        
        #update menu
        for i in range(len(menu)):
            menu[i][1] -= customers_in_queue[0].order[i][1]
        customers_in_queue.pop(0)
        #customers_served += 1

        #customers in queue leave if everything they want is not available
        for customer_index in range(len(customers_in_queue)):
            for i in range(len(menu)):
                if customers_in_queue[customer_index].order[i][1] > menu[i][1]: #kicka ut customer om allt den vill ha inte finns (kan ändra sen)
                    print("Customer wants",customers_in_queue[customer_index].order[i], "but bakery only has", menu[i])
                    customers_in_queue.pop(customer_index)
                    #customers_gave_up += 1
                    break



env = simpy.Environment()
env.process(main(env, 1)) #insert start function here
env.run(until=10)  
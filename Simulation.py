import math
import random
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

import Plot_Data

class Order:
    def __init__(self, id, og_origin, origin, arr_time, cashier_service_time, barista_service_time):
        self.id = id
        self.og_origin = og_origin
        self.origin = origin # Where the order originates from (in-store, drive through, or online)
        self.arr_time = arr_time # Time at which the job arrived into the system
        self.cashier_service_time = cashier_service_time # Time it takes for the cashier to service the job
        self.barista_service_time = barista_service_time # Time it takes for the barista to service the job

        self.dep_customer_queue_time = None # Time at which the customer exits the queue and begins to be serviced by a cashier
        self.dep_cashier_time = None # Time at which the customer finishes being serviced by the cashier and their order enters the queue
        self.dep_order_queue_time = None # Time at which the order departs the queue and is assigned to a barista
        self.dep_system_time = None # Time at which job departs from the system
        self.response_time = None # Time between when the job enters the system and when it leaves the system
    
    def print_all(self):
        print("id:", self.id)
        print("origin:", self.origin)
        print()

        print("self.arr_time:", self.arr_time)
        print("self.dep_customer_queue_time:", self.dep_customer_queue_time)
        print("self.dep_cashier_time:", self.dep_cashier_time)
        print("self.cashier_service_time:", self.cashier_service_time)
        print()

        print("self.dep_order_queue_time:", self.dep_order_queue_time)
        print("self.dep_system_time:", self.dep_system_time)
        print("self.barista_service_time:", self.barista_service_time)
        print()

        print("self.response_time:", self.response_time)

    def set_dep_system_time(self, dep_time):
        self.dep_system_time = dep_time
        self.response_time = dep_time - self.arr_time
    
    def set_dep_customer_queue_time(self, dep):
        self.dep_customer_queue_time = dep

    def set_dep_cashier_time(self, dep):
        self.dep_cashier_time = dep
    
    def set_dep_order_queue_time(self, dep):
        self.dep_order_queue_time = dep

    def get_id(self):
        return self.id
    
    def get_origin(self):
        return self.origin

    def get_cashier_service_time(self):
        return self.cashier_service_time
    
    def get_barista_service_time(self):
        return self.barista_service_time
    
    def get_arr_time(self):
        return self.arr_time

    def get_dep_customer_queue_time(self):
        return self.dep_customer_queue_time
    
    def get_dep_cashier_time(self):
        return self.dep_cashier_time
    
    def get_dep_order_queue_time(self):
        return self.dep_order_queue_time
    
    def get_dep_system_time(self):
        return self.dep_system_time

    def get_response_time(self):
        return self.response_time
    
    def get_id(self):
        return self.id
    
    def get_og_origin(self):
        return self.og_origin

class Customer_Queue:
    def __init__(self):
        self.customers = list()
        self.cashiers = list()
        self.num_switched = 0
    
    def add_cashier(self, cashier):
        self.cashiers.append(cashier)

    def isEmpty(self):
        return self.customers == []
    
    def print_q(self):
        if self.customers:
            for j in self.customers:
                print("job:", j.get_cashier_service_time())
    
    def enqueue(self, customer):
        # If the queue is empty, check if there are any idle cashiers; if there are, assign the newly arrived job to the first idle cashier
        if self.isEmpty():
            for cashier in self.cashiers:
                if cashier.isIdle():
                    cashier.add(customer)
                    return
        
        # If the queue is not empty or if there are no idle cashiers, add the newly arrived job to the queue 
        self.customers.append(customer)
  
    def dequeue(self):
        if not self.isEmpty():
            return self.customers.pop(0)

    def get_customers(self):
        return self.customers
    
    def peek(self):
        return self.customers[0]
    
    def size(self):
        return len(self.customers)

    def inc_switched(self):
        self.num_switched += 1
        
    def get_switched(self):
        return self.num_switched

class Cashier:
    def __init__(self, id, customer_queue, order_queue):
        self.id = id
        self.current_job = None  # The current job in service
        self.next_dep_time = float('inf')  # Time at which the next job is departing from the Cashier
        self.customer_queue = customer_queue  # The customer queue that the cashier is receiving jobs from
        self.order_queue = order_queue # The order queue that the cashier is sending jobs to
        self.is_idle = True # Whether or not the cashier is idle
    
    # Assigns new_job to the cashier; only called by a Customer_Queue when it is empty
    def add(self, new_job):
        self.current_job = new_job

        # new_job saw an empty customer queue, so its departure time from the customer queue is the same as its arrival time into the system
        new_job.set_dep_customer_queue_time(new_job.get_arr_time())
        self.next_dep_time = self.current_job.get_dep_customer_queue_time() + self.current_job.get_cashier_service_time()
        self.is_idle = False

    # Sends a completed job to a Order_Queue and pulls a new one from a Customer_Queue; only called by the System
    def remove(self):
        self.current_job.set_dep_cashier_time(self.next_dep_time)
        self.order_queue.enqueue(self.current_job)

        if self.customer_queue.isEmpty():
            self.current_job = None
            self.next_dep_time = float('inf')
            self.is_idle = True
        # If there are more customers in the queue, set the first job in the queue into service
        # then, calculate the departure time of the newly serviced job by adding the current time and the size of the new job
        else:
            self.current_job = self.customer_queue.dequeue()
            self.current_job.set_dep_customer_queue_time(self.next_dep_time)
            self.next_dep_time += self.current_job.get_cashier_service_time()
    
    def get_next_dep_time(self):
        return self.next_dep_time
    
    def isIdle(self):
        return self.is_idle

class Order_Queue:
    def __init__(self, policy, dispatcher):
        self.policy = policy
        self.orders = list()
        self.dispatcher = dispatcher

    def isEmpty(self):
        return self.orders == []
    
    def print_q(self):
        if self.orders:
            for j in self.orders:
                print("job:", j.get_barista_service_time())
    
    def enqueue(self, order):
        # If the queue is empty, tell the dipatcher, who will return True if the order was assigned to a (idle) barista and False if not;
        # note that the dispatcher may not neccisarily assign the order even if there are idle baristas 
        if self.isEmpty():
            if self.dispatcher.arrival(order):
                return
        
        # If the dispatcher didn't assign the order to a barista, add it to the queue and reorder the queue based on the policy
        self.orders.append(order)
        self.reorder()
  
    def dequeue(self):
        if not self.isEmpty():
            return self.orders.pop(0)

    # Reorders the queue based on the policy such that the order at index 0 is the next order to depart
    def reorder(self):
        if self.policy == "FCFS":
            pass

    def peek(self):
        return self.orders[0]
    
    def size(self):
        return len(self.orders)

    def set_dispatcher(self, dispatcher):
        self.dispatcher = dispatcher
    
    def get_queue_length(self):
        return len(self.orders)

# The connection point between the Order_Queues and the Baristas
class Dispatcher:
    def __init__(self, policy):
        self.policy = policy
        self.order_queues = None
        self.baristas = []
    
    # Called by Order_Queue when a job arrives into an empty queue.
    # Under the current implementation, the dispatcher will always assign the job to the first idle barista it finds
    def arrival(self, order):
        for barista in self.baristas:
            if barista.isIdle():
                # The order left the queue as soon as it entered, so its departure time from the queue is the same as its departure time from the cashier
                order.set_dep_order_queue_time(order.get_dep_cashier_time())
                barista.add(order)
                return True
        
        return False
        
    # Called by Barista when a job departs from the barista
    # Fetches a job from an order queue based on the policy and assigns it to the barista that made the function call
    def departure(self):
        # Under "Longest First", the dispatcher will fetch a job from the queue with the most jobs in it; all jobs are equal in priority
        if self.policy == "Longest First":
            longest_queue = self.order_queues[0]
            for queue in self.order_queues:
                if queue.get_queue_length() > longest_queue.get_queue_length():
                    longest_queue = queue
            
            if longest_queue.get_queue_length() > 0:  
                order = longest_queue.dequeue()
                return order
            else:
                return None
            
    def set_order_queues(self, order_queues):
        self.order_queues = order_queues
    
    def set_bariastas(self, baristas):
        self.baristas = baristas

class Barista:
    def __init__(self, id, dispatcher):
        self.id = id
        self.current_job = None  # The current job in service
        self.next_dep_time = float('inf')  # Time at which the next job is departing from the barista
        self.dispatcher = dispatcher
        self.is_idle = True # Whether or not the barista is idle
    
    # Assigns new_job to the barista; only called by the dispatcher when an order arrives into an empty queue
    def add(self, new_job):
        self.current_job = new_job
        self.next_dep_time = self.current_job.get_dep_order_queue_time() + self.current_job.get_barista_service_time()
        self.is_idle = False

    # The departed job is sent back to the system for post processing; only called by the System
    def remove(self):
        to_return = self.current_job
        self.current_job.set_dep_system_time(self.next_dep_time)

        # Asks the dispatcher to fetch a new job from an order queue
        order = self.dispatcher.departure()

        # If there are no more customers in the queues
        if order is None:
            self.current_job = None
            self.next_dep_time = float('inf')
            self.is_idle = True
        else:
            self.current_job = order
            order.set_dep_order_queue_time(self.next_dep_time)
            self.next_dep_time += order.get_barista_service_time()
        
        return to_return
    
    def get_next_dep_time(self):
        return self.next_dep_time
    
    def isIdle(self):
        return self.is_idle

class SystemInstance:
    # n: num of arrivals
    # queue_1_cashier_num: cashier serving in-person customer queue
    # queue_2_cashier_num: num cashiers serving drive thru
    # cashier_service_times : service time of cashiers
    # barista_num: num of baristas
    # barista mu: departure rate of barista

    def __init__(self, n, sys_lambda, queue_1_cashier_num, queue_2_cashier_num, cashier_service_times, barista_num, barista_mu, IP_threshold, DT_threshold):
        self.dispatcher = Dispatcher("Longest First")
        
        # Creates the in-person and drive-thru customer queues
        # In-person queue is at index 0, drive-thru queue is at index 1
        self.customer_queues = []
        self.customer_queues.append(Customer_Queue())
        self.customer_queues.append(Customer_Queue())

        # Creates the 3 order queues
        # In-person queue is at index 0, drive-thru queue is at index 1, online queue is at index 2
        self.order_queues = []
        self.order_queues.append(Order_Queue("FCFS", self.dispatcher))
        self.order_queues.append(Order_Queue("FCFS", self.dispatcher))
        self.order_queues.append(Order_Queue("FCFS", self.dispatcher))

        # gives dispatcher references to all order queues
        self.dispatcher.set_order_queues(self.order_queues)

        self.customers_left = 0
        self.max_customers_IP = 0
        self.max_customers_DT = 0

        self.IP_threshold = IP_threshold
        self.DT_threshold = DT_threshold
        self.threshold_policy = 'Threshold'

        self.patience = {'P': [.80, .20], 'I': [.30, .70], 'M': [0.54, 0.46]} # Patient, Impatient, and Moderate

        # Generates cashiers that serve in-person line
        self.cashiers = []
        for i in range(queue_1_cashier_num):
            cashier = Cashier(i, self.customer_queues[0], self.order_queues[0])
            self.cashiers.append(cashier)
            self.customer_queues[0].add_cashier(cashier)

        # Generates cashiers that serve drive-thru line;
        # Note that the cashier id's are offset by the number of cashiers that serve the in-person line
        for i in range(queue_1_cashier_num, queue_1_cashier_num + queue_2_cashier_num):
            cashier = Cashier(i, self.customer_queues[1], self.order_queues[1])
            self.cashiers.append(cashier)
            self.customer_queues[1].add_cashier(cashier) 

        # Create Baristas
        self.baristas = []
        for i in range(barista_num):
            self.baristas.append(Barista(i, self.dispatcher))
        self.dispatcher.set_bariastas(self.baristas)
        
        self.n = n # Number of customers that have to arrive before simulation ends 
        self.sys_lambda = sys_lambda # Arrivals to the system per second
        self.cashier_service_times = cashier_service_times
        self.barista_mu = barista_mu # Departures per second from the baristaa

        self.check_steady_state = True
        self.arrival_resp_times = np.empty(self.n)

    def run(self):
        system_time = 0  # Current time of the system
        next_event_times = [0, float('inf'), float('inf')] # Index 0 is the next arrival time, 1 is the next departure from a cashier, and 2 is the next departure from a barista
        next_dep_cashier = None  # The cashier from which the next departing order is coming from
        next_dep_barista = None  # The barista from which the next departing order is coming from

        arrivals = 0  # Number of customers that have arrived to the system

        og_arrivals_IP = 0 # Number of in-person customers that have originally arrived to the system
        og_arrivals_DT = 0
        og_arrivals_ON = 0
        
        total_response_time = 0  # Sum of response times of all customers serviced
        og_total_response_time = 0 # Sum of the response times of all customers serviced before any queue switch made
        og_total_response_time_IP = 0 # Sum of response times of all in-person customers serviced
        og_total_response_time_DT = 0 # Sum of response times of all drive-thru customers serviced
        og_total_response_time_ON = 0 # Sum of response times of all online customers serviced

        total_barista_service_time = 0

        resp_time_cashier = 0 # Sum of cashier response times, which is defined as the time between when the customer enters the system and when they leave the cashier
        resp_time_cashier_IP = 0 # Sum of in-person cashier response times, which is defined as the time between when the customer enters the system and when they leave the cashier
        resp_time_cashier_DT = 0 # Sum of drive-thru cashier response times, which is defined as the time between when the customer enters the system and when they leave the cashier
        resp_time_cashier_ON = 0 # Sum of online cashier response times, which is defined as the time between when the customer enters the system and when they leave the cashier

        resp_time_barista = 0 # Sum of barista response times, which is defined as the time between when the customer leaves the cashier and when they leave the system
        resp_time_barista_IP = 0 # Sum of in-person barista response times, which is defined as the time between when the customer leaves the cashier and when they leave the system
        resp_time_barista_DT = 0 # Sum of drive-thru barista response times, which is defined as the time between when the customer leaves the cashier and when they leave the system
        resp_time_barista_ON = 0 # Sum of online barista response times, which is defined as the time between when the customer leaves the cashier and when they leave the system

        

        total_arr = 0
        total_ent = 0


        while arrivals <= self.n:
            # Find the smallest of arrival time, departure time from cashier, and departure time from barista; then, return the index of the smallest value
            next_event = min(range(len(next_event_times)), key=next_event_times.__getitem__)

            system_time = next_event_times[next_event]
            
            # If the next event is an arrival
            if next_event == 0:
                # Flips a 3-sided, weighted coin to decide if the arrival came from the store (0), the drive through (1), or online (2)
                origin = random.choices([0, 1, 2], weights=(0.26, 0.27, 0.47), k=1)[0]

                og_origin = origin
                total_arr += 1

                # Simulate level of customer patience; 3 levels for simplicity

                customer_patience = random.choices(['P', 'I', 'M'], weights=(1, 1, 2), k=1)[0]
                customers_present_IP = self.customer_queues[0].size() + self.order_queues[0].get_queue_length()
                customers_present_DT = self.customer_queues[1].size() + self.order_queues[1].get_queue_length()

                # TODO: Test the thresholds
                if self.threshold_policy == 'Threshold':

                    # 0: stay/join queue, 1: do not join queue, either leave or join another queue
                    if origin == 2:
                        pass
                    if customers_present_IP >= self.IP_threshold and origin == 0:
                        customer_choice = random.choices([0, 1], weights=self.patience[customer_patience], k=1)[0]

                        # Customer "decision" determined by random weighted choice; either stay in line or switch lines, or even leave the store
                        # origin = random.choices([0, 1, 2, 3], weights=(0.07, 0.10, 0.8, 0.03), k=1)[0]

                        if customer_choice == 0:
                            origin = 0
                        else:
                            if customers_present_DT < customers_present_IP:
                                origin = 1
                                # If the customer switched from the in-person queue to either mobile or drive through queue, increment the number of customers that switched
                                self.customer_queues[0].inc_switched()
                            else:
                                if customer_patience != 'I':
                                    origin = 2
                                    self.customer_queues[0].inc_switched()
                                else:
                                    origin = 3

                    # If the drive through queue is too long, weighted chance for customers to decide to join either the in-person or the mobile order queue instead, or stay in line
                    if customers_present_DT >= self.DT_threshold and origin == 1:
                        customer_choice = random.choices([0, 1], weights=self.patience[customer_patience], k=1)[0]

                        # Chance for customer to join in-person queue, stay in drive-through queue, or the mobile order queue
                        # origin = random.choices([0, 1, 2], weights=(0.390, 0.6, 0.01), k=1)[0]
                        if customer_choice == 0:
                            pass
                        else:
                            if customers_present_IP < customers_present_DT:
                                origin = 0
                                self.customer_queues[1].inc_switched()
                            else:
                                if customer_patience != 'I':
                                    origin = 2
                                    self.customer_queues[1].inc_switched()
                                else:
                                    origin = 3
                    # # If customer left the store, dont add them to the customer queue
                    #     if origin == 1 or origin == 3:
                    #         pass


                if customers_present_IP > self.max_customers_IP:
                    self.max_customers_IP = customers_present_IP

                if customers_present_DT > self.max_customers_DT: 
                    self.max_customers_DT = customers_present_DT
                
                # Assigns the newly arrived job to a server based on the origin of the job
                rdm = random.uniform(self.cashier_service_times[0], self.cashier_service_times[1])
                if origin == 3:
                    self.customers_left += 1
                else:
                    self.dispatch(Order(arrivals, og_origin, origin, system_time, rdm ,get_exp(self.barista_mu)), origin)
                    total_ent += 1
                # The arrival time of the next job equals the current system time plus the interarrival time
                next_event_times[0] = system_time + get_exp(self.sys_lambda)

                if origin != 3:
                    arrivals += 1
                if og_origin == 0:
                    og_arrivals_IP += 1
                elif og_origin == 1:
                    og_arrivals_DT += 1
                else:
                    og_arrivals_ON += 1

                # if origin == 0:
                #     arrivals_IP += 1
                # elif origin == 1:
                #     arrivals_DT += 1
                # else:
                #     arrivals_ON += 1


            # If the next event is a departure from a cashier
            elif next_event == 1:
                next_dep_cashier.remove()
            # If the next event is a departure from a barista
            else:

                order = next_dep_barista.remove()

                total_barista_service_time += order.get_barista_service_time()

                if self.check_steady_state:
                    self.arrival_resp_times[order.get_id()] = order.get_response_time()

                total_response_time += order.get_response_time()
                og_total_response_time += order.get_response_time()     

                cashier_resp = order.get_dep_cashier_time() - order.get_arr_time()
                resp_time_cashier += cashier_resp

                barista_resp = order.get_dep_system_time() - order.get_dep_cashier_time()
                resp_time_barista += barista_resp

                if order.get_og_origin() == 0:
                    og_total_response_time_IP += order.get_response_time()
                    resp_time_cashier_IP += cashier_resp
                    resp_time_barista_IP += barista_resp
                elif order.get_og_origin() == 1:
                    og_total_response_time_DT += order.get_response_time()
                    resp_time_cashier_DT += cashier_resp
                    resp_time_barista_DT += barista_resp
                else:
                    og_total_response_time_ON  += order.get_response_time()
                    resp_time_cashier_ON += cashier_resp
                    resp_time_barista_ON += barista_resp

                # if order.get_origin() == 0:
                #     total_response_time_IP += order.get_response_time()
                #     resp_time_cashier_IP += cashier_resp
                #     resp_time_barista_IP += barista_resp
                # elif order.get_origin() == 1:
                #     total_response_time_DT += order.get_response_time()
                #     resp_time_cashier_DT += cashier_resp
                #     resp_time_barista_DT += barista_resp
                # else:
                #     total_response_time_ON += order.get_response_time()
                #     resp_time_cashier_ON += cashier_resp
                #     resp_time_barista_ON += barista_resp
            
            # Identifies the departure time of the order that will depart from a cashier the earliest
            next_dep_cashier = self.cashiers[0]
            for cashier in self.cashiers:
                if cashier.get_next_dep_time() < next_dep_cashier.get_next_dep_time():
                    next_dep_cashier = cashier
            next_event_times[1] = next_dep_cashier.get_next_dep_time()

            # Identifies the departure time of the order that will depart from a barista the earliest
            next_dep_barista = self.baristas[0]
            for barista in self.baristas:
                if barista.get_next_dep_time() < next_dep_barista.get_next_dep_time():
                    next_dep_barista = barista
            next_event_times[2] = next_dep_barista.get_next_dep_time()

        og_sys_avg_resp_time = og_total_response_time / arrivals
        # print("og total resp time: ", og_total_response_time)
        # print("arrivals: ", arrivals)
        og_sys_avg_resp_time_IP = og_total_response_time_IP / og_arrivals_IP
        og_sys_avg_resp_time_DT = og_total_response_time_DT / og_arrivals_DT
        og_sys_avg_resp_time_ON = og_total_response_time_ON / og_arrivals_ON
        probability_left = 1 - (total_ent / total_arr) # 1 - Probability customer enters queue
        mean_barista_service_time  = total_barista_service_time / arrivals

        customer_movement = [(self.customers_left), (self.customer_queues[0].get_switched() / total_arr), (self.customer_queues[1].get_switched() / total_arr)]

        # simulated_barista_average_response_times.append(resp_time_barista / arrivals)
        # simulated_barista_average_response_times_IP.append(resp_time_barista_IP / og_arrivals_IP)
        # simulated_barista_average_response_times_DT.append(resp_time_barista_DT / og_arrivals_DT)
        # simulated_barista_average_response_times_ON.append(resp_time_barista_ON / og_arrivals_ON)

        # simulated_cashier_average_response_times.append(resp_time_cashier / (og_arrivals_IP + og_arrivals_DT))
        # simulated_cashier_average_response_times_IP.append(resp_time_cashier_IP / og_arrivals_IP)
        # simulated_cashier_average_response_times_DT.append(resp_time_cashier_DT / og_arrivals_DT)
        # simulated_cashier_average_response_times_ON.append(resp_time_cashier_ON / og_arrivals_ON)

        # simulated_system_average_response_times.append(og_sys_avg_resp_time)
        # simulated_system_average_response_times_IP.append(og_sys_avg_resp_time_IP)
        # simulated_system_average_response_times_DT.append(og_sys_avg_resp_time_DT)
        # simulated_system_average_response_times_ON.append(og_sys_avg_resp_time_ON)

        self.get_switched()

        return [(og_sys_avg_resp_time),(og_sys_avg_resp_time_IP), (og_sys_avg_resp_time_DT), (og_sys_avg_resp_time_ON), 
                (self.arrival_resp_times), probability_left, mean_barista_service_time, customer_movement]

    # Dispatches an arriving job to a queue based on the origin of the job
    def dispatch(self, new_job, origin):
        if origin == 0:
            self.customer_queues[0].enqueue(new_job)
        elif origin == 1:
            self.customer_queues[1].enqueue(new_job)
        else:
            # Online orders never join a customer queue, so their departure time from the customer queue and the cashier is the same as their arrival time into the system
            new_job.set_dep_customer_queue_time(new_job.get_arr_time())
            new_job.set_dep_cashier_time(new_job.get_arr_time())
            self.order_queues[2].enqueue(new_job)

    def get_max_customers(self):
        print('max customers in IP: ', self.max_customers_IP)
        print('max customers in DT: ', self.max_customers_DT)
        print()
        return True
    
    def get_switched(self):
        print('customers left:', self.customers_left)
        print('customers switched from IP:', self.customer_queues[0].get_switched())
        print('customers switched from DT:', self.customer_queues[1].get_switched())

    
    
# Generates an exponentially distributed random variable
def get_exp(rate):
    if rate == 0:
        return float('inf')
    u = random.random()
    return (-1.0 / rate) * math.log(1 - u)

# Generates the expected response time of an M/M/k queueing system
def expected_response_time(lambda_val, mu, k):
    p = lambda_val / (mu*k)
    k_factorial = math.factorial(k)

    pi_0 = 0
    for i in range(0, k):
        pi_0 += (((k*p)**i)/math.factorial(i))       
    pi_0 += ((k*p)**k)/((k_factorial)*(1-p))
    
    pi_0 = (pi_0**(-1))

    p_q = (((k * p)**k) * pi_0) / ((k_factorial * (1-p)))

    e_nq = (p / (1 - p)) * p_q

    e_tq = (1/lambda_val) * e_nq #14.8, pg 262

    e_t = e_tq + (1/mu) #14.9
    
    return e_t

# def calc_moving_average(arr_resp_times, window_size):
#     result = []
#     moving_sum = sum(arr_resp_times[:window_size])
#     result.append(moving_sum / window_size)
#     for i in range(len(arr_resp_times) - window_size):
#         moving_sum

""" queue_length = []
time_in_queue = []
ids = []
# n, sys_lambda, queue_1_cashier_num, queue_2_cashier_num, cashier_mu, barista_num, barista_mu
system = SystemInstance(1_000_000, 1, 2, 1, 1, 3, 1000)
# print(1/(1-0.85))
print(expected_response_time(1.0, 1.0, 2))
print(system.run())

plt.plot(ids, time_in_queue, label='Actual')
plt.xlabel('order #')
plt.ylabel('time in queue')
plt.title('Simulated vs Actual Average Response Times')
plt.legend()
plt.show() """

barista_mu = 1/87 # 87 seconds per order

# factor = 16

# [(min time for cash transaction, max time for cash transaction), (min time for card transaction, max time for card transaction)]

# calculated_cashier_average_response_times = [0] *(factor - 1)
# calculated_barista_average_response_times = [0] *(factor - 1)  
simulated_barista_average_response_times = []
simulated_barista_average_response_times_IP = []
simulated_barista_average_response_times_DT = []
simulated_barista_average_response_times_ON = []

simulated_cashier_average_response_times = []
simulated_cashier_average_response_times_IP = []
simulated_cashier_average_response_times_DT = []
simulated_cashier_average_response_times_ON = []

simulated_system_average_response_times = []
simulated_system_average_response_times_IP = []
simulated_system_average_response_times_DT = []
simulated_system_average_response_times_ON = []
cashier_service_times = (29.21, 83.37)
thresholds = [1, 2, 3, 4, 5]

threshold_data = np.empty((len(thresholds), len(thresholds)))
threshold_data_IP = np.empty((len(thresholds), len(thresholds)))
threshold_data_DT = np.empty((len(thresholds), len(thresholds)))
threshold_data_ON = np.empty((len(thresholds), len(thresholds)))

prob_data = np.empty((len(thresholds), len(thresholds)))
customers_left = np.empty((len(thresholds), len(thresholds)))
customers_switched_from_IP = np.empty((len(thresholds), len(thresholds)))
customers_switched_from_DT = np.empty((len(thresholds), len(thresholds)))

lambda_val = 0.025
for i, IP_threshold in enumerate(thresholds):
        for j, DT_threshold in enumerate(thresholds):
            print("i, j: ", i,",", j)

            system = SystemInstance(1_000_000, lambda_val, 2, 1, cashier_service_times, 3, barista_mu, IP_threshold, DT_threshold)
            mean_resp_times = system.run()
            threshold_data[i, j] = mean_resp_times[0]
            threshold_data_IP[i, j] = mean_resp_times[1]
            threshold_data_DT[i, j] = mean_resp_times[2]
            threshold_data_ON[i, j] = mean_resp_times[3]

            customers_left[i, j] = mean_resp_times[7][0]
            customers_switched_from_IP[i, j] = mean_resp_times[7][1]
            customers_switched_from_DT[i, j] = mean_resp_times[7][2]

            prob_data[i, j] = mean_resp_times[5]

            # calculated_cashier_average_response_time = expected_response_time(lambda_val, mu, 2)
            # calculated_barista_average_response_time = expected_response_time(lambda_val, mu, 3)
            # calculated_cashier_average_response_time = 1/(mu - lambda_val)
            
            # calculated_cashier_average_response_times[i - 1] = calculated_cashier_average_response_time
            # calculated_barista_average_response_times[i - 1] = calculated_barista_average_response_time
            
            # n, sys_lambda, queue_1_cashier_num, queue_2_cashier_num, cashier_mu, barista_num, barista_mu
        
df_sys = pd.DataFrame(threshold_data, columns=thresholds, index=thresholds)
df_sys.to_csv('sys_threshold_data.csv')

df_prob = pd.DataFrame(prob_data, columns=thresholds, index=thresholds)
df_prob.to_csv('probability_left.csv')

df_customers_left = pd.DataFrame(customers_left, columns=thresholds, index=thresholds)
df_customers_left.to_csv('customers_left.csv')

df_customers_switched_from_IP = pd.DataFrame(customers_switched_from_IP, columns=thresholds, index=thresholds)
df_customers_switched_from_IP.to_csv('customers_switched_from_IP.csv')

df_customers_switched_from_DT = pd.DataFrame(customers_switched_from_DT, columns=thresholds, index=thresholds)
df_customers_switched_from_DT.to_csv('customers_switched_from_DT.csv')

df_IP = pd.DataFrame(threshold_data_IP, columns=thresholds, index=thresholds)
df_IP.to_csv('IP_threshold_data.csv')

df_DT = pd.DataFrame(threshold_data_DT, columns=thresholds, index=thresholds)
df_DT.to_csv('DT_threshold_data.csv')

df_ON = pd.DataFrame(threshold_data_ON, columns=thresholds, index=thresholds)
df_ON.to_csv('DT_threshold_data.csv')

resp_time_title = "Mean Response Time for Threshold"
prob_title = "Probability of Customers' Joining System"

# Plot_Data.plot_heatmap("System", resp_time_title,True,lambda_val, threshold_data, thresholds, True, mean_resp_times[6], 'Greens')
# Plot_Data.plot_heatmap("In-Person", resp_time_title, True, lambda_val, threshold_data_IP, thresholds, True, mean_resp_times[6], 'Greens')
# Plot_Data.plot_heatmap("Drive-Thru", resp_time_title, True, lambda_val, threshold_data_DT, thresholds, True, mean_resp_times[6], sns.cubehelix_palette(as_cmap=True))
# Plot_Data.plot_heatmap("Mobile", resp_time_title, True, lambda_val, threshold_data_ON, thresholds, True, mean_resp_times[6], sns.color_palette("light:#62381D", as_cmap=True))

Plot_Data.plot_heatmap("System", resp_time_title,lambda_val, threshold_data, thresholds, True, mean_resp_times[6])
Plot_Data.plot_heatmap("In-Person", resp_time_title, lambda_val, threshold_data_IP, thresholds, True, mean_resp_times[6])
Plot_Data.plot_heatmap("Drive-Thru", resp_time_title, lambda_val, threshold_data_DT, thresholds, True, mean_resp_times[6])
Plot_Data.plot_heatmap("Mobile", resp_time_title, lambda_val, threshold_data_ON, thresholds, True, mean_resp_times[6])
Plot_Data.plot_heatmap("Probability_of_leaving", prob_title, lambda_val, prob_data, thresholds, False, mean_resp_times[0])

prob_leaving_avg = np.mean(prob_data)
print("prob leaving avg: ", prob_leaving_avg)

arrival_resp_times = mean_resp_times[4]
df_ss = pd.DataFrame(arrival_resp_times, columns=['Arrival Response Times'])
df_ss['Moving Avg'] = df_ss['Arrival Response Times'].rolling(window=20000).mean()
arrivals = np.arange(0, len(df_ss['Moving Avg']))
df_ss.set_index(arrivals)
df_ss=df_ss.dropna()
print(df_ss.tail(50))
df_ss.to_pickle("steady_state.pkl")
Plot_Data.create_ss_plot(lambda_val, df_ss.index, df_ss['Moving Avg'])



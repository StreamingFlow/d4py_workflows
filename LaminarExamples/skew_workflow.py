from dispel4py.base import ProducerPE, IterativePE, ConsumerPE
from dispel4py.workflow_graph import WorkflowGraph
import random
import time
import numpy as np
class NumberProducer(ProducerPE):

    def __init__(self):
        ProducerPE.__init__(self)
        

    def _process(self, inputs):
        skewed_sleep_time = np.random.beta(2, 5) / 2  # will give values skewed towards 0 and between 0 and 0.5
        time.sleep(skewed_sleep_time)
        # print(f"sleep time is {skewed_sleep_time}")
        result = random.randint(1, 1000)
        return result

    
class IsPrime(IterativePE):

    def __init__(self):
        IterativePE.__init__(self)
        self.counter = 0

    def _process(self, num):
        self.counter += 1
        self.log("before checking data - %s - is prime or not and cnt is %s" % (num, self.counter))

        # print("before checking data - %s - is prime or not and cnt is %s" % (num, self.counter))


        if all(num % i != 0 for i in range(2, num)):

            return num
        
    def log(self, msg):
        print(msg)

class PrintPrime(ConsumerPE):
    def __init__(self):
        ConsumerPE.__init__(self)

    def _process(self, num):
        self.log("the num %s is prime" % num)

    def log(self, msg):
        print(msg)

producer = NumberProducer()
isprime = IsPrime()
printprime = PrintPrime()

graph = WorkflowGraph()
graph.connect(producer, 'output', isprime, 'input')
graph.connect(isprime, 'output', printprime, 'input')

# print(f"!!!graph node is {graph.getContainedObjects()}")
# from easydict import EasyDict as edict

# from dispel4py.new.simple_process import process as simple_process
# args = edict({'irer': 100})
# simple_process(graph, {producer: 20}, {'irer': 200})

# from dispel4py.new.multi_process import process as multi_process
# args = edict({'num': 5, 'simple' : False})
# multi_process(graph, {producer : 5}, args)

# from dispel4py.new.dynamic_redis import process as dyn_process
# args = edict({'num':5, 'simple' : False, 'redis_ip' : 'localhost', 'redis_port' : '6379'})
# dyn_process(graph, {producer : 5}, args)


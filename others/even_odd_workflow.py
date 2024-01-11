
# coding: utf-8

# # Even humans are odd!

# In this exercise we are going to create a dispel4py workflow that produces random numbers and it pairs them by ("one odd","one even") pattern. As we introduced before, we have different types of PEs: Generic, Iterative, Producer, Consumerk, SimpleFunction, ... In this exercise we are going to get familiar with the following ones: **GenericPE**, **IterativePE** and **ProducerPE**. 

# The first step is to create a PE class that produces a random integer number at the time in a range 1 to 1000, as we did in the "prime" workflow. 
# 
# Because this PE is our first one in this workflow and it has not any input streams, the most sensible choice is to use a **ProducerPE** type. However, we could also use a **GenericPE** type as well. Feel free to modify this ipython notebook to change it as you like. 
# 
# One quick comment about how to write data to the output streams. There are two options: 
# 
#  * return: it only provides one value. Then the process method is finished. 
#  * self.write: it can produce one or more value(s) during processing. Then it can continue to process (e.g. providing one/several value(s) in a loop). 
#  
# For this PE we could use both formats, as you can see in the following code. You could comment the one that you like less. 
#     

# In[ ]:

from dispel4py.base import ProducerPE
import random

class NumberProducer(ProducerPE):
    def __init__(self):
        ProducerPE.__init__(self)
        
    def _process(self, inputs):
        result= random.randint(1, 1000)
        return result
        #OR: self.write('output', result)


# After building the "NumberProducer" PE class, its output stream will be sent to another PE class (Divideby2) to determine if the number that has just been produced is even or odd. One way to perform this task is by dividing the the number by 2 and checking the reminder. If the reminder **is equal 0**, the number is **even**. Otherwise the number is **odd**. We are going to use a parameter (called "compare") for comparing the reminder with **0** and **1**, and therefore reuse the same PE class for getting the answer (odd or even). 
# 
# Because this PE class needs only 1 input and produces **0** or **1** output, we are going to create it by using a IterativePE type. 
# 

# In[ ]:

from dispel4py.base import IterativePE

class Divideby2(IterativePE):

    def __init__(self, compare):
        IterativePE.__init__(self)
        self.compare = compare

    def _process(self, data):
        if data % 2 == self.compare:
            return data


# Finally, the last PE in this workflow is going to receive two inputs streams. This PE will require two lists for grouping even and odd numbers. Therefore, GenericPE type is going to be the choice for creating this PE class. This type of PE requires to add the input ("odd" and "even") and output ("output") streams in the **\_\_init\_\_** method. Because we need to store the data between different iterations, we create member variables in the **\_\_init\_\_** method.
# 
# During the **\_process** method of this PE, the numbers received through its inputs will be appended to one list or another.  
# 
# As you can imagine, those lists can be imbalanced and one could have more elements than the other (because the producer PE has randomly generated more odd numbers than even, or the other way around). Therefore, in order to check if there are the numbers that have not been paired up (or "left over"), we can use the **\_postprocess** method for printing out which data has not be paired before. The **\_postprocess** method is launched only **once** per PE after all processing has completed. 

# In[ ]:

from dispel4py.core import GenericPE

class PairProducer(GenericPE):

    def __init__(self):
        GenericPE.__init__(self)
        self._add_input("odd")
        self._add_input("even")
        self._add_output("output")
        self.list_odd=[]
        self.list_even=[]

    def _process(self, inputs):
        if "odd" in inputs:
            self.list_odd.append(inputs["odd"])
        if "even" in inputs:
            self.list_even.append(inputs["even"])
       
        while self.list_odd and self.list_even:
            self.write("output", (self.list_odd.pop(0), self.list_even.pop(0)))
    
    def _postprocess(self):
        self.log('We are left behind: odd: %s, even: %s' % (self.list_odd, self.list_even))
        self.list_odd = []
        self.list_even = []


# Now we only have to create the graph and connect the different PEs. 
# Note that we create two PEs (filter_even and filter_odd) of the same type (Divideby2) to decide whether a number is odd or even. The output stream from the producer is connected to both filter PEs meaning that they both receive a copy of the same stream.

# In[ ]:

from dispel4py.workflow_graph import WorkflowGraph

producer = NumberProducer()
filter_even = Divideby2(0)
filter_odd = Divideby2(1)
pair = PairProducer()

graph = WorkflowGraph()
graph.connect(producer, 'output', filter_even, 'input')
graph.connect(producer, 'output', filter_odd, 'input')
graph.connect(filter_even, 'output', pair, 'even')
graph.connect(filter_odd, 'output', pair, 'odd')


#from dispel4py.new.simple_process import process as simple_process
#simple_process(graph, {producer: 20})


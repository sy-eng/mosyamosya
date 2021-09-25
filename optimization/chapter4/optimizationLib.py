import pandas as pd
import numpy as np

#This class came from algorithm4_1_resource_allocation_problem
class Node:
    def __init__(self, value, index):
        self.value = value
        self.index = index

#This class came from algorithm4_1_resource_allocation_problem
class Heap:
    #This requires O(N) memory
    
    def __init__(self):
        self.queue = []
    
    def swap(self, index1, index2):
        tmpValue = self.queue[index1].value
        tmpIndex = self.queue[index1].index
        self.queue[index1].value = self.queue[index2].value
        self.queue[index1].index = self.queue[index2].index
        self.queue[index2].value = tmpValue
        self.queue[index2].index = tmpIndex
    
    def add(self, node):
        self.queue.append(node)
        
        n = len(self.queue) - 1
        
        # Here is O(log N)
        while(n > 0):
            parentN = int((n - 1) / 2)
            
            if(self.queue[parentN].value > self.queue[n].value):
                break
            
            self.swap(parentN, n)
            
            n = parentN
    
    def get(self):
        if(len(self.queue) == 0):
            return None
        
        retValue = Node(self.queue[0].value, self.queue[0].index)
        #print(" ", retValue.value)
        
        self.queue[0].index = self.queue[-1].index
        self.queue[0].value = self.queue[-1].value
        
        self.queue = self.queue[: -1]
        
        queueLength = len(self.queue)
        n = 0
        
        # Here is O(log N)
        while(n < (queueLength - 1) / 2):
            childN = (n + 1) * 2
            
            #print(childN)
            #self.printData()
            
            if(queueLength == childN):
                if(self.queue[childN - 1].value > self.queue[n].value):                
                    self.swap(childN - 1, n)

                n = childN - 1
                
            else:
                if(self.queue[childN - 1].value > self.queue[childN].value):
                    selectedN = childN - 1
                else:
                    selectedN = childN
                
                if self.queue[selectedN].value > self.queue[n].value:
                    self.swap(selectedN, n)
            
                n = selectedN
        
        #self.printData()
        
        return retValue
    
    def printData(self):
        for q in self.queue:
            print("{:.3f}".format(q.value), end = " ")
            
        print(" ")

#This class came from algorithm4_2_kruskal
class QuickSort:
    # The data is not checked.
    # The pivot is the first element.
    # Here is O(N log N) in the best case or on average
    # Here is O(N log N) in the worst case
    def execute(self, nodes):
        
        if len(nodes) == 0:
            return []
        
        if len(nodes) == 1:
            return nodes
        
        smaller = []
        larger = []
        
        pivot = [nodes[0]]
        
        # Here can be O(N)
        for n in nodes[1:]:
            if(n.value <= nodes[0].value):
                smaller.append(n)
            else:
                larger.append(n)

        # This recursive process is O(log N) in the best case or on average
        # This recursive process is O(N^2) in the worst case
        return self.execute(smaller) + pivot + self.execute(larger)
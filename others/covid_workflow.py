from dispel4py.base import create_iterative_chain, ConsumerPE, IterativePE, ProducerPE, GenericPE
from dispel4py.workflow_graph import WorkflowGraph
import urllib.request
import json
import matplotlib.pyplot as plt
from datetime import datetime
import io

class DataProducer(GenericPE):
    def __init__(self, url):
        GenericPE.__init__(self)
        self.url = url
        self._add_output('output')

    def _process(self, inputs):
        response = urllib.request.urlopen(self.url)
        data = json.load(response)
        self.write('output', data)

class DataProcessor(IterativePE):
    def __init__(self):
        IterativePE.__init__(self)

    def _process(self, data):
        dates = []
        new_cases = []

        for entry in data['cases_time_series']:
            date_str = entry['date']
            date = datetime.strptime(date_str, "%d %B %Y")
            dates.append(date)
            new_cases.append(int(entry['dailyconfirmed']))
        return [dates, new_cases]

class DataVisualizer(ConsumerPE):
    def __init__(self):
        ConsumerPE.__init__(self) 

    def _process(self, inputs):
        dates, new_cases = inputs
        plt.figure(figsize=(12, 6))
        plt.plot(dates, new_cases, marker='o', linestyle='-')
        plt.title('COVID-19 Daily New Cases')
        plt.xlabel('Date')
        plt.ylabel('New Cases')
        plt.xticks(rotation=45)
        plt.tight_layout()
        #plt.show()
        fout="./covid_cases.png"
        plt.savefig(fout)

url = "https://api.covid19india.org/data.json"
# Create the workflow chain
producer = DataProducer(url)
processor = DataProcessor()
visualizer = DataVisualizer()

graph = WorkflowGraph()
graph.connect(producer, "output", processor, "input")
graph.connect(processor, "output", visualizer, "input")

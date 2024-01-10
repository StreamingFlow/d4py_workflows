from dispel4py.base import create_iterative_chain, IterativePE, ProducerPE, GenericPE
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
        for record in data['cases_time_series']:
            self.write('output', record)

class DataProcessor(IterativePE):
    def __init__(self):
        IterativePE.__init__(self)

    def _process(self, data):
        dates = []
        new_cases = []

        date_str = data['date']
        date = datetime.strptime(date_str, "%d %B %Y")
        dates.append(date)
        new_cases.append(int(data['dailyconfirmed']))
        return [dates, new_cases]

class DataVisualizer(GenericPE):
    def __init__(self):
        GenericPE.__init__(self)
        self._add_input('input')
        self._add_output('output')
        self.inputconnections['input']["grouping"] = "global"
        self.results = {}
        self.results['dates']=[]
        self.results['new_cases']=[]

    def _process(self, inputs):
        self.results['dates'].append(inputs['input'][0])
        self.results['new_cases'].append(inputs['input'][1])

    def _postprocess(self):
        dates = self.results['dates']
        new_cases = self.results['new_cases']
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

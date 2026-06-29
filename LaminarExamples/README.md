# Laminar Examples

A collection of self-contained [dispel4py](https://github.com/StreamingFlow/d4py) workflows used as examples for the **Laminar** serverless streaming framework. Each `*.py` file builds a `WorkflowGraph` out of Processing Elements (PEs) connected as a stream-based pipeline, and can be run with any of the dispel4py mappings (`simple`, `mpi`, `multi`, `redis`, the dynamic/autoscaling variants, etc.).

The examples range from tiny synthetic pipelines (good for learning the PE model and for stress-testing schedulers) up to real scientific workflows in astronomy and seismology. Several come in a normal version plus a "skew" version that injects an uneven, randomly distributed per-record workload — useful for evaluating load balancing and dynamic/autoscaling mappings.

> **What is Laminar?** Laminar is a serverless, stream-based framework built on top of dispel4py. It manages streaming workflows and PEs through a registry and adds LLM-based semantic code search, summarization, and completion. The workflows here are the kind of components Laminar registers, searches, and executes. See the [StreamingFlow organization](https://github.com/StreamingFlow) for the framework itself.

## Requirements

Activate the conda Python 3.10+ environment with dispel4py installed. If you have not created one yet, follow the [dispel4py README](https://github.com/StreamingFlow/d4py#installation).

```shell
conda activate d4py_env
```

Individual workflows have additional dependencies:

| Workflow(s) | Extra packages |
|---|---|
| `even_odd_workflow.py`, `skew_workflow.py`, `SensorWorkflow.py` | `numpy` |
| `covid_workflow.py` | `numpy`, `matplotlib` |
| `int_ext_graph.py`, `int_ext_graph_skew.py` | `numpy`, `requests`, `astropy` |
| `realtime_prep.py`, `realtime_prep_dict.py` | `numpy`, `scipy`, `obspy` |

Install as needed, for example:

```shell
pip install obspy        # seismic workflows
pip install astropy      # astronomy workflows
```

## Directory contents

| File | Type | Purpose |
|---|---|---|
| `even_odd_workflow.py` | Workflow | Produces random integers and pairs them as (odd, even). A teaching example of `ProducerPE`, `IterativePE`, and `GenericPE`. |
| `skew_workflow.py` | Workflow | Prime-number pipeline that sleeps a *skewed* (Beta-distributed) amount per item to simulate an uneven workload. |
| `SensorWorkflow.py` | Workflow | Reads sensor temperature readings, normalizes them, flags anomalies, alerts, and reports running averages. |
| `covid_workflow.py` | Workflow | Downloads a COVID-19 daily-cases time series, processes it, and renders a plot. |
| `int_ext_graph.py` | Workflow | Astronomy: computes the internal extinction of galaxies from VizieR VOTable queries. |
| `int_ext_graph_skew.py` | Workflow | Same as above, with injected skewed sleep times to model uneven per-record cost. |
| `realtime_prep.py` | Workflow | Seismic noise pre-processing (phase 1 of seismic cross-correlation): decimate, detrend, demean, instrument-response removal, filter, normalize, whiten, FFT. |
| `realtime_prep_dict.py` | Workflow | Same seismic pipeline, but data is passed between PEs as JSON-serializable dictionaries so it works with mappings that require serialization (e.g. Redis/dynamic). |
## The workflows

### Learning and benchmarking pipelines

**`even_odd_workflow.py`** — `NumberProducer` emits random integers (1–1000). Two `Divideby2` PEs receive a copy of the stream and keep only odd or only even numbers; `PairProducer` pairs them up and logs any leftover, unpaired numbers in its post-process step. This is the recommended starting point for understanding the dispel4py PE types and how a single output stream can fan out to multiple downstream PEs.

**`skew_workflow.py`** — A producer/filter/consumer prime-number pipeline (`NumberProducer` → `IsPrime` → `PrintPrime`). The producer sleeps for a Beta(2, 5)-distributed time before emitting each value, creating a deliberately uneven workload. Pair it with the dynamic and autoscaling mappings to observe how work is rebalanced under skew.

### Sensor data

**`SensorWorkflow.py`** — A five-stage stream pipeline over `sensor_data_1000.json`:

1. `ReadSensorDataPE` (producer) reads the JSON file and emits one `{timestamp, temperature}` record at a time.
2. `NormalizeDataPE` scales temperature to a 0–1 range.
3. `AnomalyDetectionPE` compares each reading against the running mean and tags anomalies.
4. `AlertingPE` prints an alert for flagged readings.
5. `AggregateDataPE` (consumer) prints the average of every 5 readings.

The entry PE expects an input of the form `{"input": "sensor_data_1000.json"}`.

### COVID-19 time series

**`covid_workflow.py`** — `DataProducer` fetches a JSON time series over HTTP, `DataProcessor` parses each record's date and daily confirmed cases, and `DataVisualizer` (a globally-grouped PE) collects everything and writes a line chart to `covid_cases.png` in its post-process step.

> **Note:** the data URL hard-coded in this file (`api.covid19india.org`) was retired after the original project ended, so the download may fail. Point `url` at any equivalent JSON time series, or adapt `DataProcessor` to your source's schema, to run it today.

### Astronomy: internal extinction

**`int_ext_graph.py`** — Computes the internal dust extinction of galaxies. `ReadRaDec` reads RA/DEC coordinates from a text file; `GetVOTable` queries the VizieR VOTable service for each coordinate; `FilterColumns` extracts the morphological type (`MType`) and `logR25`; `InternalExtinction` computes the extinction value per galaxy. The entry PE expects `{"input": "coordinates.txt"}` (a comma-separated `RA,DEC` per line).

**`int_ext_graph_skew.py`** — Identical pipeline with Beta-distributed `time.sleep` calls injected into `GetVOTable` and `FilterColumns`, so the per-record cost is skewed. Use it to benchmark mappings under uneven load. The random seed is fixed (`np.random.seed(42)`) for reproducibility.

> The header of both files documents `multi` and `mpi` invocations and notes that the `-s` (simple-types) flag avoids a known NumPy/pickle issue with empty string dtypes.

### Seismology: real-time preparation

Phase 1 of the seismic cross-correlation application — an "embarrassingly parallel," stateless per-station pipeline (decimate → detrend → demean → remove instrument response → band-pass filter → normalize → spectral whitening → FFT → save). See the [`seismic_preparation`](https://github.com/StreamingFlow/d4py_workflows/tree/main/seismic_preparation) and [`tc_cross_correlation`](https://github.com/StreamingFlow/d4py_workflows/tree/main/tc_cross_correlation) directories for the full application and data-download helpers.

**`realtime_prep.py`** — Passes raw ObsPy `Stream` objects between PEs.

**`realtime_prep_dict.py`** — Converts streams (and FFT results) to/from plain dictionaries at each step, making every message JSON-serializable. Prefer this version with mappings that serialize data across processes or hosts (Redis and the dynamic mappings).

Both expect:

- An `INPUT/` directory containing `stream_<NETWORK>_<STATION>_*.mseed` waveform files and `<NETWORK>_inventory.xml` response files.
- The station list `Copy-Uniq-OpStationList-NetworkStation.txt` as the entry input.
- The hard-coded path near the top edited to your checkout:

  ```python
  #### Important -- change with your path to this workflow
  sys.path.append('/home/user/d4py_workflows/seismic_preparation')
  ####
  ```

# SimASM

**Abstract State Machine Framework for Discrete Event Simulation**

SimASM is a Python package for modeling, simulating, and verifying discrete event systems using Abstract State Machines (ASM) as a common semantic foundation.

## Features

- **DSL for Simulation Models**: Write discrete event simulation models in a clean, readable syntax
- **Multiple Formalisms**: Support for Event Graph and Activity Cycle Diagram modeling styles
- **Stutter Equivalence Verification**: Formally verify that two models produce equivalent observable behavior
- **Jupyter Integration**: Interactive modeling with `%%simasm` magic commands
- **Statistics Collection**: Built-in support for time-average, utilization, and count statistics
- **Automatic Plotting**: Generate publication-quality plots with confidence intervals, box plots, and time series traces

## Installation

```bash
pip install simasm
```

For Jupyter support:
```bash
pip install simasm[jupyter]
```

## Quick Start

### In Jupyter/Colab

```python
import simasm  # Auto-registers %%simasm magic
```

Define a model:
```
%%simasm model --name mm1_queue
domain Event
domain Load

var sim_clocktime: Real
var queue: List<Load>

// ... model definition
```

Run an experiment:
```
%%simasm experiment
experiment MyExperiment:
    model := "mm1_queue"

    replication:
        count: 10
        warm_up_time: 100.0
        run_length: 1000.0
    endreplication

    statistics:
        stat AvgQueueLength: time_average
            expression: "lib.length(queue)"
        endstat
    endstatistics
endexperiment
```

### From Python

```python
from simasm.experimenter.engine import ExperimenterEngine

# Run an experiment
engine = ExperimenterEngine("experiments/my_experiment.simasm")
result = engine.run()

print(f"Average queue length: {result['L_queue']}")
```

## Model Syntax

SimASM uses a domain-specific language for defining simulation models:

```simasm
// Domain declarations
domain Load
domain Server

// Constants and variables
const server: Server
var sim_clocktime: Real
var queue: List<Load>

// Random stream variables
var interarrival_time: rnd.exponential(1.25) as "arrivals"
var service_time: rnd.exponential(1.0) as "service"

// Rules
rule arrive() =
    let load = new Load
    lib.add(queue, load)
    // Schedule next arrival
endrule

// Main rule
main rule main =
    if sim_clocktime < sim_end_time then
        run_routine()
    endif
endrule

// Initial state
init:
    sim_clocktime := 0.0
    queue := []
endinit
```

## Automatic Plotting

SimASM can automatically generate plots for your experiments with time series traces and statistical analysis:

```simasm
experiment MyExperiment:
    model := "my_model.simasm"

    replication:
        count: 30
        warm_up_time: 100.0
        run_length: 1000.0
        generate_plots: true      // Enable automatic plotting
        trace_interval: 10.0      // Sample traces every 10 time units
    endreplication

    statistics:
        stat queue_length: time_average
            expression: "lib.length(queue)"
            trace: true           // Capture time series data
        endstat

        stat utilization: time_average
            expression: "busy / capacity"
            trace: true
        endstat
    endstatistics
endexperiment
```

This automatically generates three types of plots:

1. **Summary Statistics** (`summary_statistics.png`)
   - Bar chart showing mean ± 95% confidence intervals
   - Compares all statistics side-by-side

2. **Box Plots** (`boxplots.png`)
   - Distribution analysis across replications
   - Shows median, quartiles, and outliers

3. **Time Series** (`timeseries.png`)
   - Evolution of statistics over simulation time
   - Mean trace with 95% confidence bands
   - Highlights warmup period

Plots are saved to timestamped directories: `simasm/output/YYYY-MM-DD_HH-MM-SS_ExperimentName/`

In Jupyter notebooks, plots display inline. From CLI/Python scripts, plots are saved as PNG files.

## Verification

SimASM can verify stutter equivalence between two models:

```
%%simasm verify
verification EG_vs_ACD:
    models:
        import EG from "event_graph_model.simasm"
        import ACD from "acd_model.simasm"
    endmodels

    seed: 42

    labels:
        label queue_empty for EG: "queue_count() == 0"
        label queue_empty for ACD: "queue_count() == 0"
    endlabels

    observables:
        observable queue_empty:
            EG -> queue_empty
            ACD -> queue_empty
        endobservable
    endobservables

    check:
        type: stutter_equivalence
        run_length: 1000.0
    endcheck
endverification
```

## Documentation

- [Full Documentation](https://github.com/yourusername/simasm)
- [Examples](https://github.com/yourusername/simasm/tree/main/examples)

## License

MIT License - see [LICENSE](LICENSE) for details.

## Citation

If you use SimASM in your research, please cite:

```bibtex
@software{simasm,
  title = {SimASM: Abstract State Machine Framework for Discrete Event Simulation},
  author = {Steve},
  year = {2024},
  url = {https://github.com/yourusername/simasm}
}
```

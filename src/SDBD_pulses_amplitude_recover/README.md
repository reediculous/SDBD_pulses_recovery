
# PulseApproximator

A Python package for recovering clipped current pulses in experimental signal data. Also contains useful functions to extract, fit, and visualize pulses.

---

## Features

- **Pulse Fitting:** Robust parametric approximation of current pulses using a two-component model.
- **Flexible Preprocessing:** Automatic event start detection and signal smoothing.
- **Peak Batch Processing:** Efficiently process multiple pulses from indexed files.
- **Visualization:** Plot original and restored/fitted pulse overlays.

---

## Installation

```bash
pip install pulseapproximator
```

Or, from source:

```bash
git clone https://github.com/yourname/pulseapproximator.git
cd pulseapproximator
pip install .
```

---

## Requirements

- Python 3.7+
- numpy
- scipy
- matplotlib (for plotting)

---

## Usage Example

### 1. Pulse Approximation

```python
import numpy as np
from pulseapproximator import PulseApproximator

# Load your time/current data
time = ...    # 1D numpy array
current = ... # 1D numpy array

approximator = PulseApproximator(window_length=15)
fitted = approximator.approximate(time, current)
```

### 2. Batch Workflow

Process all peaks described in a peaks file, creating plots and a stats file:

```python
from pulseapproximator import process_all_peaks

summary = process_all_peaks(
    peaks_file="cut_peaks_positions.txt",
    data_dir="./data_01_11_2017",
    plots_dir="./plots"
)
print(summary)
```

### 3. Fine-grained Usage

All subcomponents are reusable:

```python
from pulseapproximator import (
    parse_cut_peaks_file, load_npz_data,
    find_event_start, find_event_end, plot_restore, PulseApproximator
)

peaks = parse_cut_peaks_file("peaks_file.txt")
for fname, peak_idx, plateau_length in peaks:
    data = load_npz_data(fname)
    t, i = data["time"], data["current"]
    # Find event window around a peak
    start_idx = find_event_start(i, peak_idx)
    end_idx = find_event_end(i, peak_idx)
    time = t[start_idx:end_idx]
    current = i[start_idx:end_idx]
    fitted = PulseApproximator().approximate(time, current)
    plot_restore(time, current, fitted, fname, restored=True, out_dir="./plots")
```

---

## API

| Function/Class              | Description |
|-----------------------------|-------------|
| `PulseApproximator`         | Main class for pulse fitting/approximation. |
| `parse_cut_peaks_file`      | Parses a peaks positions file into a list of tuples. |
| `load_npz_data`             | Loads `.npz` file and returns time/voltage/current. |
| `find_event_start` / `find_event_end` | Detects pulse event window in a signal. |
| `plot_restore`              | Plots and saves an overlay of original and fitted pulses. |
| `process_all_peaks`         | High-level batch processor for many peaks and files. |

---

## License

MIT

---

## Acknowledgments

Forked and extended from original scripts by [Your Name / Institution], 2024.

---

## Contributing

Pull requests welcome! Please open issues for bugs or suggestions.

---

## Contact

Email: your.email@example.com
GitHub: [yourname](https://github.com/yourname)

---

**Happy pulse analyzing!**

---

Let me know if you want additional usage examples, explanations of parameters, or other information for your README!

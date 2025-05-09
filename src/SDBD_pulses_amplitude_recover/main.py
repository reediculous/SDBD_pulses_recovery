import os
import numpy as np
import matplotlib.pyplot as plt

from approximator import PulseApproximator

CUT_PEAKS_FILE = "cut_peaks_positions.txt"
PLOTS_DIR = "plots"

def ensure_plots_dir():
    if not os.path.exists(PLOTS_DIR):
        os.makedirs(PLOTS_DIR)

def parse_cut_peaks_file(filename):
    peaks = []
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.lower().startswith('filename'):
                fname, idx, pl = line.split(",")
                peaks.append((fname.strip(), int(idx), int(pl)))
    return peaks

def find_event_start(current_data, peak_index, threshold_factor=0.1):
    derivative = np.diff(current_data[:peak_index])
    if len(derivative) == 0:
        return 0
    threshold = threshold_factor * np.max(derivative)
    start_candidates = np.where(derivative > threshold)[0]
    if len(start_candidates) > 0:
        start_index = start_candidates[0]
    else:
        start_index = max(0, int(peak_index * 0.9))
    return max(0, start_index)

def find_event_end(current_data, peak_index, threshold_factor=0.1, extra_points=20):
    # analyze after peak_index
    derivative = np.diff(current_data[peak_index:])
    if len(derivative) == 0:
        return len(current_data)-1
    threshold = threshold_factor * np.max(derivative)
    end_candidates = np.where(derivative < -threshold)[0]
    if len(end_candidates) > 0:
        end_index = peak_index + end_candidates[0]
    else:
        # fallback: 10% after peak
        end_index = min(len(current_data)-1, int(peak_index + (len(current_data)-peak_index)*0.1))
    end_index = min(len(current_data)-1, end_index + extra_points)
    return end_index

def plot_restore(time, current, fitted, filename, restored):
    plt.figure(figsize=(8,6))
    plt.plot(time, current, label="Original current", color='blue')
    plt.plot(time, fitted, label="Fitted pulse", color='red', linestyle='--')
    plt.xlabel("Time")
    plt.ylabel("Current")
    plt.legend()
    plt.title(f"{os.path.basename(filename)} - {'Restored' if restored else 'Not restored'}")
    out_name = os.path.splitext(os.path.basename(filename))[0]
    status = "restored" if restored else "not_restored"
    out_file = os.path.join(PLOTS_DIR, f"{out_name}_{status}.png")
    plt.savefig(out_file, dpi=150)
    plt.close()

def main():
    ensure_plots_dir()
    peaks = parse_cut_peaks_file(CUT_PEAKS_FILE)
    non_restored_count = 0
    restored_count = 0

    approximator = PulseApproximator(window_length=15)

    plateu_lengths = []
    for file_path, peak_idx, plateu_l in peaks:
        file_path = file_path.replace('../', '').replace('data_01_11_2017/', '')
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            non_restored_count += 0 # TODO: потому что запускаем пока на сабсете, не все файлы есть!
            continue
        try:
            npz = np.load(file_path)
            data = npz['data']
            t, v, i = data[0], data[1], data[2]
        except Exception as e:
            print(f"Failed to load {file_path}: {e}")
            non_restored_count += 1
            continue

        # Find start and end
        event_start = peak_idx - 30
        event_end = peak_idx + 150
        # Safety
        if event_end - event_start < 5:
            print(f"Event too short for {file_path}")
            non_restored_count += 1
            continue

        time = t[event_start:event_end]
        current = i[event_start:event_end]

        if len(time) < 3:
            print(f"Pulse window too short in {file_path}")
            non_restored_count += 1
            continue

        fitted = approximator.approximate(time, current.copy())

        amp_current = np.max(current)
        amp_fitted = np.max(fitted)

        if abs(amp_fitted - amp_current) > 0.01 and amp_fitted < amp_current:
            non_restored_count += 1
            plateu_lengths.append(plateu_l)
            plot_restore(time, current, fitted, file_path, restored=False)
            continue
        else:
            restored_count += 1
            plot_restore(time, current, fitted, file_path, restored=True)

    # Write stats
    with open(os.path.join(PLOTS_DIR, "stats.txt"), "w") as f:
        f.write(f"Non-restored peaks: {non_restored_count}\n")
        f.write(f"Restored peaks: {restored_count}\n")
        f.write(f"Average Plateu Length in Non-restored: {np.mean(plateu_lengths)}")
    print(f"Done. Non-restored: {non_restored_count}, Restored: {restored_count}")

if __name__ == "__main__":
    main()

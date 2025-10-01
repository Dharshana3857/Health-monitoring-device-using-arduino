# dashboard.py
# Usage:
#   Serial mode: python dashboard.py --port COM3
#   File mode:   python dashboard.py --file health.csv
#
# Requirements: pyserial, pandas, matplotlib

import argparse
import sys
import time
import collections

import matplotlib.pyplot as plt

def serial_mode(port, baud=9600, max_points=100, save_on_exit=None):
    import serial
    try:
        ser = serial.Serial(port, baud, timeout=1)
        time.sleep(2)  # allow Arduino reset
    except Exception as e:
        print(f"ERROR opening serial port {port}: {e}")
        return

    times = []
    temps = []
    bpms = []

    plt.ion()
    fig, (ax1, ax2) = plt.subplots(2,1, figsize=(8,6))

    print("Reading from serial. Press Ctrl+C to stop.")
    try:
        while True:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if not line:
                continue
            # optionally skip header lines
            if line.lower().startswith("time"):
                continue
            parts = [p.strip() for p in line.split(',')]
            if len(parts) < 3:
                # not the expected CSV line
                # print("Skip:", line)
                continue
            try:
                t = float(parts[0])
                temp = float(parts[1])
                bpm_raw = parts[2]
                bpm = None
                if bpm_raw.upper() != "N/A" and bpm_raw != "":
                    bpm = float(bpm_raw)
            except Exception as e:
                # parsing failed; skip line
                # print("parse error:", e, "line:", line)
                continue

            # Append values (keep BPM optionally None)
            times.append(t)
            temps.append(temp)
            bpms.append(bpm)

            # keep only last max_points
            if len(times) > max_points:
                times = times[-max_points:]
                temps = temps[-max_points:]
                bpms = bpms[-max_points:]

            # Plot
            ax1.clear()
            ax2.clear()

            ax1.plot(times, temps, marker='o', linestyle='-')
            ax1.set_ylabel("Temp (°C)")
            ax1.set_title("Temperature vs Time")

            # For BPM, only plot points that are not None
            bpmtimes = [tt for tt,bb in zip(times, bpms) if bb is not None]
            bpmvals = [bb for bb in bpms if bb is not None]
            if bpmtimes:
                ax2.plot(bpmtimes, bpmvals, marker='x', color='red', linestyle='-')
            ax2.set_ylabel("BPM")
            ax2.set_xlabel("Time (s)")
            ax2.set_title("BPM vs Time")

            plt.tight_layout()
            plt.pause(0.1)

    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        try:
            ser.close()
        except:
            pass
        if save_on_exit:
            # save last collected data to CSV
            import csv
            fname = save_on_exit
            print(f"Saving last data to {fname}")
            with open(fname, 'w', newline='') as f:
                w = csv.writer(f)
                w.writerow(["Time(s)","Temp(C)","BPM"])
                for tt, tmp, bb in zip(times, temps, bpms):
                    w.writerow([tt, tmp, bb if bb is not None else "N/A"])
            # also save a PNG snapshot of the plot
            pngname = fname.rsplit('.',1)[0] + "_plot.png"
            fig.savefig(pngname)
            print(f"Saved plot to {pngname}")
        plt.ioff()
        plt.show()


def file_mode(csvfile, save_plot=None):
    import pandas as pd
    try:
        df = pd.read_csv(csvfile, comment='#', header=0)
    except Exception as e:
        print(f"ERROR reading {csvfile}: {e}")
        return

    # Basic cleaning
    # Expecting columns: Time(s), Temp(°C), BPM  (case-insensitive)
    cols = {c.lower(): c for c in df.columns}
    # find keys
    def find_col(key):
        k = key.lower()
        return cols.get(k, None)

    time_col = find_col("time(s)") or find_col("time") or list(cols.values())[0]
    temp_col = find_col("temp(°c)") or find_col("temp") or list(cols.values())[1]
    bpm_col = find_col("bpm") or list(cols.values())[2] if len(cols)>=3 else None

    t = df[time_col].astype(float)
    temp = df[temp_col].astype(float)
    bpm = None
    if bpm_col:
        bpm = pd.to_numeric(df[bpm_col], errors='coerce')  # will convert "N/A" to NaN

    # Plot
    fig, (ax1, ax2) = plt.subplots(2,1, figsize=(8,6))
    ax1.plot(t, temp, marker='o')
    ax1.set_ylabel("Temp (°C)")
    ax1.set_title("Temperature vs Time")

    if bpm is not None:
        ax2.plot(t, bpm, marker='x', color='red')
    ax2.set_ylabel("BPM")
    ax2.set_xlabel("Time (s)")
    ax2.set_title("BPM vs Time")

    plt.tight_layout()
    if save_plot:
        fig.savefig(save_plot)
        print(f"Saved plot to {save_plot}")
    plt.show()


def main():
    parser = argparse.ArgumentParser(description="Arduino Health Monitor dashboard (serial or file mode).")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--port', help='Serial port (e.g., COM3 or /dev/ttyUSB0)')
    group.add_argument('--file', help='CSV file path (exported from Serial Monitor)')
    parser.add_argument('--baud', type=int, default=9600, help='Serial baud rate (default 9600)')
    parser.add_argument('--max', type=int, default=100, help='Max points to show in live plot')
    parser.add_argument('--save', help='If provided in serial mode: save last data to this CSV on exit; in file mode: save plot to this filename')
    args = parser.parse_args()

    if args.port:
        serial_mode(args.port, baud=args.baud, max_points=args.max, save_on_exit=args.save)
    else:
        file_mode(args.file, save_plot=args.save)

if __name__ == "__main__":
    main()

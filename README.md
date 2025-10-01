# Arduino Health Monitoring Device

An Arduino-based health monitoring system that measures body temperature using an LM35 sensor and simulates heart rate (BPM) with a push button. The results are displayed on a 16×2 LCD, logged in the Serial Monitor, and an alert system (buzzer + LED) notifies when abnormal values are detected.

---

## ⚙️ Features
- Measure body temperature with LM35 sensor  
- Simulate BPM using a push button  
- Display readings on 16×2 LCD  
- Alert system with buzzer and LED for abnormal values (Temp > 38°C or BPM > 100)  
- Serial Monitor logging in CSV format for easy graphing in Excel or Python  
- Tinkercad simulation available for virtual testing  

---

## 🛠 Components
- Arduino Uno  
- LM35 temperature sensor  
- Push button (for pulse simulation)  
- 16×2 LCD + potentiometer (for contrast)  
- Piezo buzzer  
- Red LED + 220Ω resistor  
- Breadboard + jumper wires

---
## 🔎 Data Visualization with Python

This project also includes a **Python script** that reads the Arduino/Tinkercad output (CSV) and generates real-time or offline graphs.

- **dashboard.py** → Reads CSV or Serial output and plots graphs using matplotlib.
- **health_data.csv** → Sample dataset collected from Arduino/Tinkercad.
- **health_plot.png** → Example output graph.

### Usage
Run the script in file mode:
```bash
python dashboard.py --file code/health_data.csv --save docs/health_plot.png

Run and test the project directly in Tinkercad:  
[🔗 Arduino Health Monitor Simulation](https://www.tinkercad.com/things/67KJe31Xc2Y-health-monitor-device?sharecode=U8fZo2YqBiZMBVjh-tUB_O1cb_Xs4QOgrW5cOOaIch0)




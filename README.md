# MacSentinel
A lightweight Python tool to monitor macOS background Dark Wake transitions, system activity, and potential security anomalies.
# MacSentinel 🛡️

**MacSentinel** is a lightweight Python utility designed to monitor macOS background activities, **Dark Wake** state transitions, and system events while the screen is off or locked.

---

## 🚀 Features
- 🌙 **Dark Wake Detection:** Tracks low-power background wakeups (iCloud sync, Find My, Handoff).
- 🔓 **Full Wake Tracking:** Records when the display turned on or user unlocked the machine.
- 🔒 **Privacy Monitoring:** Detects Bluetooth Low Energy (BLE) MAC address rotations.
- 🔑 **Auth Activity:** Identifies `akd` and AuthKit Apple ID validation checks.
- 🚨 **Nighttime Anomaly Detection:** Flags unexpected wakeups or TCC permission requests occurring between 1:00 AM and 6:00 AM.

---

## 🚀 Quick Start

Run the script directly via terminal:

```bash
python3 mac_sentinel.py

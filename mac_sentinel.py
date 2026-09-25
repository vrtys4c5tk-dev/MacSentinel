#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MacSentinel - macOS Dark Wake & Background Activity Monitor
Copyright (c) 2026 MacSentinel

Licensed under the Dual License (Non-Commercial / Commercial).
See LICENSE file in the project root for full license information.
"""

import subprocess
import re
from datetime import datetime, timedelta

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def run_log_command(hours_back=24):
    start_time = (datetime.now() - timedelta(hours=hours_back)).strftime("%Y-%m-%d %H:%M:%S")
    predicate = (
        'subsystem CONTAINS "com.apple.sharing" OR '
        'subsystem CONTAINS "com.apple.authkit" OR '
        'subsystem CONTAINS "com.apple.SkyLight" OR '
        'process == "sharingd" OR process == "akd"'
    )
    cmd = ["log", "show", "--start", start_time, "--predicate", predicate, "--style", "syslog"]
    print(f"[*] Analyzing logs for the last {hours_back} hours (Start: {start_time})...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"{RED}[!] Error reading logs: {e}{RESET}")
        return ""

def parse_logs(log_data):
    events = []
    time_pattern = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})")
    for line in log_data.splitlines():
        time_match = time_pattern.match(line)
        if not time_match:
            continue
        timestamp_str = time_match.group(1)
        dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        is_night = 1 <= dt.hour < 6

        if "Dark Wake" in line:
            events.append({"time": timestamp_str, "dt": dt, "type": "DARK_WAKE", "detail": "Device woke up in background low-power mode.", "is_anomaly": is_night})
        elif "Event: Will Wake" in line:
            events.append({"time": timestamp_str, "dt": dt, "type": "FULL_WAKE", "detail": "Display turned on / User woke up the device.", "is_anomaly": False})
        elif "BLE address changed" in line or "Bluetooth address changed" in line:
            events.append({"time": timestamp_str, "dt": dt, "type": "PRIVACY", "detail": "Bluetooth (BLE) MAC address refreshed for privacy.", "is_anomaly": False})
        elif "Checking iCDP status" in line or "Apple ID account state" in line:
            events.append({"time": timestamp_str, "dt": dt, "type": "AUTH", "detail": "iCloud / Apple ID security verification check.", "is_anomaly": False})
        elif "TCCAccessRequest" in line:
            events.append({"time": timestamp_str, "dt": dt, "type": "SECURITY", "detail": "System permission request (TCC) triggered.", "is_anomaly": is_night})
    return events

def generate_report(events):
    print("\n" + "="*65)
    print("        MACSENTINEL - BACKGROUND WAKE & ACTIVITY REPORT")
    print("        License: Dual License | Copyright (c) 2026 MacSentinel")
    print("="*65)
    if not events:
        print(f"{GREEN}[+] No background activity found for the specified timeframe.{RESET}")
        return

    dark_wakes = [e for e in events if e["type"] == "DARK_WAKE"]
    full_wakes = [e for e in events if e["type"] == "FULL_WAKE"]
    privacy_events = [e for e in events if e["type"] == "PRIVACY"]
    auth_events = [e for e in events if e["type"] == "AUTH"]
    anomalies = [e for e in events if e["is_anomaly"]]

    print("\n TOTAL SUMMARY:")
    print(f"  • Background Wakes (Dark Wake)  : {len(dark_wakes)} times")
    print(f"  • Full User Wakes               : {len(full_wakes)} times")
    print(f"  • MAC Address Refreshes (BLE)   : {len(privacy_events)} times")
    print(f"  • iCloud / Auth Checks          : {len(auth_events)} times")
    
    if anomalies:
        print(f"  • {RED}Suspicious Night Activity      : {len(anomalies)} events detected!{RESET}")
    else:
        print(f"  • {GREEN}Suspicious Night Activity      : No anomalies detected.{RESET}")

    print("\n EVENT TIMELINE (CHRONOLOGICAL):")
    print("-" * 65)
    for event in events:
        status_tag = f"{RED}[ANOMALY]{RESET}" if event["is_anomaly"] else f"{GREEN}[NORMAL]{RESET}"
        print(f"[{event['time']}] [{event['type']:<10}] {status_tag} {event['detail']}")
    print("="*65)

if __name__ == "__main__":
    raw_logs = run_log_command(hours_back=24)
    if raw_logs:
        parsed_events = parse_logs(raw_logs)
        generate_report(parsed_events)

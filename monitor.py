import time
import sqlite3
import subprocess


def get_memory_usage():
    with open("/proc/meminfo") as f:
        lines = f.readlines()

    mem_total = int(lines[0].split()[1])
    mem_available = int(lines[2].split()[1])

    used = mem_total - mem_available
    percent = (used / mem_total) * 100

    return round(percent, 2)


def get_cpu_usage():
    def read_cpu():
        with open("/proc/stat") as f:
            line = f.readline()
            values = list(map(int, line.split()[1:]))

            idle = values[3]
            total = sum(values)

            return idle, total

    idle1, total1 = read_cpu()
    time.sleep(1)
    idle2, total2 = read_cpu()

    idle_delta = idle2 - idle1
    total_delta = total2 - total1

    usage = 100 * (1 - idle_delta / total_delta)
    return round(usage, 2)


def get_disk_usage():
    result = subprocess.run(["df", "/"], capture_output=True, text=True)
    lines = result.stdout.split("\n")

    disk_line = lines[1].split()
    usage = disk_line[4]

    return float(usage.replace("%", ""))


def save_metrics(cpu, memory, disk):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            cpu REAL,
            memory REAL,
            disk REAL
        )
    """)

    cursor.execute("""
        INSERT INTO metrics (cpu, memory, disk)
        VALUES (?, ?, ?)
    """, (cpu, memory, disk))

    conn.commit()
    conn.close()
def save_alert(message, cpu, memory, disk):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            message TEXT,
            cpu REAL,
            memory REAL,
            disk REAL
        )
    """)

    cursor.execute("""
        INSERT INTO alerts (message, cpu, memory, disk)
        VALUES (?, ?, ?, ?)
    """, (message, cpu, memory, disk))

    conn.commit()
    conn.close()

last_cpu_alert = 0
last_memory_alert = 0
last_disk_alert = 0

COOLDOWN = 60

while True:
    cpu = get_cpu_usage()
    memory = get_memory_usage()
    disk = get_disk_usage()
    now = time.time()

    if cpu > 80 and (now - last_cpu_alert > COOLDOWN):
     msg = "CPU alta"
     print("peligro" , msg)
     save_alert(msg, cpu, memory, disk)
     last_cpu_alert = now

    if memory > 80 and (now - last_memory_alert > COOLDOWN):
     msg = "RAM alta"
     print("peligro", msg)
     save_alert(msg, cpu, memory, disk)
     last_memory_alert = now

    if disk > 80 and (now - last_disk_alert > COOLDOWN):
     msg = "Disco alto"
     print("peligro", msg)
     save_alert(msg, cpu, memory, disk)
     last_disk_alert = now

    print("CPU:", cpu, "%")
    print("RAM:", memory, "%")
    print("DISK:", disk, "%")
    print("-" * 30)


    save_metrics(cpu, memory, disk)

    time.sleep(10)

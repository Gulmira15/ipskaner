import psutil
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Ma'lumotlarni saqlash uchun ro'yxatlar
all_process_data = []
disk_data = []
memory_data = []  # YANGI: Xotiradagi joy ma'lumotlarini saqlash uchun ro'yxat
cpu_data = []     # YANGI: CPU ishlatish ma'lumotlarini saqlash uchun ro'yxat

# Disk yozish va o'qish ma'lumotlarini olish
def get_disk_io():
    disk_io = psutil.disk_io_counters()
    disk_data.append((disk_io.write_bytes, disk_io.read_bytes))

# Dastur nomi boyicha xotiradagi joy va CPU ishlatilish ma'lumotlarini olish
def get_process_info(process_name):
    try:
        process_id = None
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == process_name:
                process_id = proc.info['pid']
                break

        if process_id is None:
            return None, None

        process = psutil.Process(process_id)
        memory_info = process.memory_info()
        memory_usage_mb = memory_info.rss / (1024 * 1024)  # Convert bytes to megabytes
        cpu_percent = process.cpu_percent(interval=1)  # CPU usage in percent
        return memory_usage_mb, cpu_percent
    except psutil.NoSuchProcess:
        return None, None

# Dastur ma'lumotlarini kuzatishni boshlash
def start_monitor():
    global monitor_id
    monitor_id = root.after(1000, monitor_process)

# Dastur ma'lumotlarini to'xtatish
def stop_monitor():
    root.after_cancel(monitor_id)

# Dastur ma'lumotlarini kuzatish
def monitor_process():
    # Funktsiya joriy ishlashi
    process_name = entry.get().strip()
    if process_name:
        memory_usage, cpu_usage = get_process_info(process_name)
        if memory_usage is not None and cpu_usage is not None:
            all_process_data.append((memory_usage, cpu_usage))
            memory_data.append(memory_usage)  # YANGI: Xotiradagi joy ma'lumotlarini ro'yxatga qo'shish
            cpu_data.append(cpu_usage)        # YANGI: CPU ishlatish ma'lumotlarini ro'yxatga qo'shish
            ax[0].plot(memory_data, 'r-')
            ax[1].plot(cpu_data, 'b-')
            canvas.draw()
            result_label.config(text=f"Dastur xotiradagi joy: {memory_usage:.2f} MB\nDastur CPU ishlatilishi: {cpu_usage:.2f}%")
        else:
            result_label.config(text="Xatolik: Kiritilgan dastur nomi bo'yicha topa olmadim!")

    get_disk_io()
    disk_write_data = [data[0] for data in disk_data]
    disk_read_data = [data[1] for data in disk_data]
    ax[2].plot(disk_write_data, 'g-', label='Disk Yozish')
    ax[2].plot(disk_read_data, 'y-', label='Disk O\'qish')
    ax[2].legend()
    canvas.draw()

    # Keyingi monitor_process chaqirishini belgilash
    global monitor_id
    monitor_id = root.after(1000, monitor_process)

# Ma'lumotlarni saqlash
def save_data():
    with open('monitor_data.txt', 'w') as file:
        for process_data in all_process_data:
            file.write(f"Memory Usage: {process_data[0]} MB, CPU Usage: {process_data[1]}%\n")
        for disk_write, disk_read in disk_data:
            file.write(f"Disk Write: {disk_write} bytes, Disk Read: {disk_read} bytes\n")
    result_label.config(text="Ma'lumotlar faylga saqlandi: monitor_data.txt")

# Dastur GUI
root = tk.Tk()
root.title("Dastur ma'lumotlarini kuzatish")

label = tk.Label(root, text="dastur nomini kiriting")
label.pack()

entry = tk.Entry(root)
entry.pack()

button_start = tk.Button(root, text="boshlash", command=start_monitor)
button_start.pack()

button_stop = tk.Button(root, text="To'xtatish", command=stop_monitor)
button_stop.pack()

button_save = tk.Button(root, text="Saqlash", command=save_data)
button_save.pack()

result_label = tk.Label(root, text="")
result_label.pack()

# Grafiklar
fig, ax = plt.subplots(3, 1, sharex=True)
fig.suptitle('Dastur ma\'lumotlarini kuzatish', fontsize=16)  # Bosh sarlavha
ax[0].set_title('Xotiradagi Joy (MB)')
ax[0].set_ylabel('Joy (MB)')  # Y o'qi nomini o'zgartirish
ax[1].set_title('CPU Ishlatilishi')
ax[1].set_ylabel('Ishlatish %')  # Y o'qi nomini o'zgartirish
ax[1].set_xlabel('Vaqt')  # X o'qi nomini o'zgartirish
ax[2].set_title('Disk Yozish va O\'qish (Bytes)')
ax[2].set_ylabel('Yozish/O\'qish (Bytes)')  # Y o'qi nomini o'zgartirish
ax[2].set_xlabel('Vaqt')  # X o'qi nomini o'zgartirish

# Chiroyli qilish
for axes in ax:
    axes.grid(True, linestyle='--', color='green', linewidth=0.5)  # Qadriyatlar va chizmalar ustidan yorliqlar qo'shish
    axes.patch.set_facecolor('#f0f0f0')  # Oyna fonini o'zgartirish

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

root.mainloop()

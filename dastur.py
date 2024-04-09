import socket
import ipaddress
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import requests
import whois

class NetworkScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Scanner")

        self.root.configure(background='light blue')

        self.input_label = ttk.Label(root, text="IP Address yoki Domain kiriting:")
        self.input_label.grid(row=0, column=0, padx=10, pady=5)
        self.input_entry = ttk.Entry(root)
        self.input_entry.grid(row=0, column=1, padx=10, pady=5)

        self.port_start_label = ttk.Label(root, text="Start Port:")
        self.port_start_label.grid(row=1, column=0, padx=10, pady=5)
        self.port_start_entry = ttk.Entry(root)
        self.port_start_entry.grid(row=1, column=1, padx=10, pady=5)

        self.port_end_label = ttk.Label(root, text="End Port:")
        self.port_end_label.grid(row=2, column=0, padx=10, pady=5)
        self.port_end_entry = ttk.Entry(root)
        self.port_end_entry.grid(row=2, column=1, padx=10, pady=5)

        self.scan_button = ttk.Button(root, text="Scan", command=self.start_scan)
        self.scan_button.grid(row=3, column=1, padx=10, pady=5)

        self.save_button = ttk.Button(root, text="Save Results", command=self.save_results)
        self.save_button.grid(row=3, column=2, padx=10, pady=5)

        self.result_label = ttk.Label(root, text="Scan Results:")
        self.result_label.grid(row=4, column=0, columnspan=2, padx=10, pady=5)

        self.result_text = tk.Text(root, height=10, width=50)
        self.result_text.grid(row=5, column=0, columnspan=3, padx=10, pady=5)

    def start_scan(self):
        input_value = self.input_entry.get()
        start_port = int(self.port_start_entry.get())
        end_port = int(self.port_end_entry.get())

        if not input_value:
            messagebox.showerror("Error", "Please enter an IP address or domain name")
            return

        self.result_text.delete('1.0', tk.END)

        ip_info = None
        domain_info = None

        try:
            ip_address = ipaddress.ip_address(input_value)
            self.scan_ip(ip_address, start_port, end_port)
            ip_info = self.get_ip_info(ip_address)
        except ValueError:
            ip_address = self.resolve_domain(input_value)
            if ip_address:
                self.scan_ip(ip_address, start_port, end_port)
                ip_info = self.get_ip_info(ip_address)
            else:
                self.scan_domain(input_value, start_port, end_port)
                domain_info = self.get_domain_info(input_value)

        self.display_info(ip_info, domain_info)

    def scan_ip(self, ip_address, start_port, end_port):
        self.result_text.insert(tk.END, f"Scanning IP: {ip_address}\n\n")

        open_ports = self.scan_ports(ip_address, start_port, end_port)
        self.display_results({ip_address: open_ports})

    def scan_domain(self, domain, start_port, end_port):
        self.result_text.insert(tk.END, f"Scanning domain: {domain}\n\n")

        ip_addresses = self.resolve_domain(domain)
        if ip_addresses:
            self.result_text.insert(tk.END, f"\nResolved IP addresses for domain '{domain}':\n")
            for ip in ip_addresses:
                self.result_text.insert(tk.END, f"{ip}\n")
                self.result_text.insert(tk.END, f"Scanning IP: {ip}\n\n")
                open_ports = self.scan_ports(ip, start_port, end_port)
                self.display_results({ip: open_ports})
        else:
            self.result_text.insert(tk.END, f"No IP addresses found for domain '{domain}'\n")

    def scan_ports(self, ip, start_port, end_port):
        open_ports = []
        for port in range(start_port, end_port + 1):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1)
            result = sock.connect_ex((str(ip), port))
            if result == 0:
                open_ports.append(port)
            sock.close()
        return open_ports

    def get_ip_info(self, ip_address):
        token = "fc3acbdc6ccb01"  # Your token here
        url = f"https://ipinfo.io/{ip_address}/json?token={token}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def resolve_domain(self, domain):
        try:
            ip_address = socket.gethostbyname(domain)
            return ip_address
        except socket.gaierror:
            return None

    def get_domain_info(self, domain):
        try:
            w = whois.whois(domain)
            return w
        except whois.parser.PywhoisError:
            return None

    def display_results(self, results):
        for ip, open_ports in results.items():
            if open_ports:
                self.result_text.insert(tk.END, f"IP: {ip}\n")
                for port in open_ports:
                    self.result_text.insert(tk.END, f"\tPort {port}: Open\n")
                self.result_text.insert(tk.END, "\n")
            else:
                self.result_text.insert(tk.END, f"IP: {ip} - No open ports found\n\n")

    def display_info(self, ip_info, domain_info):
        if ip_info:
            self.result_text.insert(tk.END, f"\n\nIP Info:\n")
            for key, value in ip_info.items():
                self.result_text.insert(tk.END, f"{key}: {value}\n")
        elif domain_info:
            for key, value in domain_info.items():
                self.result_text.insert(tk.END, f"{key}: {value}\n")
        else:
            self.result_text.insert(tk.END, f"No information available for the input\n")

    def save_results(self):
        save_path = "C:/Users/Shodmonbek/Desktop/ip/ip_domen_results.txt"
        with open(save_path, "w") as file:
            file.write(self.result_text.get("1.0", tk.END))

        messagebox.showinfo("Success", "Results have been saved successfully.")

def main():
    root = tk.Tk()
    app = NetworkScannerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

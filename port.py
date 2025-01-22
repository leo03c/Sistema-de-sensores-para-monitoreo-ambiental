import serial.tools.list_ports

def is_arduino(port_info):
    # Listado de VID:PID comunes para dispositivos Arduino
    arduino_vid_pid = [
        (0x2341, 0x0043),  # Arduino Uno (VID:PID oficial)
        (0x2341, 0x0001),  # Arduino Uno (antiguo)
        (0x2341, 0x0243),  # Arduino Mega 2560 R3
        (0x1A86, 0x7523),  # CH340 (clones de Arduino)
        (0x10C4, 0xEA60),  # CP2102 (clones de Arduino)
        (0x2341, 0x0210),  # Arduino Leonardo
    ]
    return (port_info.vid, port_info.pid) in arduino_vid_pid

ports = serial.tools.list_ports.comports()
for port in ports:
    print(f"Port: {port.device}")
    print(f"Description: {port.description}")
    print(f"Hardware ID: {port.hwid}")
    print(f"Manufacturer: {port.manufacturer}")
    print(f"Product: {port.product}")
    print(f"Serial Number: {port.serial_number}")
    print(f"Location: {port.location}")
    print(f"VID:PID: {port.vid}:{port.pid}" if port.vid and port.pid else "VID:PID: N/A")
    print(f"Interface: {port.interface}")
    
    # Identificar si es un Arduino
    if is_arduino(port):
        print("-> Este dispositivo parece ser un Arduino.")
    else:
        print("-> Este dispositivo no parece ser un Arduino.")
    print("-" * 40)

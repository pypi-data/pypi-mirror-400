import serial.tools.list_ports

def scan():
    """
    Scans for connected micro:bits.
    Returns a list of dictionaries containing: 'port', 'serial_number', 'description'
    """
    found_devices = []
    ports = serial.tools.list_ports.comports()
    
    for port in ports:
        # 1. check for the specific micro:bit Vendor ID (3368)
        # 2. keep the string check as a backup for other OSs
        p_str = (str(port.description) + str(port.hwid)).lower()
        
        if port.vid == 3368 or "microbit" in p_str or "mbed" in p_str:
            device_info = {
                "port": port.device,
                "serial_number": port.serial_number,
                "description": port.description
            }
            found_devices.append(device_info)
            
    return found_devices

def find(interactive=True):
    devices = scan()
    
    selected = None
    
    if len(devices) == 0:
        return None
    
    elif len(devices) == 1:
        selected = devices[0]
        
    else:
        # Multiple found
        if not interactive:
            selected = devices[0]
        else:
            print(f"\n⚠️  Found {len(devices)} micro:bits:")
            for i, dev in enumerate(devices):
                # Show Serial number to help user choose, but don't return it
                print(f"   [{i}] Port: {dev['port']} | Serial: {dev['serial_number']}")
            
            while True:
                selection = input("\n   Select device number (0-9): ")
                try:
                    index = int(selection)
                    if 0 <= index < len(devices):
                        selected = devices[index]
                        break
                    print("   ❌ Number out of range.")
                except ValueError:
                    print("   ❌ Invalid input.")

    # --- THE MAGIC CHANGE ---
    # Instead of returning the whole dict, we just return the port string
    return selected['port']


import sys
import subprocess
import hashlib
import platform
import socket

def _hash(value):
    if not value:
        return ""
    normalized = value.strip().lower().encode('utf-8')
    return hashlib.sha256(normalized).hexdigest()

def _run_cmd(cmd):
    try:
        if sys.platform == "win32":
            # shell=True sometimes needed for wmic on windows or internal cmds
            # but usually list of args avoids shell injection
            output = subprocess.check_output(cmd, shell=True).decode().strip()
            return output
        else:
            output = subprocess.check_output(cmd, shell=True).decode().strip()
            return output
    except Exception:
        return None

def _get_mobo_uuid():
    try:
        if sys.platform == "win32":
            out = _run_cmd("wmic csproduct get uuid")
            # Output format:
            # UUID
            # XXXXX-XXXX
            if out:
                lines = out.splitlines()
                for line in lines:
                    clean = line.strip()
                    if clean and clean.lower() != 'uuid':
                        return clean
        elif sys.platform == "darwin":
            # macOS
            cmd = "ioreg -rd1 -c IOPlatformExpertDevice | awk '/IOPlatformUUID/ { split($0, line, \"\\\"\"); printf \"%s\\n\", line[4]; }'"
            return _run_cmd(cmd)
        elif sys.platform.startswith("linux"):
            # Try /sys/class/dmi/id/product_uuid
            try:
                with open("/sys/class/dmi/id/product_uuid", "r") as f:
                    return f.read().strip()
            except:
                pass
            # Fallback
            return _run_cmd("cat /etc/machine-id")
    except:
        pass
    return "UNKNOWN-UUID"

def _get_disk_serial():
    try:
        if sys.platform == "win32":
            out = _run_cmd("wmic diskdrive get serialnumber")
            if out:
                lines = out.splitlines()
                # Get first non-empty line after header
                for line in lines[1:]:
                    if line.strip():
                        return line.strip()
        elif sys.platform == "darwin":
            # system_profiler SPStorageDataType ? 
            return "UNKNOWN-DISK" # macOS disk serial via command line is tricky without root sometimes
        elif sys.platform.startswith("linux"):
            # lsblk -d -n -o SERIAL
            out = _run_cmd("lsblk -d -n -o SERIAL | head -n 1")
            if out: return out
    except:
        pass
    return "UNKNOWN-DISK"

def _get_cpu_model():
    try:
        return platform.processor() or "UNKNOWN-CPU"
    except:
        pass
    return "UNKNOWN-CPU"
    
def _get_mac_address():
    try:
        import uuid
        mac = uuid.getnode()
        return ':'.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2))
    except:
        return "UNKNOWN-MAC"

def _get_hostname():
    try:
        name = socket.gethostname()
        if name and name.lower() != 'localhost': return name
    except: pass
    
    try:
        name = platform.node()
        if name: return name
    except: pass
    
    # Fallback to shell command (reliable on Kali/Linux/Mac)
    if sys.platform != "win32":
        try:
            return _run_cmd("hostname")
        except: pass
        
    return "UNKNOWN-HOST"

def get_device_fingerprint():
    return {
        "motherboardUuid": _hash(_get_mobo_uuid()),
        "diskSerial": _hash(_get_disk_serial()),
        "cpuModel": _hash(_get_cpu_model()),
        "macAddress": _hash(_get_mac_address()),
        "isVm": False, # TODO: Implement VM check if needed, e.g. check CPU flags
        "hostname": _get_hostname()
    }

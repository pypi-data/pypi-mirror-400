import machine
import utime
import struct
import uasyncio

# Configuration object storing metadata for each register
REGISTER_CONFIG = {
    "inverter_status": {"addr": 0, "qty": 1, "unit": 1},
    "Ppv": {"addr": 1, "qty": 2, "unit": 0.1},
    "Vpv1": {"addr": 3, "qty": 1, "unit": 0.1},
    "PV1Curr": {"addr": 4, "qty": 1, "unit": 0.1},
    "Ppv1": {"addr": 5, "qty": 2, "unit": 0.1},
    "Pac": {"addr": 35, "qty": 2, "unit": 0.1},
    "Fac": {"addr": 37, "qty": 1, "unit": 0.01},
    "Vac1": {"addr": 38, "qty": 1, "unit": 0.1},
    "Iac1": {"addr": 39, "qty": 1, "unit": 0.1},
    "Pac1": {"addr": 40, "qty": 2, "unit": 0.1},
    "Vac2": {"addr": 42, "qty": 1, "unit": 0.1},
    "Iac2": {"addr": 43, "qty": 1, "unit": 0.1},
    "Pac2": {"addr": 44, "qty": 2, "unit": 0.1},
    "Vac3": {"addr": 46, "qty": 1, "unit": 0.1},
    "Iac3": {"addr": 47, "qty": 1, "unit": 0.1},
    "Pac3": {"addr": 48, "qty": 2, "unit": 0.1},
    "Vac_RS": {"addr": 50, "qty": 1, "unit": 0.1},
    "Vac_ST": {"addr": 51, "qty": 1, "unit": 0.1},
    "Vac_TR": {"addr": 52, "qty": 1, "unit": 0.1},
    "Eac_today": {"addr": 53, "qty": 2, "unit": 0.1},
    "Eac_total": {"addr": 55, "qty": 2, "unit": 0.1},
    "Time_total": {"addr": 57, "qty": 2, "unit": 0.5},
    "Epv1_today": {"addr": 59, "qty": 2, "unit": 0.1},
    "Epv1_total": {"addr": 61, "qty": 2, "unit": 0.1},
    "Epv_total": {"addr": 91, "qty": 2, "unit": 0.1},
    "Temp1": {"addr": 93, "qty": 1, "unit": 0.1},
    "RealOPPercent": {"addr": 101, "qty": 1, "unit": 1},
    "FaultMaincode": {"addr": 105, "qty": 1, "unit": 1},
    "Pdischarge1": {"addr": 1009, "qty": 2, "unit": 0.1},
    "Pcharge1": {"addr": 1011, "qty": 2, "unit": 0.1},
    "Vbat": {"addr": 1013, "qty": 1, "unit": 0.1},
    "SOC": {"addr": 1014, "qty": 1, "unit": 1},
    "PactouserTotal": {"addr": 1021, "qty": 2, "unit": 0.1},
    "Pac_to_grid": {"addr": 1023, "qty": 2, "unit": 0.1},
    "Pactogrid_total": {"addr": 1029, "qty": 2, "unit": 0.1},
    "BatteryTemperature": {"addr": 1040, "qty": 1, "unit": 0.1},
    "Etouser_today": {"addr": 1044, "qty": 2, "unit": 0.1},
    "Etouser_total": {"addr": 1046, "qty": 2, "unit": 0.1},
    "Etogrid_today": {"addr": 1048, "qty": 2, "unit": 0.1},
    "Etogrid_total": {"addr": 1050, "qty": 2, "unit": 0.1},
    "Edischarge1_today": {"addr": 1052, "qty": 2, "unit": 0.1},
    "Edischarge1_total": {"addr": 1054, "qty": 2, "unit": 0.1},
    "Echarge1_today": {"addr": 1056, "qty": 2, "unit": 0.1},
    "Echarge1_total": {"addr": 1058, "qty": 2, "unit": 0.1},
    "ELocalLoad_Today": {"addr": 1060, "qty": 2, "unit": 0.1},
    "ELocalLoad_Total": {"addr": 1062, "qty": 2, "unit": 0.1},
    "ACCharge_today": {"addr": 1124, "qty": 2, "unit": 1},
    "ACChargePower": {"addr": 1128, "qty": 2, "unit": 1},
    "Esystem_today": {"addr": 1137, "qty": 2, "unit": 0.1},
    "Esystem_total": {"addr": 1139, "qty": 2, "unit": 0.1},
    "Eself_today": {"addr": 1141, "qty": 2, "unit": 0.1},
    "Eself_total": {"addr": 1143, "qty": 2, "unit": 0.1},
    "PSystem": {"addr": 1145, "qty": 2, "unit": 0.1},
    "PSelf": {"addr": 1147, "qty": 2, "unit": 0.1},
}


# Generic function for reading specific value
async def read_variable(name):
    config = REGISTER_CONFIG.get(name)
    if not config:
        raise ValueError(f"Variable {name} not found in configuration.")

    regs = await read_input_registers(config["addr"], config["qty"])

    if not regs:
        raise Exception(f"Failed reading {name} at address {config['addr']}")

    # combine if values takes up 2 registers
    if (config["qty"] == 2):
        raw_val = combine_high_low(regs[0], regs[1])
    else:
        raw_val = regs[0]

    return raw_val * config["unit"]


# -------------------------------------------------
# --- Individual Getters with Full Descriptions ---
# -------------------------------------------------

# Inverter Status: Inverter run state (0:waiting, 1:normal, 3:fault)
async def get_inverter_status(): return await read_variable("inverter_status")


# Ppv: Input power
async def get_Ppv(): return await read_variable("Ppv")


# Vpv1: PV1 voltage
async def get_Vpv1(): return await read_variable("Vpv1")


# PV1Curr: PV1 input current
async def get_PV1Curr(): return await read_variable("PV1Curr")


# Ppv1: PV1 input power
async def get_Ppv1(): return await read_variable("Ppv1")


# Pac: Output power
async def get_Pac(): return await read_variable("Pac")


# Fac: Grid frequency
async def get_Fac(): return await read_variable("Fac")


# Vac1: Three/single phase grid voltage
async def get_Vac1(): return await read_variable("Vac1")


# Iac1: Three/single phase grid output current
async def get_Iac1(): return await read_variable("Iac1")


# Pac1: Three/single phase grid output watt VA
async def get_Pac1(): return await read_variable("Pac1")


# Vac2: Three phase grid voltage
async def get_Vac2(): return await read_variable("Vac2")


# Iac2: Three phase grid output current
async def get_Iac2(): return await read_variable("Iac2")


# Pac2: Three phase grid output power
async def get_Pac2(): return await read_variable("Pac2")


# Vac3: Three phase grid voltage
async def get_Vac3(): return await read_variable("Vac3")


# Iac3: Three phase grid output current
async def get_Iac3(): return await read_variable("Iac3")


# Pac3: Three phase grid output power
async def get_Pac3(): return await read_variable("Pac3")


# Vac RS: Three phase grid voltage (Line voltage)
async def get_Vac_RS(): return await read_variable("Vac_RS")


# Vac ST: Three phase grid voltage (Line voltage)
async def get_Vac_ST(): return await read_variable("Vac_ST")


# Vac TR: Three phase grid voltage (Line voltage)
async def get_Vac_TR(): return await read_variable("Vac_TR")


# Eac today: Today generate energy
async def get_Eac_today(): return await read_variable("Eac_today")


# Eac total: Total generate energy
async def get_Eac_total(): return await read_variable("Eac_total")


# Time total: Work time total
async def get_Time_total(): return await read_variable("Time_total")


# Epv1_today: PV1 Energy today
async def get_Epv1_today(): return await read_variable("Epv1_today")


# Epv1_total: PV1 Energy total
async def get_Epv1_total(): return await read_variable("Epv1_total")


# Epv_total: PV Energy total
async def get_Epv_total(): return await read_variable("Epv_total")


# Temp1: Inverter temperature
async def get_Temp1(): return await read_variable("Temp1")


# RealOPPercent: Real Output power Percent
async def get_RealOPPercent(): return await read_variable("RealOPPercent")


# Fault Maincode: Inverter fault maincode
async def get_FaultMaincode(): return await read_variable("FaultMaincode")


# Pdischarge1: Discharge power
async def get_Pdischarge1(): return await read_variable("Pdischarge1")


# Pcharge1: Charge power
async def get_Pcharge1(): return await read_variable("Pcharge1")


# Vbat: Battery voltage
async def get_Vbat(): return await read_variable("Vbat")


# SOC: State of charge Capacity
async def get_SOC(): return await read_variable("SOC")


# PactouserTotal: AC power to user total
async def get_PactouserTotal(): return await read_variable("PactouserTotal")


# Pac to grid: AC power to grid
async def get_Pac_to_grid(): return await read_variable("Pac_to_grid")


# Pactogrid total: AC power to grid total
async def get_Pactogrid_total(): return await read_variable("Pactogrid_total")


# Battery Temperature: Battery Temperature
async def get_BatteryTemperature(): return await read_variable("BatteryTemperature")


# Etouser_today: Energy to user today
async def get_Etouser_today(): return await read_variable("Etouser_today")


# Etouser_total: Energy to user total
async def get_Etouser_total(): return await read_variable("Etouser_total")


# Etogrid_today: Energy to grid today
async def get_Etogrid_today(): return await read_variable("Etogrid_today")


# Etogrid_total: Energy to grid total
async def get_Etogrid_total(): return await read_variable("Etogrid_total")


# Edischarge1_today: Discharge energy1 today
async def get_Edischarge1_today(): return await read_variable("Edischarge1_today")


# Edischarge1_total: Total discharge energy1
async def get_Edischarge1_total(): return await read_variable("Edischarge1_total")


# Echarge1_today: Charge1 energy today
async def get_Echarge1_today(): return await read_variable("Echarge1_today")


# Echarge1_total: Charge1 energy total
async def get_Echarge1_total(): return await read_variable("Echarge1_total")


# ELocalLoad_Today: Local load energy today [cite: 146]
async def get_ELocalLoad_Today(): return await read_variable("ELocalLoad_Today")


# ELocalLoad_Total: Local load energy total [cite: 146]
async def get_ELocalLoad_Total(): return await read_variable("ELocalLoad_Total")


# AC Charge Energy today: AC Charge Energy today [cite: 163]
async def get_ACCharge_today(): return await read_variable("ACCharge_today")


# AC Charge Power: AC Charge Power [cite: 181]
async def get_ACChargePower(): return await read_variable("ACChargePower")


# Esystem_today: System electric energy today [cite: 216]
async def get_Esystem_today(): return await read_variable("Esystem_today")


# Esystem_total: System electric energy total
async def get_Esystem_total(): return await read_variable("Esystem_total")


# Eself_today: self electric energy today
async def get_Eself_today(): return await read_variable("Eself_today")


# Eself_total: self electric energy total
async def get_Eself_total(): return await read_variable("Eself_total")


# PSystem: System power
async def get_PSystem(): return await read_variable("PSystem")


# PSelf: self power
async def get_PSelf(): return await read_variable("PSelf")


# Get object of all available values
async def get_all():
    results = {}

    for name in REGISTER_CONFIG.keys():
        # Construct the function name string
        func_name = f"get_{name}"
        if func_name in globals():
            element_value = await globals()[func_name]()
            element_to_add = {name: element_value}
            results.update(element_to_add)
        else:
            raise Exception(f"Warning: {func_name} not implemented.")

    return results

# -------------------------------------------------
#               UART COMMUNICATION
# -------------------------------------------------

# async defAULT CONFIGURATION
UART_ID = 0
TX_PIN = 0
RX_PIN = 1
CTRL_PIN = 2  # (DE/RE pin for RS485)
BAUD_RATE = 9600
SLAVE_ADDR = 1

#   -----  CHANGE COMMUNICATION SETTINGS -----
def set_tx_pin(pin_number):
    global TX_PIN
    TX_PIN = pin_number

def set_rx_pin(pin_number):
    global RX_PIN
    RX_PIN = pin_number

def set_ctrl_pin(pin_number):
    global CTRL_PIN
    CTRL_PIN = pin_number

def set_slave_address(address):
    if address < 1 or address > 255:
        raise Exception("Modbus slave address must be between 1 and 255.")
    global SLAVE_ADDR
    SLAVE_ADDR = address

# HARDWARE SETUP
uart = machine.UART(UART_ID, baudrate=BAUD_RATE, tx=machine.Pin(TX_PIN), rx=machine.Pin(RX_PIN), bits=8, parity=None, stop=1)
ctrl = machine.Pin(CTRL_PIN, machine.Pin.OUT)
ctrl.value(0)  # Start in Receive mode

def calculate_crc(data):
    crc = 0xFFFF
    for char in data:
        crc ^= char
        for _ in range(8):
            if crc & 1:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    # Swap bytes for Modbus (Low Byte first)
    return struct.pack('<H', crc)

# Sends a Modbus RTU request frame
async def send_modbus_request(slave_id, function_code, start_addr, quantity):
    # Frame: Slave ID (1B) + Func (1B) + Addr (2B) + Qty (2B) + CRC (2B)
    payload = struct.pack('>BBHH', slave_id, function_code, start_addr, quantity)
    crc = calculate_crc(payload)
    request = payload + crc

    ctrl.value(1)  # Enable TX Mode (Set DE/RE High)
    await uasyncio.sleep_ms(10)

    uart.write(request)  # send data

    wait_time = int((len(request) * 10 * 1000) / BAUD_RATE) + 2
    await uasyncio.sleep_ms(wait_time) # Wait for UART to finish sending before switching off DE pin

    ctrl.value(0)  # Enable RX Mode (Set DE/RE Low)


# Ready input registers (0x04)
# return await value: array of 16-bit values
async def read_input_registers(start_addr, quantity):
    # print(f"Reading {quantity} registers starting at {start_addr}...")

    await send_modbus_request(SLAVE_ADDR, 0x04, start_addr, quantity)

    expected_len = 3 + quantity + 2  # Response frame: slave_address(1) + function_number(1) + data_byte_count + Data(quantity) + CRC(2)

    start_time = utime.ticks_ms()
    timeout_ms = 1000  # 1 second max timeout

    while utime.ticks_diff(utime.ticks_ms(), start_time) < timeout_ms:
        if uart.any():
            await uasyncio.sleep_ms(10)
            response = uart.read()

            if not response or len(response) < expected_len:
                raise Exception("Response not complete")

            if response[0] != SLAVE_ADDR:
                raise Exception(f"Wrong Slave ID received. Received: {response[0]}")

            if response[1] != 0x04:
                raise Exception(f"Wrong function code received: {response[1]}")

            data_bytes = response[3:-2]  # Strip header and CRC

            # Convert to list of 16-bit integers
            registers = []
            for i in range(0, len(data_bytes), 2):
                val = struct.unpack('>H', data_bytes[i:i + 2])[0]  # convert two elements in Big Endian to unsigned 16-bit integer
                registers.append(val)

            return registers

    raise TimeoutError

def combine_high_low(high, low):
    return (high << 16) | low
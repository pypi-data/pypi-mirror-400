## Growatt pico reader
Micropython library for reading data from Growatt inverter using RS485 port.
Library is build for Raspberry pi pico / pico w and RS485 to TTL module.

## Installation
### 1. Using PyPi package (recommended)
 In Thonny IDE go to Tools -> Manage Packages and search for `growatt_pico_reader`
### 2. Copy python file
 Copy `growatt_pico_reader/growatt_pico_reader_py` file to your root directory on pi pico.

## Usage
### Import package
```python
from growatt_pico_reader import *
```
### Initial setup (not required)
```python
set_tx_pin(pin_number) # change TX port (default is 0)
set_rx_pin(pin_number) # change RX port (default is 1)
set_ctrl_pin(pin_number) # change RS485 transceiver control pin (default is 1)
set_slave_address(address) # change growatt address (default is 1) (address can be set on inverter LCD display)
```

### Read data
#### Read All Data:
```python
all_data = get_all()
print(all_data)
```

#### Read specific data:
```python
grid_frequency = get_Fac()
print(grid_frequency)
```

#### All available data to read: 
| Register Address | Variable Short         | Description                            | Unit | Function Call            | Note                         |
| ---------------- | ---------------------- | -------------------------------------- | ---- | ------------------------ | ---------------------------- |
| 0                | Inverter Status        | Inverter run state                     | \-   | get_inverter_status()    | 0:waiting, 1:normal, 3:fault |
| 1-2              | Ppv                    | Input power                            | W    | get_Ppv()                |                              |
| 3                | Vpv1                   | PV1 voltage                            | V    | get_Vpv1()               |                              |
| 4                | PV1Curr                | PV1 input current                      | A    | get_PV1Curr()            |                              |
| 5-6              | Ppv1                   | PV1 input power                        | W    | get_Ppv1()               |                              |
| 35-36            | Pac                    | Output power                           | W    | get_Pac()                |                              |
| 37               | Fac                    | Grid frequency                         | Hz   | get_Fac()                |                              |
| 38               | Vac1                   | Three/single phase grid voltage        | V    | get_Vac1()               |                              |
| 39               | Iac1                   | Three/single phase grid output current | A    | get_Iac1()               |                              |
| 40-41            | Pac1                   | Three/single phase grid output watt VA | VA   | get_Pac1()               |                              |
| 42               | Vac2                   | Three phase grid voltage               | V    | get_Vac2()               |                              |
| 43               | Iac2                   | Three phase grid output current        | A    | get_Iac2()               |                              |
| 44-45            | Pac2                   | Three phase grid output power          | VA   | get_Pac2()               |                              |
| 46               | Vac3                   | Three phase grid voltage               | V    | get_Vac3()               |                              |
| 47               | Iac3                   | Three phase grid output current        | A    | get_Iac3()               |                              |
| 48-49            | Pac3                   | Three phase grid output power          | VA   | get_Pac3()               |                              |
| 50               | Vac RS                 | Three phase grid voltage               | V    | get_Vac_RS()             |                              |
| 51               | Vac ST                 | Three phase grid voltage               | V    | get_Vac_ST()             |                              |
| 52               | Vac TR                 | Three phase grid voltage               | V    | get_Vac_TR()             |                              |
| 53-54            | Eac today              | Today generate energy                  | kWh  | get_Eac_today()          |                              |
| 55-56            | Eac total              | Total generate energy                  | kWh  | get_Eac_total()          |                              |
| 57-58            | Time total             | Work time total                        | s    | get_Time_total()         |                              |
| 59-60            | Epv1_today             | PV1Energy today                        | kWh  | get_Epv1_today()         |                              |
| 61-62            | Epv1_total             | PV1Energy total                        | kWh  | get_Epv1_total()         |                              |
| 91-92            | Epv_total              | PV Energy total                        | kWh  | get_Epv_total()          |                              |
| 93               | Temp1                  | Inverter temperature                   | °C   | get_Temp1()              |                              |
| 101              | RealOPPercent          | Real Output power Percent              | %    | get_RealOPPercent()      |                              |
| 105              | Fault Maincode         | Inverter fault maincode                | \-   | get_FaultMaincode()      |                              |
| 1009-1010        | Pdischarge1            | Discharge power                        | W    | get_Pdischarge1()        |                              |
| 1011-1012        | Pcharge1               | Charge power                           | W    | get_Pcharge1()           |                              |
| 1013             | Vbat                   | Battery voltage                        | V    | get_Vbat()               |                              |
| 1014             | SOC                    | State of charge Capacity               | %    | get_SOC()                |                              |
| 1021-1022        | PactouserTotal         | AC power to user total                 | W    | get_PactouserTotal()     |                              |
| 1023-1024        | Pac to grid            | AC power to grid                       | W    | get_Pac_to_grid()        |                              |
| 1029-1030        | Pactogrid total        | AC power to grid total                 | W    | get_Pactogrid_total()    |                              |
| 1040             | Battery Temperature    | Battery Temperature                    | °C   | get_BatteryTemperature() |                              |
| 1044-1045        | Etouser_today          | Energy to user today                   | kWh  | get_Etouser_today()      |                              |
| 1046-1047        | Etouser_total          | Energy to user total                   | kWh  | get_Etouser_total()      |                              |
| 1048-1049        | Etogrid_today          | Energy to grid today                   | kWh  | get_Etogrid_today()      |                              |
| 1050-1051        | Etogrid_total          | Energy to grid total                   | kWh  | get_Etogrid_total()      |                              |
| 1052-1053        | Edischarge1_today      | Discharge energy1 today                | kWh  | get_Edischarge1_today()  |                              |
| 1054-1055        | Edischarge1_total      | Total discharge energy1                | kWh  | get_Edischarge1_total()  |                              |
| 1056-1057        | Echarge1_today         | Charge1 energy today                   | kWh  | get_Echarge1_today()     |                              |
| 1058-1059        | Echarge1_total         | Charge1 energy total                   | kWh  | get_Echarge1_total()     |                              |
| 1060-1061        | ELocalLoad_Today       | Local load energy today                | kWh  | get_ELocalLoad_Today()   |                              |
| 1062-1063        | ELocalLoad_Total       | Local load energy total                | kWh  | get_ELocalLoad_Total()   |                              |
| 1124-1125        | AC Charge Energy today | AC Charge Energy today                 | kWh  | get_ACCharge_today()     |                              |
| 1128-1129        | AC Charge Power        | AC Charge Power                        | W    | get_ACChargePower()      |                              |
| 1137-1138        | Esystem_today          | System electric energy today           | kWh  | get_Esystem_today()      |                              |
| 1139-1140        | Esystem_total          | System electric energy total           | kWh  | get_Esystem_total()      |                              |
| 1141-1142        | Eself_today            | self electric energy today             | kWh  | get_Eself_today()        |                              |
| 1143-1144        | Eself_total            | self electric energy total             | kWh  | get_Eself_total()        |                              |
| 1145-1146        | PSystem                | System power                           | W    | get_PSystem()            |                              |
| 1147-1148        | PSelf                  | self power                             | W    | get_PSelf()              |                              |

## Example Hardware Setup
On growatt inverter on LCD display set RS485 mode to VPP. Pins 5 (modbus A) and 4 (modbus B) are used on RJ45 connector.

<img src="assets/circuit_image.png" height="300"/>
<img src="assets/physical_connection.jpg" height="250"/>
<img src="assets/rs485_port.jpg" height="250"/>


### Used resources:
- For parsing data was used this document: [Growatt-Inverter-Modbus-RTU-Protocol-II-V1-24-English-new.pdf](https://github.com/johanmeijer/grott/blob/master/documentatie/Growatt-Inverter-Modbus-RTU-Protocol-II-V1-24-English-new.pdf)
- Base functionality was inspired from [TheTrueRandom/growatt-modbus](https://github.com/TheTrueRandom/growatt-modbus/tree/master)

## License and contributing
Project is licensed under MIT license. 
Feel free to open a PR for new features (e.g. more parsed data)
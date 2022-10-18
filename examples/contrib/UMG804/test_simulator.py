#!/usr/bin/env python3
"""Test simulator.

"""
import struct
from time import sleep

from pymodbus.client import ModbusTcpClient
from pymodbus.transaction import ModbusSocketFramer


def build_int32_from_registers(registers):
        """Build registers from int32 or float32"""
        value_bytes = int.to_bytes(registers[0], 2, 'big') + int.to_bytes(
            registers[1], 2, 'big'
        )
        return int.from_bytes(value_bytes, 'big')

def build_float32_from_registers(registers):
        """Build registers from int32 or float32"""
        value_bytes = int.to_bytes(registers[0], 2, 'big') + int.to_bytes(
            registers[1], 2, 'big'
        )
        return struct.unpack("f", value_bytes)[0]


def modbus_calls(client):
    """Execute modbus calls and print."""

    rr = client.read_input_registers(1, 2, slave=1)
    print(f"Serial number (register 1 & 2): {build_int32_from_registers(rr.registers)}")

    rr = client.read_input_registers(3, 1, slave=1)
    print(f"Boot loader version (register 3): {rr.registers[0]}")

    rr = client.read_holding_registers(6, 1, slave=1)
    print(f"Powerup counter (register 6): {rr.registers[0]}")

    rr = client.read_input_registers(7, 2, slave=1)
    print(f"Uptime  (register 7 & 8): {build_int32_from_registers(rr.registers)}")

    rr = client.read_input_registers(126, 2, slave=1)
    print(f"IP address (register 126 & 127): {build_int32_from_registers(rr.registers)}")

    rr = client.read_coils(144 * 16, 16, slave=1)
    print(f"DNS Switch Enabled (register 144 == bit 144 * 16): {rr.bits}")

    rr = client.read_input_registers(145, 1, slave=1)
    print(f"DNS Switch value (register 145): {rr.registers}")

    rr = client.read_holding_registers(190, 1, slave=1)
    print(f"Global CT Size (register 190): {rr.registers[0]}")

    rr = client.read_holding_registers(191, 1, slave=1)
    print(f"Global breaker Size (register 191): {rr.registers[0]}")

    rr = client.read_holding_registers(200, 95, slave=1)
    print(f"CT Size (register 200 -> 295): count={len(rr.registers)}")
    print(rr.registers)
    rr = client.read_holding_registers(296, 95, slave=1)
    print(f"Breaker Size (register 296 -> 391): count={len(rr.registers)}")
    print(rr.registers)

    rr = client.read_input_registers(4900, 2, slave=1)
    print(f"Frequency (register 4900 & 4901): {build_float32_from_registers(rr.registers)}")

    rr = client.read_holding_registers(109, 7, slave=1)
    print(f"Real Time Clock (register 109 -> 115): count={len(rr.registers)} {rr.registers}")


    rr = client.read_input_registers(29, 16, slave=1)
    txt = ''
    for x in rr.registers:
        txt += int.to_bytes(x, 2, 'big').decode('utf-8')
    print(f"Brand name (register 29 -> 44): <<{txt}>>")


def run_client():
    """Run sync client."""
    print("### Client starting")
    client = ModbusTcpClient("198.251.71.103", port=5020, framer=ModbusSocketFramer)
    # client = ModbusTcpClient("127.0.0.1", port=5020, framer=ModbusSocketFramer)
    client.connect()
    modbus_calls(client)
    client.close()
    print("### End of Program")


if __name__ == "__main__":
    run_client()

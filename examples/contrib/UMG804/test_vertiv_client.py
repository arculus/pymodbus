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

def modbus_calls(client):
    """Execute modbus calls and print."""

    rr = client.read_input_registers(30592, 2, slave=1)
    print(f"Output kW-Hrs (DFW18_120_RPP_A1-3->BREAKER #01) (register 30592 x2): {build_int32_from_registers(rr.registers)}")

    rr = client.read_input_registers(30591, 1, slave=1)
    print(f"Branch Output Power (W) (DFW18_120_RPP_A1-3->BREAKER #01) (register 30591): {rr.registers[0]}")

    rr = client.read_input_registers(31384, 2, slave=1)
    print(f"Output kW-Hrs (DFW18_120_RPP_A1-3->BREAKER #67) (register 31384 x2): {build_int32_from_registers(rr.registers)}")

    rr = client.read_input_registers(31383, 1, slave=1)
    print(f"Branch Output Power (W) (DFW18_120_RPP_A1-3->BREAKER #67) (register 31383): {rr.registers[0]}")


def run_client():
    """Run sync client."""
    print("### Client starting")
    client = ModbusTcpClient("198.251.71.103", port=5021, framer=ModbusSocketFramer)
    # client = ModbusTcpClient("127.0.0.1", port=5021, framer=ModbusSocketFramer)
    client.connect()
    modbus_calls(client)
    client.close()
    print("### End of Program")


if __name__ == "__main__":
    run_client()

#!/usr/bin/env python3
"""Vertiv RPP Simulator.

The setup configuration is below.
"""
import asyncio
import logging

from pymodbus import pymodbus_apply_logging_config
from pymodbus.datastore import ModbusServerContext, ModbusSimulatorContext
from pymodbus.server import StartAsyncTcpServer
from pymodbus.transaction import ModbusSocketFramer


_logger = logging.getLogger()


# ================================
# ===   DEVICE CONFIGURATION   ===
# ================================
PORT = 5021
vertiv_config = {
    "setup": {
        "co size": 50000,
        "di size": 50000,
        "hr size": 50000,
        "ir size": 50000,
        "shared blocks": True,
        "type exception": False,
        "defaults": {
            "value": {
                "bits": 0,
                "uint16": 0,
                "uint32": 0,
                "float32": 0.0,
                "string": " ",
            },
            "action": {
                "bits": None,
                "uint16": "register",
                "uint32": "register",
                "float32": "register",
                "string": None,
            },
        },
    },
    "invalid": [
        [0,10064],
        [10072, 10132],
        [11215, 15506],
        [15512, 30462],
        [30491, 30586],
        [30596, 30598],
        [35900, 39997],
        [40000, 40477],
        [40480, 45899],
        [45901, 49997],
    ],
    "write": [
        [45478, 45479],
        45900,
        [49998, 49999],
    ],
    "bits": [
    ],
    "uint16": [
        [10065, 10071],
        [10133, 11214],
        [15507, 15511],
        [30463, 30490],
        [30587, 30591],
        [30594, 30595],
        35899,
        45900,

    ],
    "uint32": [
        30592,
        39998,
        40478,
        49998,
    ],
    "float32": [
    ],
    "string": [
    ],
    "repeat": [
        {"addr": [30587, 30598], "to": [30599, 31594]},
    ],
}


# Missing actions:
#  uptime() in seconds
def vertiv_reset(_registers, _inx, _cell):
    """Test action."""


# =======================================
# ===   END OF DEVICE CONFIGURATION   ===
# =======================================


async def run_vertiv_simulator():
    """Run server."""
    pymodbus_apply_logging_config()
    _logger.setLevel("DEBUG")
    _logger.info("### start Vertiv RPP simulator")

    vertiv_actions = {
        "vertiv_reset": vertiv_reset,
    }
    datastore = ModbusSimulatorContext(vertiv_config, vertiv_actions)
    context = ModbusServerContext(slaves=datastore, single=True)
    await StartAsyncTcpServer(
        context=context,
        address=("", PORT),
        framer=ModbusSocketFramer,
        allow_reuse_address=True,
    )
    _logger.info("### stop Vertiv RPP simulator")


if __name__ == "__main__":
    asyncio.run(run_vertiv_simulator(), debug=True)

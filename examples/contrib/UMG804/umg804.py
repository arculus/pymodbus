#!/usr/bin/env python3
"""UMG804 Simulator.

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
PORT = 5020
umg804_config = {
    "setup": {
        "co size": 63000,
        "di size": 63000,
        "hr size": 63000,
        "ir size": 63000,
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
        [78, 99],
        [157, 189],
        [194, 199],
        [983, 999],
        [1022, 1099],
        [1104, 1197],
        1499,
        [1604, 1699],
        [1716, 1799],
        [2614, 4799],
        [4817, 4899],
        [4933, 4999],
    ],
    "write": [
        5,
        [61, 76],
        [100, 101],
        [109, 117],
        [120, 136],
        140,
        [147, 152],
        156,
        [190, 982],
        [1000, 1004],
        [1007, 1021],
        [1100, 1103],
        [1198, 1199],  # DOCUMENTED AS 1998, 1999 !!!
        [1206, 1306],
        [1307, 1402],
        [1800, 1929],
    ],
    "bits": [
        9,           # Bit 0 - 1
        77,          # bit 0
        [116, 119],  # bit 0
        136,         # bit 0
        {"addr": 144, "value": 0x01},
        149,         # Bit 0 - 1
        152,         # Bit 0 - 4
        [1198, 1199],  # DOCUMENTED AS 1998, 1999 !!!
        [1200, 1201],
        [1206, 1207],
        {"addr": [1208, 1306], "action": "random"},
        {"addr": [1307, 1402], "action": "random"},
        [1500, 1507],
        [1508, 1603],
    ],
    "uint16": [
        {"addr": 3, "value": 123, "action": None},
        {"addr": 4, "value": 101, "action": None},
        {"addr": 5, "value": 999, "action": None},
        {"addr": 6, "value": 11, "action": None},
        {"addr": 10, "value": 0, "action": None},
        {"addr": 11, "value": 1, "action": None},
        {"addr": 12, "value": 4, "action": None},
        {"addr": 13, "value": 0, "action": None},
        {"addr": [22, 25], "value": 56789, "action": None},
        {"addr": [26, 28], "value": 117, "action": None},
        {"addr": [100, 101], "action": None},
        {"addr": 102, "action": "timestamp"},
        {"addr": [103, 108], "action": None},
        {"addr": 109, "action": "timestamp"},
        {"addr": [110, 115], "action": None},
        {"addr": 137, "action": None},
        {"addr": [142, 143], "action": None},
        {"addr": [145, 148], "action": None},
        {"addr": [150, 151], "value": 1017, "action": None},
        {"addr": 153, "value": 31415, "action": None},
        {"addr": 156, "action": None},
        {"addr": [190, 191], "value": 2048, "action": None},
        {"addr": 192, "action": "umg804_reset"},
        {"addr": 193, "action": None},
        {"addr": [200, 295], "action": None},
        {"addr": [296, 391], "action": None},
        {"addr": [392, 487], "action": None},
        {"addr": [488, 583], "action": None},
        {"addr": [584, 679], "action": None},
        {"addr": [680, 775], "action": None},
        {"addr": [776, 871], "action": None},
        {"addr": [872, 967], "action": None},
        {"addr": [968, 982], "action": None},
        {"addr": [1000, 1006], "action": None},
        {"addr": [1007, 1021], "action": None},
        {"addr": [1100, 1103], "action": None},
        [1202, 1205],
        [1403, 1498],
        {"addr": 1700, "action": "increment"},
        {"addr": 1701, "action": "increment"},
        {"addr": 1702, "action": "timestamp"},
        {"addr": [1703, 1709], "action": None},
        {"addr": 1710, "value": 220, "action": None},
        {"addr": 1711, "value": 3, "action": None},
        {"addr": [1800, 1801], "action": None},
        {"addr": [1930, 1949], "action": None},
        {"addr": [1966, 1989], "action": None},
        {"addr": 4800, "value": 1, "action": None},
        {"addr": 4801, "value": 50, "action": None},
        {"addr": [4802, 4809], "value": 110, "action": None},
        {"addr": [4810, 4813], "value": 97, "action": None},
        {"addr": [4814, 4816], "value": 90, "action": None},
        {"addr": [5000, 5095], "value": 10, "action": None},
        {"addr": [5096, 5191], "value": 20, "action": None},
        {"addr": [5192, 5287], "value": 10, "action": None},
    ],
    "uint32": [
        {"addr": 1, "value": 123456789, "action": None},
        {"addr": 7, "action": "uptime"},
        {"addr": [14, 20], "value": 123456789, "action": None},
        {"addr": [120, 122], "value": 0, "action": "increment"},
        {"addr": [126, 134], "value": 1234, "action": None},
        {"addr": [138, 140], "value": 1, "action": None},
        {"addr": [1802, 1928], "action": None},
        {"addr": [1950, 1964], "action": None},
        {"addr": [1990, 2108], "action": None},
        {"addr": [5288, 5478], "value": 115, "action": "increment"},
        {"addr": [5480, 5670], "value": 55, "action": "increment"},
        {"addr": [5672, 5862], "value": 45, "action": "increment"},
        {"addr": [5864, 5958], "value": 2065, "action": "increment"},
        {"addr": [5960, 6054], "value": 33, "action": "increment"},
        {"addr": [6056, 6150], "value": 23, "action": "increment"},
    ],
    "float32": [
        {"addr": 154, "value": 3.141592, "action": None},
        {"addr": 1712, "value": 220.3, "action": None},
        {"addr": 1714, "value": 3.5, "action": None},
        {"addr": 4900, "value": 50.1, "action": None},
        {"addr": [4902, 4916], "value": 110, "action": None},
        {"addr": [4918, 4824], "value": 97, "action": None},
        {"addr": [4926, 4931], "value": 90, "action": None},
        {"addr": [10000, 10190], "value": 115.0, "action": "increment"},
        {"addr": [10192, 10382], "value": 55.0, "action": "increment"},
        {"addr": [10384, 10574], "value": 45.0, "action": "increment"},
        {"addr": [10576, 10766], "value": 2065.0, "action": "increment"},
        {"addr": [10768, 10958], "value": 33.0, "action": "increment"},
        {"addr": [10960, 11150], "value": 23.0, "action": "increment"},
    ],
    "string": [
        {"addr": [29, 44], "value": "Brand name, 32 bytes...........X"},
        {"addr": [45, 60], "value": "Model name, 32 bytes...........X"},
        {"addr": [61, 76], "value": "Device name, 32 bytes..........X"},
    ],
    "repeat": [
        {"addr": [1942, 2109], "to": [2110, 2613]}],
}


# Missing actions:
#  uptime() in seconds
def umg804_reset(_registers, _inx, _cell):
    """Test action."""


# =======================================
# ===   END OF DEVICE CONFIGURATION   ===
# =======================================


async def run_umg804_simulator():
    """Run server."""
    pymodbus_apply_logging_config()
    _logger.setLevel("DEBUG")
    _logger.info("### start UMG804 simulator")

    umg804_actions = {
        "umg804_reset": umg804_reset,
    }
    datastore = ModbusSimulatorContext(umg804_config, umg804_actions)
    context = ModbusServerContext(slaves=datastore, single=True)
    await StartAsyncTcpServer(
        context=context,
        address=("", PORT),
        framer=ModbusSocketFramer,
        allow_reuse_address=True,
    )
    _logger.info("### stop UMG804 simulator")


if __name__ == "__main__":
    asyncio.run(run_umg804_simulator(), debug=True)

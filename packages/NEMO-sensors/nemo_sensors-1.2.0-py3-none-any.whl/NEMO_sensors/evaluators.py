import ast
from typing import List

from NEMO.evaluators import BasicEvaluatorVisitor
from pymodbus.client import ModbusTcpClient

from NEMO_sensors.models import Sensor

# Special modbus functions, for backwards compatibility
modbus_functions_map = {
    "decode_16bit_uint": ModbusTcpClient.DATATYPE.UINT16,
    "decode_32bit_uint": ModbusTcpClient.DATATYPE.UINT32,
    "decode_64bit_uint": ModbusTcpClient.DATATYPE.UINT64,
    "decode_16bit_int": ModbusTcpClient.DATATYPE.INT16,
    "decode_32bit_int": ModbusTcpClient.DATATYPE.INT32,
    "decode_64bit_int": ModbusTcpClient.DATATYPE.INT64,
    "decode_32bit_float": ModbusTcpClient.DATATYPE.FLOAT32,
    "decode_64bit_float": ModbusTcpClient.DATATYPE.FLOAT64,
    "decode_bits": ModbusTcpClient.DATATYPE.BITS,
    "decode_string": ModbusTcpClient.DATATYPE.STRING,
}

# Special functions that are executed on the modbus client itself and require a complete connection
modbus_client_functions = ["read_coils"]


def evaluate_modbus_client_function(sensor: Sensor, name: str, args: List):
    # This will evaluate and return the value of the client function
    client = ModbusTcpClient(sensor.card.server, port=sensor.card.port)
    try:
        valid_connection = client.connect()
        if not valid_connection:
            raise Exception(f"Connection to server {sensor.card.server}:{sensor.card.port} could not be established")
        read_reply = getattr(client, name)(*args)
        if read_reply.isError():
            raise Exception(str(read_reply))
        if name == "read_coils":
            return read_reply.bits[0]
        return read_reply
    finally:
        client.close()


# Extension of the basic evaluator with additional modbus specific functions
# noinspection PyTypeChecker
class ModbusEvaluatorVisitor(BasicEvaluatorVisitor):
    def __init__(self, sensor, **kwargs):
        self.sensor = sensor
        super().__init__(**kwargs)

    def visit_Call(self, node: ast.Call):
        if node.func.id in self.functions:
            return super().visit_Call(node)
        elif node.func.id in modbus_functions_map:
            # for backwards compatibility
            function_args = [self.visit(arg) for arg in node.args]
            data_type = modbus_functions_map[node.func.id]
            return ModbusTcpClient.convert_from_registers(function_args[0], data_type, word_order="little")
        elif node.func.id in modbus_client_functions:
            function_args = [self.visit(arg) for arg in node.args]
            return evaluate_modbus_client_function(self.sensor, node.func.id, function_args)
        elif node.func.id == "convert_from_registers":
            function_args = [self.visit(arg) for arg in node.args]
            return ModbusTcpClient.convert_from_registers(*function_args)
        elif node.func.id == "convert_to_registers":
            function_args = [self.visit(arg) for arg in node.args]
            return ModbusTcpClient.convert_to_registers(*function_args)
        else:
            self.generic_visit(node)


def evaluate_modbus_expression(sensor, **kwargs):
    v = ModbusEvaluatorVisitor(sensor, **kwargs)
    return v.visit(ast.parse(sensor.formula, mode="eval").body)

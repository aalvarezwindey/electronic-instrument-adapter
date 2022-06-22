import ctypes
import logging
import os
from open_lisa.domain.command.command import Command, CommandType
from open_lisa.domain.command.command_parameters import CommandParameters
from open_lisa.domain.command.command_return import CommandReturn, CommandReturnType
from open_lisa.exceptions.invalid_clib_command_function_name import InvalidCLibCommandFunctionNameError
from open_lisa.exceptions.invalid_clib_command_lib_file import InvalidCLibCommandLibFileError

TMP_BUFFER_FILE = "tmp_file_buffer.bin"


class CLibCommand(Command):
    def __init__(self, name, lib_function, lib_file_name, parameters=CommandParameters(), command_return=CommandReturn(), description=''):
        """Creates a new SCPI command

        Args:
            name (string): the string syntax that identifies the command
            lib_function (string): Lib function to be called in the lib file
            lib_file_name (string): Lib file name should be an absolute path in order to find the library
            parameters (CommandParameters): an instance of command parameters
        """
        super().__init__(name=name, command=lib_function,
                         parameters=parameters, command_return=command_return, type=CommandType.CLIB, description=description)

        self.lib_function = lib_function
        self.lib_file_name = lib_file_name

        try:
            # Load the shared library into c types.
            self._c_lib = ctypes.CDLL(self.lib_file_name)
        except Exception as e:
            logging.error('[CLibCommand][__init__][CDLL] error: {}'.format(e))
            raise InvalidCLibCommandLibFileError(lib_name=self.lib_file_name)

        try:
            # c_lib is an object instance and function name is accessed like
            # an object property, doing c_lib[self.lib_function] is incorrect
            self._c_function = getattr(self._c_lib, self.lib_function)
        except Exception as e:
            logging.error(
                '[CLibCommand][__init__][INVALID_LIB_FUNCTION] error: {}'.format(e))
            raise InvalidCLibCommandFunctionNameError(
                function_name=self.lib_function, lib_name=self.lib_file_name)

        # Set returning type for marshalling
        command_return_ctype = self.command_return.to_ctype()
        self._c_function.restype = command_return_ctype

    @staticmethod
    def from_dict(command_dict, lib_base_path):
        return CLibCommand(
            name=command_dict["name"],
            lib_function=command_dict["command"],
            lib_file_name=lib_base_path + command_dict["lib_file_name"],
            parameters=CommandParameters.from_dict(command_dict["params"]),
            command_return=CommandReturn.from_dict(command_dict["return"]),
            description=command_dict["description"]
        )

    def to_dict(self, instrument_id):
        return {
            "instrument_id": instrument_id,
            "name": self.name,
            "command": self.lib_function,
            "type": str(self.type),
            # only return filename
            "lib_file_name": os.path.basename(self.lib_file_name),
            "description": self.description,
            "params": self.parameters.to_dict(),
            "return": self.command_return.to_dict()
        }

    def execute(self, params_values=[]):
        self.parameters.validate_parameters_values(params_values)

        # Generate C function arguments
        arguments = self.parameters.parameters_values_to_c_function_arguments(
            params_values)

        if self.command_return.type == CommandReturnType.BYTES:
            arguments.append(ctypes.c_char_p(TMP_BUFFER_FILE.encode()))
            result = self._c_function(*arguments)
            if result:
                logging.error("[CLibCommand][command={}] fail calling C function that returns bytes, result code is {}".format(
                    self.name, result))
                return bytes("C function error code {}".format(result).encode())
            else:
                data = bytes()
                with open(TMP_BUFFER_FILE, "rb") as f:
                    data = f.read()

                # Delete file
                os.remove(TMP_BUFFER_FILE)

                return bytes(data)
        else:
            result = self._c_function(*arguments)
            # ctypes c_char_p is returned as bytes
            return result.decode() if self._c_function.restype == ctypes.c_char_p else result

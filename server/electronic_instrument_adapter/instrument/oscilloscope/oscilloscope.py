from ..constants import INSTRUMENT_STATUS_AVAILABLE
from ..instrument import Instrument


class Oscilloscope(Instrument):
    def __init__(self, id, brand, model):
        super(Oscilloscope, self).__init__(id, brand, model)
        self.type = "oscilloscope"
        self.configuration = OscilloscopeConfiguration()
        if self.status == INSTRUMENT_STATUS_AVAILABLE:
            self.set_initial_configuration()

    def __str__(self):
        return "Oscilloscope:\n\t" \
               "Brand  : {}\n\t" \
               "Model  : {}\n\t" \
               "ID     : {}\n\t" \
               "Status : {}".format(
            self.brand,
            self.model,
            self.id,
            self.status)

    def as_dict(self):
        return {
            "id": self.id,
            "brand": self.brand,
            "model": self.model,
            "status": self.status,
            "configuration": {
                "volts_scale": self.configuration.volts_scale,
                "time_scale": self.configuration.time_scale
            }
        }

    def configuration_as_dict(self):
        return {
            "id": self.id,
            "configuration": {
                "volts_scale": self.configuration.volts_scale,
                "time_scale": self.configuration.time_scale
            }
        }

    def set_initial_configuration(self):
        raise Exception("NotImplementedException")

    # General purpose oscilloscope primitives

    def clear_status(self):
        raise Exception("NotImplementedException")

    def reset_settings(self):
        raise Exception("NotImplementedException")

    def get_identification(self):
        raise Exception("NotImplementedException")


    # Channel configuration primitives

    def set_channel_volts_scale(self, channel, volts_scale):
        raise Exception("NotImplementedException")

    def set_channel_probe(self, channel, probe):
        raise Exception("NotImplementedException")


    # Timebase primitives

    def set_timebase_scale(self, seconds):
        raise Exception("NotImplementedException")

    def set_timebase_mode(self, mode):
        raise Exception("NotImplementedException")

    def set_timebase_x_channel(self, channel):
        raise Exception("NotImplementedException")

    def set_timebase_y_channel(self, channel):
        raise Exception("NotImplementedException")


    # Acquisitions primitives

    def get_is_in_acquisitions_state(self):
        raise Exception("NotImplementedException")

    def stop_acquisitions(self):
        raise Exception("NotImplementedException")

    def set_acquisition_mode(self, mode):
        raise Exception("NotImplementedException")

    def get_acquisition_mode(self):
        raise Exception("NotImplementedException")

    def set_average_acquisition_mode_samples_amount(self, amount):
        raise Exception("NotImplementedException")

    def set_acquisition_memory_depth(self, depth):
        raise Exception("NotImplementedException")


    # Trigger primitives

    def force_trigger(self):
        raise Exception("NotImplementedException")

    def set_trigger_mode(self, mode):
        raise Exception("NotImplementedException")

    def set_trigger_type(self, type):
        raise Exception("NotImplementedException")

    def get_trigger_type(self):
        raise Exception("NotImplementedException")

    def set_trigger_edge_type(self, type):
        raise Exception("NotImplementedException")

    def set_trigger_edge_source(self, src):
        raise Exception("NotImplementedException")

    def set_trigger_level(self, level):
        raise Exception("NotImplementedException")


    # Waveform primitives

    def set_waveform_encoding(self, encoding):
        raise Exception("NotImplementedException")

    def get_waveform_encoding(self):
        raise Exception("NotImplementedException")

    def set_waveform_endianness(self, endianness):
        raise Exception("NotImplementedException")

    def set_waveform_source(self, src):
        raise Exception("NotImplementedException")

    def set_waveform_points_format(self, fmt):
        raise Exception("NotImplementedException")



class OscilloscopeConfiguration:
    def __init__(self, volts_scale=5, time_scale=0.000500):
        self.volts_scale = volts_scale  # in volts
        self.time_scale = time_scale    # in seconds
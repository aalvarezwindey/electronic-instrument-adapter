import pyvisa


def InstrumentFactory(type, id, brand, model):
    if type == "oscilloscope":
        from .oscilloscope.factory import OscilloscopeFactory
        return OscilloscopeFactory(id, brand, model)


class Instrument:
    def __init__(self, id, brand, model):
        self.id = id
        self.brand = brand
        self.model = model
        self.status = self.check_status()
        self.device = None

    def check_status(self):
        rm = pyvisa.ResourceManager()
        resources = rm.list_resources()
        if resources.__contains__(self.id):
            self.device = rm.open_resource(self.id)
            return "AVAILABLE"
        else:
            return "UNAVAILABLE"


class Oscilloscope(Instrument):
    def __init__(self, id, brand, model):
        super(Oscilloscope, self).__init__(id, brand, model)
        self.type = "oscilloscope"
        self.configuration = OscilloscopeConfiguration()

    def __str__(self):
        return "Oscilloscope:\n\t" \
                    "Brand  : {}\n\t" \
                    "Model  : {}\n\t" \
                    "ID     : {}\n\t" \
                    "Status : {}".format(
                        self.brand,
                        self.model,
                        self.id,
                        self.check_status())

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

    def set_volts_scale(self):
        raise Exception("NotImplementedException")


class OscilloscopeConfiguration:
    def __init__(self, volts_scale=5, time_scale=500):
        self.volts_scale = volts_scale  # in volts
        self.time_scale = time_scale  # in micro seconds

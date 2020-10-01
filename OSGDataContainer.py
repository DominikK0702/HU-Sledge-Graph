from OSGPulse import OSGPulseData


class OSGDataContainer:
    def __init__(self):
        self.pulse_data = OSGPulseData()

    def import_pulse(self, filename):
        try:
            self.pulse_data.load_from_file(filename)
            return True
        except Exception as e:
            return False

    def get_pulse_to_transfer(self):
        # todo get correct pulse
        return [i for i in range(0,3001)]
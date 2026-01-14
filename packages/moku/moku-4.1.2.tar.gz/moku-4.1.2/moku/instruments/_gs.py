from moku import Moku, MultiInstrumentSlottable


class GigabitStreamer(MultiInstrumentSlottable, Moku):
    """
    GigabitStreamer instrument object.

    This instrument streams data by transmitting and/or receiving UDP packets through
    the SFP ports at gigabit speeds.

    Read more at https://apis.liquidinstruments.com/reference/gs

    """

    INSTRUMENT_ID = 12
    OPERATION_GROUP = "gs"

    def __init__(
        self,
        ip=None,
        serial=None,
        force_connect=False,
        ignore_busy=False,
        persist_state=False,
        connect_timeout=15,
        read_timeout=30,
        slot=None,
        multi_instrument=None,
        **kwargs,
    ):
        self._init_instrument(
            ip=ip,
            serial=serial,
            force_connect=force_connect,
            ignore_busy=ignore_busy,
            persist_state=persist_state,
            connect_timeout=connect_timeout,
            read_timeout=read_timeout,
            slot=slot,
            multi_instrument=multi_instrument,
            **kwargs,
        )

    @classmethod
    def for_slot(cls, slot, multi_instrument):
        """Configures instrument at given slot in multi instrument mode"""
        return cls(slot=slot, multi_instrument=multi_instrument)

    def save_settings(self, filename):
        """
        Save instrument settings to a file. The file name should have
        a `.mokuconf` extension to be compatible with other tools.

        :type filename: FileDescriptorOrPath
        :param filename: The path to save the `.mokuconf` file to.
        """
        self.session.get_file(f"slot{self.slot}/{self.operation_group}", "save_settings", filename)

    def load_settings(self, filename):
        """
        Load a previously saved `.mokuconf` settings file into the instrument.
        To create a `.mokuconf` file, either use `save_settings` or the desktop app.

        :type filename: FileDescriptorOrPath
        :param filename: The path to the `.mokuconf` configuration to load
        """
        with open(filename, "rb") as f:
            self.session.post_file(
                f"slot{self.slot}/{self.operation_group}", "load_settings", data=f
            )

    def summary(self):
        """
        summary.
        """
        operation = "summary"
        return self.session.get(f"slot{self.slot}/{self.operation_group}", operation)

    def set_defaults(self):
        """
        set_defaults.
        """
        operation = "set_defaults"
        return self.session.post(f"slot{self.slot}/{self.operation_group}", operation)

    def set_frontend(
        self,
        channel,
        impedance,
        coupling,
        attenuation=None,
        gain=None,
        bandwidth=None,
        strict=True,
    ):
        """
        set_frontend.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type impedance: `string` ['1MOhm', '50Ohm']
        :param impedance: Input impedance

        :type coupling: `string` ['AC', 'DC']
        :param coupling: Input coupling

        :type attenuation: `string` ['-20dB', '0dB', '14dB', '20dB', '32dB', '40dB'] # noqa
        :param attenuation: Input attenuation.

        :type gain: `string` ['20dB', '0dB', '-14dB', '-20dB', '-32dB', '-40dB'] # noqa
        :param gain: Input gain.

        :type bandwidth: `string` ['1MHz', '30MHz', '200MHz', '300MHz', '600MHz', '2GHz']
        :param bandwidth: Input bandwidth

        """
        operation = "set_frontend"
        params = dict(
            strict=strict,
            channel=channel,
            impedance=impedance,
            coupling=coupling,
            attenuation=attenuation,
            gain=gain,
            bandwidth=bandwidth,
        )
        return self.session.post(f"slot{self.slot}/{self.operation_group}", operation, params)

    def get_frontend(self, channel):
        """
        get_frontend.

        :type channel: `integer`
        :param channel: Target channel

        """
        operation = "get_frontend"
        params = dict(
            channel=channel,
        )
        return self.session.post(f"slot{self.slot}/{self.operation_group}", operation, params)

    def enable_input(self, channel, enable=True, strict=True):
        """
        enable_input.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type enable: `boolean`
        :param enable: Enable input signal

        """
        operation = "enable_input"
        params = dict(
            strict=strict,
            channel=channel,
            enable=enable,
        )
        return self.session.post(f"slot{self.slot}/{self.operation_group}", operation, params)

    def set_acquisition(self, mode, sample_rate, strict=True):
        """
        set_acquisition.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type mode: `string` ['Normal', 'Precision'] # noqa
        :param mode: Acquisition mode

        :type sample_rate: `number` [5e3, 5e9]
        :param sample_rate: Target samples per second

        """
        operation = "set_acquisition"
        params = dict(
            strict=strict,
            mode=mode,
            sample_rate=sample_rate,
        )
        return self.session.post(f"slot{self.slot}/{self.operation_group}", operation, params)

    def start_sending(self, duration, delay=0, trigger_source=None, trigger_level=0, strict=True):
        """
        start_sending.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type duration: `double` Sec
        :param duration: Duration to log for

        :type delay: `integer` Sec
        :param delay: Delay the start by

        :type trigger_source: `string` ['Input1', 'Input2', 'Input3', 'Input4', 'InputA', 'InputB', 'External'] # noqa
        :param trigger_source: Trigger source

        :type trigger_level: `number` [-5V, 5V]
        :param trigger_level: Trigger level

        """
        operation = "start_sending"
        params = dict(
            strict=strict,
            duration=duration,
            delay=delay,
            trigger_source=trigger_source,
            trigger_level=trigger_level,
        )
        return self.session.post(f"slot{self.slot}/{self.operation_group}", operation, params)

    def stop_sending(self):
        """
        stop_sending.
        """
        operation = "stop_sending"
        return self.session.post(f"slot{self.slot}/{self.operation_group}", operation)

    def get_send_status(self):
        """
        get_send_status.
        """
        operation = "get_send_status"
        return self.session.get(f"slot{self.slot}/{self.operation_group}", operation)

    def get_receive_status(self):
        """
        get_receive_status.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        """
        operation = "get_receive_status"
        return self.session.get(f"slot{self.slot}/{self.operation_group}", operation)

    def reset_receive_counters(self):
        """
        reset_receive_counters.
        """
        operation = "reset_receive_counters"
        return self.session.post(f"slot{self.slot}/{self.operation_group}", operation)

    def set_local_network(self, ip_address, port, multicast_ip_address=None, strict=True):
        """
        set_local_network.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type ip_address: `string`
        :param ip_address: IP address

        :type port: `integer`
        :param port: UDP port number

        :type multicast_ip_address: `string`
        :param multicast_ip_address: Multicast IP address

        """
        operation = "set_local_network"
        params = dict(
            strict=strict,
            ip_address=ip_address,
            multicast_ip_address=multicast_ip_address,
            port=port,
        )
        return self.session.post(f"slot{self.slot}/{self.operation_group}", operation, params)

    def set_outgoing_packets(self, mtu, strict=True):
        """
        set_outgoing_packets.

        :type mtu: `string` ["508bytes", "576bytes", "1500bytes", "9000bytes", "65535bytes"] # noqa
        :param mtu: Network Maximum Transmission Unit

        """
        operation = "set_outgoing_packets"
        params = dict(
            strict=strict,
            mtu=mtu,
        )
        return self.session.post(f"slot{self.slot}/{self.operation_group}", operation, params)

    def set_remote_network(self, ip_address, port, mac_address, strict=True):
        """
        set_remote_network.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type ip_address: `string`
        :param ip_address: IP Address

        :type port: `integer`
        :param port: Remote UDP port number

        :type mac_address: `string`
        :param mac_address: MAC address

        """
        operation = "set_remote_network"
        params = dict(
            strict=strict,
            ip_address=ip_address,
            port=port,
            mac_address=mac_address,
        )
        return self.session.post(f"slot{self.slot}/{self.operation_group}", operation, params)

    def set_interpolation(self, mode, strict=True):
        """
        set_interpolation.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type mode: `string` ["None", "Linear"]
        :param mode: Interpolation mode

        """
        operation = "set_interpolation"
        params = dict(
            strict=strict,
            mode=mode,
        )
        return self.session.post(f"slot{self.slot}/{self.operation_group}", operation, params)

    def set_output(self, channel, enable, gain, offset, strict=True):
        """
        set_output.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type enable: `boolean`
        :param enable: Enable output signal

        :type gain: `number`
        :param gain: Gain in dB

        :type offset: `number`
        :param offset: Offset in V

        """
        operation = "set_output"
        params = dict(
            strict=strict,
            channel=channel,
            enable=enable,
            gain=gain,
            offset=offset,
        )
        return self.session.post(f"slot{self.slot}/{self.operation_group}", operation, params)


class GigabitStreamerPlus(GigabitStreamer):
    """
    GigabitStreamerPlus instrument object.

    This instrument streams data by transmitting and/or receiving UDP packets through
    the QSFP port at high gigabit speeds.

    Read more at https://apis.liquidinstruments.com/reference/gsp

    """

    INSTRUMENT_ID = 13
    OPERATION_GROUP = "gsp"

# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Spirone(KaitaiStruct):
    """:field csp_header_priority: beacon_types.type_check.csp_header_priority
    :field csp_header_source: beacon_types.type_check.csp_header_source
    :field csp_header_destination: beacon_types.type_check.csp_header_destination
    :field csp_header_destination_port: beacon_types.type_check.csp_header_destination_port
    :field csp_header_source_port: beacon_types.type_check.csp_header_source_port
    :field csp_header_reserved: beacon_types.type_check.csp_header_reserved
    :field csp_header_flags: beacon_types.type_check.csp_header_flags
    :field firmware_version: beacon_types.type_check.firmware_version
    :field positioning_flag: beacon_types.type_check.positioning_flag
    :field position_x: beacon_types.type_check.position_x
    :field position_y: beacon_types.type_check.position_y
    :field position_z: beacon_types.type_check.position_z
    :field velocity_x: beacon_types.type_check.velocity_x
    :field velocity_y: beacon_types.type_check.velocity_y
    :field velocity_z: beacon_types.type_check.velocity_z
    :field battery_mode: beacon_types.type_check.battery_mode
    :field battery_voltage: beacon_types.type_check.battery_voltage
    :field battery_current: beacon_types.type_check.battery_current
    :field power_switch_uhf_transceiver: beacon_types.type_check.power_switch_uhf_transceiver
    :field power_switch_leo_nav: beacon_types.type_check.power_switch_leo_nav
    :field power_switch_gps_receiver: beacon_types.type_check.power_switch_gps_receiver
    :field power_switch_cameras: beacon_types.type_check.power_switch_cameras
    :field power_switch_s_band: beacon_types.type_check.power_switch_s_band
    :field power_switch_rp: beacon_types.type_check.power_switch_rp
    :field power_switch_current_uhf_transceiver: beacon_types.type_check.power_switch_current_uhf_transceiver
    :field power_switch_current_leo_nav: beacon_types.type_check.power_switch_current_leo_nav
    :field power_switch_current_gps_receiver: beacon_types.type_check.power_switch_current_gps_receiver
    :field power_switch_current_cameras: beacon_types.type_check.power_switch_current_cameras
    :field power_switch_current_s_band: beacon_types.type_check.power_switch_current_s_band
    :field power_switch_current_rp: beacon_types.type_check.power_switch_current_rp
    :field solar_cell_input_voltage_x: beacon_types.type_check.solar_cell_input_voltage_x
    :field solar_cell_input_voltage_y: beacon_types.type_check.solar_cell_input_voltage_y
    :field solar_cell_input_voltage_z: beacon_types.type_check.solar_cell_input_voltage_z
    :field solar_cell_input_current_x: beacon_types.type_check.solar_cell_input_current_x
    :field solar_cell_input_current_y: beacon_types.type_check.solar_cell_input_current_y
    :field solar_cell_input_current_z: beacon_types.type_check.solar_cell_input_current_z
    :field estimated_attitude_q0: beacon_types.type_check.estimated_attitude_q0
    :field estimated_attitude_q1: beacon_types.type_check.estimated_attitude_q1
    :field estimated_attitude_q2: beacon_types.type_check.estimated_attitude_q2
    :field estimated_attitude_q3: beacon_types.type_check.estimated_attitude_q3
    :field estimated_gyro_bias_roll: beacon_types.type_check.estimated_gyro_bias_roll
    :field estimated_gyro_bias_pitch: beacon_types.type_check.estimated_gyro_bias_pitch
    :field estimated_gyro_bias_yaw: beacon_types.type_check.estimated_gyro_bias_yaw
    :field estimated_angular_rate_roll: beacon_types.type_check.estimated_angular_rate_roll
    :field estimated_angular_rate_pitch: beacon_types.type_check.estimated_angular_rate_pitch
    :field estimated_angular_rate_yaw: beacon_types.type_check.estimated_angular_rate_yaw
    :field measured_angular_rate_roll: beacon_types.type_check.measured_angular_rate_roll
    :field measured_angular_rate_pitch: beacon_types.type_check.measured_angular_rate_pitch
    :field measured_angular_rate_yaw: beacon_types.type_check.measured_angular_rate_yaw
    :field sun_eclipse: beacon_types.type_check.sun_eclipse
    :field current_operation_mode: beacon_types.type_check.current_operation_mode
    :field elapsed_time: beacon_types.type_check.elapsed_time
    :field temperature_obc_1: beacon_types.type_check.temperature_obc_1
    :field temperature_obc_2: beacon_types.type_check.temperature_obc_2
    :field temperature_eps_p31u_1: beacon_types.type_check.temperature_eps_p31u_1
    :field temperature_eps_p31u_2: beacon_types.type_check.temperature_eps_p31u_2
    :field temperature_eps_p31u_3: beacon_types.type_check.temperature_eps_p31u_3
    :field temperature_eps_p31u_4: beacon_types.type_check.temperature_eps_p31u_4
    :field temperature_eps_bp4_1: beacon_types.type_check.temperature_eps_bp4_1
    :field temperature_eps_bp4_2: beacon_types.type_check.temperature_eps_bp4_2
    :field temperature_uhf_ax100_brd: beacon_types.type_check.temperature_uhf_ax100_brd
    :field temperature_uhf_ax100_pa: beacon_types.type_check.temperature_uhf_ax100_pa
    :field deploy_status_s_band_antenna: beacon_types.type_check.deploy_status_s_band_antenna
    :field deploy_status_uhf_antenna: beacon_types.type_check.deploy_status_uhf_antenna
    :field deploy_attempts_uhf: beacon_types.type_check.deploy_attempts_uhf
    :field deploy_attempts_s_band: beacon_types.type_check.deploy_attempts_s_band
    :field total_tx_data_volume: beacon_types.type_check.total_tx_data_volume
    :field total_rx_data_volume: beacon_types.type_check.total_rx_data_volume
    :field beacon_type: beacon_types.type_check.beacon_type
    :field satellite_time: beacon_types.type_check.satellite_time
    
    .. seealso::
       Sejong University
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.beacon_types = Spirone.BeaconTypesT(self._io, self, self._root)

    class BeaconTypesT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self.check
            if _on == 1012027214:
                self.type_check = Spirone.Simple(self._io, self, self._root)
            else:
                self.type_check = Spirone.Full(self._io, self, self._root)

        @property
        def check(self):
            if hasattr(self, '_m_check'):
                return self._m_check

            _pos = self._io.pos()
            self._io.seek(59)
            self._m_check = self._io.read_u4be()
            self._io.seek(_pos)
            return getattr(self, '_m_check', None)


    class Full(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = []
            for i in range(16):
                self.ax25_header.append(self._io.read_u1())

            self.csp_header_priority = self._io.read_bits_int_be(2)
            self.csp_header_source = self._io.read_bits_int_be(5)
            self.csp_header_destination = self._io.read_bits_int_be(5)
            self.csp_header_destination_port = self._io.read_bits_int_be(6)
            self.csp_header_source_port = self._io.read_bits_int_be(6)
            self.csp_header_reserved = self._io.read_bits_int_be(4)
            self.csp_header_flags = self._io.read_bits_int_be(4)
            self._io.align_to_byte()
            self.start_id = (self._io.read_bytes(4)).decode(u"UTF-8")
            if not self.start_id == u"SPI>":
                raise kaitaistruct.ValidationNotEqualError(u"SPI>", self.start_id, self._io, u"/types/full/seq/8")
            self.firmware_version = self._io.read_u1()
            self.time_year = self._io.read_u1()
            self.time_month = self._io.read_u1()
            self.time_day = self._io.read_u1()
            self.time_hour = self._io.read_u1()
            self.time_minute = self._io.read_u1()
            self.time_second = self._io.read_u1()
            self.positioning_flag = self._io.read_u1()
            self.position_x = self._io.read_s4be()
            self.position_y = self._io.read_s4be()
            self.position_z = self._io.read_s4be()
            self.velocity_x = self._io.read_s4be()
            self.velocity_y = self._io.read_s4be()
            self.velocity_z = self._io.read_s4be()
            self.battery_mode = self._io.read_u1()
            self.battery_voltage = self._io.read_u2be()
            self.battery_current = self._io.read_u2be()
            self.not_used = self._io.read_bits_int_be(2)
            self.power_switch_uhf_transceiver = self._io.read_bits_int_be(1) != 0
            self.power_switch_leo_nav = self._io.read_bits_int_be(1) != 0
            self.power_switch_gps_receiver = self._io.read_bits_int_be(1) != 0
            self.power_switch_cameras = self._io.read_bits_int_be(1) != 0
            self.power_switch_s_band = self._io.read_bits_int_be(1) != 0
            self.power_switch_rp = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.power_switch_current_uhf_transceiver = self._io.read_u2be()
            self.power_switch_current_leo_nav = self._io.read_u2be()
            self.power_switch_current_gps_receiver = self._io.read_u2be()
            self.power_switch_current_cameras = self._io.read_u2be()
            self.power_switch_current_s_band = self._io.read_u2be()
            self.power_switch_current_rp = self._io.read_u2be()
            self.solar_cell_input_voltage_x = self._io.read_u2be()
            self.solar_cell_input_voltage_y = self._io.read_u2be()
            self.solar_cell_input_voltage_z = self._io.read_u2be()
            self.solar_cell_input_current_x = self._io.read_u2be()
            self.solar_cell_input_current_y = self._io.read_u2be()
            self.solar_cell_input_current_z = self._io.read_u2be()
            self.estimated_attitude_q0_check = self._io.read_f4be()
            self.estimated_attitude_q1_check = self._io.read_f4be()
            self.estimated_attitude_q2_check = self._io.read_f4be()
            self.estimated_attitude_q3_check = self._io.read_f4be()
            self.estimated_gyro_bias_roll_check = self._io.read_f4be()
            self.estimated_gyro_bias_pitch_check = self._io.read_f4be()
            self.estimated_gyro_bias_yaw_check = self._io.read_f4be()
            self.estimated_angular_rate_roll_check = self._io.read_f4be()
            self.estimated_angular_rate_pitch_check = self._io.read_f4be()
            self.estimated_angular_rate_yaw_check = self._io.read_f4be()
            self.measured_angular_rate_roll_check = self._io.read_f4be()
            self.measured_angular_rate_pitch_check = self._io.read_f4be()
            self.measured_angular_rate_yaw_check = self._io.read_f4be()
            self.not_used_1 = self._io.read_bits_int_be(6)
            self.sun_eclipse = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.current_operation_mode = self._io.read_u1()
            self.elapsed_time = self._io.read_u4be()
            self.not_used_2 = []
            for i in range(5):
                self.not_used_2.append(self._io.read_s1())

            self.temperature_obc_1 = self._io.read_s1()
            self.temperature_obc_2 = self._io.read_s1()
            self.temperature_eps_p31u_1 = self._io.read_s1()
            self.temperature_eps_p31u_2 = self._io.read_s1()
            self.temperature_eps_p31u_3 = self._io.read_s1()
            self.temperature_eps_p31u_4 = self._io.read_s1()
            self.temperature_eps_bp4_1 = self._io.read_s1()
            self.temperature_eps_bp4_2 = self._io.read_s1()
            self.temperature_uhf_ax100_brd = self._io.read_s1()
            self.temperature_uhf_ax100_pa = self._io.read_s1()
            self.not_used_3 = self._io.read_bits_int_be(6)
            self.deploy_status_s_band_antenna = self._io.read_bits_int_be(1) != 0
            self.deploy_status_uhf_antenna = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.deploy_attempts_uhf = self._io.read_u1()
            self.deploy_attempts_s_band = self._io.read_u1()
            self.total_tx_data_volume = self._io.read_u4be()
            self.total_rx_data_volume = self._io.read_u4be()
            self.end_id = (self._io.read_bytes(5)).decode(u"UTF-8")
            if not self.end_id == u"<RONE":
                raise kaitaistruct.ValidationNotEqualError(u"<RONE", self.end_id, self._io, u"/types/full/seq/80")

        @property
        def measured_angular_rate_pitch(self):
            if hasattr(self, '_m_measured_angular_rate_pitch'):
                return self._m_measured_angular_rate_pitch

            if self.measured_angular_rate_pitch_check == self.measured_angular_rate_pitch_check:
                self._m_measured_angular_rate_pitch = self.measured_angular_rate_pitch_check

            return getattr(self, '_m_measured_angular_rate_pitch', None)

        @property
        def month(self):
            """only for calculation, do not display."""
            if hasattr(self, '_m_month'):
                return self._m_month

            self._m_month = (u"0" + str(self.time_month) if len(str(self.time_month)) == 1 else str(self.time_month))
            return getattr(self, '_m_month', None)

        @property
        def minute(self):
            """only for calculation, do not display."""
            if hasattr(self, '_m_minute'):
                return self._m_minute

            self._m_minute = (u"0" + str(self.time_minute) if len(str(self.time_minute)) == 1 else str(self.time_minute))
            return getattr(self, '_m_minute', None)

        @property
        def estimated_angular_rate_yaw(self):
            if hasattr(self, '_m_estimated_angular_rate_yaw'):
                return self._m_estimated_angular_rate_yaw

            if self.estimated_angular_rate_yaw_check == self.estimated_angular_rate_yaw_check:
                self._m_estimated_angular_rate_yaw = self.estimated_angular_rate_yaw_check

            return getattr(self, '_m_estimated_angular_rate_yaw', None)

        @property
        def satellite_time(self):
            if hasattr(self, '_m_satellite_time'):
                return self._m_satellite_time

            self._m_satellite_time = u"20" + self.year + u"-" + self.month + u"-" + self.day + u"T" + self.hour + u":" + self.minute + u":" + self.second + u"Z"
            return getattr(self, '_m_satellite_time', None)

        @property
        def estimated_gyro_bias_yaw(self):
            if hasattr(self, '_m_estimated_gyro_bias_yaw'):
                return self._m_estimated_gyro_bias_yaw

            if self.estimated_gyro_bias_yaw_check == self.estimated_gyro_bias_yaw_check:
                self._m_estimated_gyro_bias_yaw = self.estimated_gyro_bias_yaw_check

            return getattr(self, '_m_estimated_gyro_bias_yaw', None)

        @property
        def estimated_attitude_q3(self):
            if hasattr(self, '_m_estimated_attitude_q3'):
                return self._m_estimated_attitude_q3

            if self.estimated_attitude_q2_check == self.estimated_attitude_q2_check:
                self._m_estimated_attitude_q3 = self.estimated_attitude_q2_check

            return getattr(self, '_m_estimated_attitude_q3', None)

        @property
        def year(self):
            """only for calculation, do not display."""
            if hasattr(self, '_m_year'):
                return self._m_year

            self._m_year = (u"0" + str(self.time_year) if len(str(self.time_year)) == 1 else str(self.time_year))
            return getattr(self, '_m_year', None)

        @property
        def beacon_type(self):
            if hasattr(self, '_m_beacon_type'):
                return self._m_beacon_type

            self._m_beacon_type = u"full"
            return getattr(self, '_m_beacon_type', None)

        @property
        def estimated_angular_rate_roll(self):
            if hasattr(self, '_m_estimated_angular_rate_roll'):
                return self._m_estimated_angular_rate_roll

            if self.estimated_angular_rate_roll_check == self.estimated_angular_rate_roll_check:
                self._m_estimated_angular_rate_roll = self.estimated_angular_rate_roll_check

            return getattr(self, '_m_estimated_angular_rate_roll', None)

        @property
        def second(self):
            """only for calculation, do not display."""
            if hasattr(self, '_m_second'):
                return self._m_second

            self._m_second = (u"0" + str(self.time_second) if len(str(self.time_second)) == 1 else str(self.time_second))
            return getattr(self, '_m_second', None)

        @property
        def measured_angular_rate_roll(self):
            if hasattr(self, '_m_measured_angular_rate_roll'):
                return self._m_measured_angular_rate_roll

            if self.measured_angular_rate_roll_check == self.measured_angular_rate_roll_check:
                self._m_measured_angular_rate_roll = self.measured_angular_rate_roll_check

            return getattr(self, '_m_measured_angular_rate_roll', None)

        @property
        def estimated_attitude_q0(self):
            if hasattr(self, '_m_estimated_attitude_q0'):
                return self._m_estimated_attitude_q0

            if self.estimated_attitude_q0_check == self.estimated_attitude_q0_check:
                self._m_estimated_attitude_q0 = self.estimated_attitude_q0_check

            return getattr(self, '_m_estimated_attitude_q0', None)

        @property
        def estimated_gyro_bias_roll(self):
            if hasattr(self, '_m_estimated_gyro_bias_roll'):
                return self._m_estimated_gyro_bias_roll

            if self.estimated_gyro_bias_roll_check == self.estimated_gyro_bias_roll_check:
                self._m_estimated_gyro_bias_roll = self.estimated_gyro_bias_roll_check

            return getattr(self, '_m_estimated_gyro_bias_roll', None)

        @property
        def estimated_attitude_q1(self):
            if hasattr(self, '_m_estimated_attitude_q1'):
                return self._m_estimated_attitude_q1

            if self.estimated_attitude_q1_check == self.estimated_attitude_q1_check:
                self._m_estimated_attitude_q1 = self.estimated_attitude_q1_check

            return getattr(self, '_m_estimated_attitude_q1', None)

        @property
        def estimated_angular_rate_pitch(self):
            if hasattr(self, '_m_estimated_angular_rate_pitch'):
                return self._m_estimated_angular_rate_pitch

            if self.estimated_angular_rate_pitch_check == self.estimated_angular_rate_pitch_check:
                self._m_estimated_angular_rate_pitch = self.estimated_angular_rate_pitch_check

            return getattr(self, '_m_estimated_angular_rate_pitch', None)

        @property
        def estimated_attitude_q2(self):
            if hasattr(self, '_m_estimated_attitude_q2'):
                return self._m_estimated_attitude_q2

            if self.estimated_attitude_q2_check == self.estimated_attitude_q2_check:
                self._m_estimated_attitude_q2 = self.estimated_attitude_q2_check

            return getattr(self, '_m_estimated_attitude_q2', None)

        @property
        def measured_angular_rate_yaw(self):
            if hasattr(self, '_m_measured_angular_rate_yaw'):
                return self._m_measured_angular_rate_yaw

            if self.measured_angular_rate_yaw_check == self.measured_angular_rate_yaw_check:
                self._m_measured_angular_rate_yaw = self.measured_angular_rate_yaw_check

            return getattr(self, '_m_measured_angular_rate_yaw', None)

        @property
        def estimated_gyro_bias_pitch(self):
            if hasattr(self, '_m_estimated_gyro_bias_pitch'):
                return self._m_estimated_gyro_bias_pitch

            if self.estimated_gyro_bias_pitch_check == self.estimated_gyro_bias_pitch_check:
                self._m_estimated_gyro_bias_pitch = self.estimated_gyro_bias_pitch_check

            return getattr(self, '_m_estimated_gyro_bias_pitch', None)

        @property
        def day(self):
            """only for calculation, do not display."""
            if hasattr(self, '_m_day'):
                return self._m_day

            self._m_day = (u"0" + str(self.time_day) if len(str(self.time_day)) == 1 else str(self.time_day))
            return getattr(self, '_m_day', None)

        @property
        def hour(self):
            """only for calculation, do not display."""
            if hasattr(self, '_m_hour'):
                return self._m_hour

            self._m_hour = (u"0" + str(self.time_hour) if len(str(self.time_hour)) == 1 else str(self.time_hour))
            return getattr(self, '_m_hour', None)


    class Simple(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = []
            for i in range(16):
                self.ax25_header.append(self._io.read_u1())

            self.csp_header_priority = self._io.read_bits_int_be(2)
            self.csp_header_source = self._io.read_bits_int_be(5)
            self.csp_header_destination = self._io.read_bits_int_be(5)
            self.csp_header_destination_port = self._io.read_bits_int_be(6)
            self.csp_header_source_port = self._io.read_bits_int_be(6)
            self.csp_header_reserved = self._io.read_bits_int_be(4)
            self.csp_header_flags = self._io.read_bits_int_be(4)
            self._io.align_to_byte()
            self.start_id = (self._io.read_bytes(4)).decode(u"UTF-8")
            if not self.start_id == u"SPI>":
                raise kaitaistruct.ValidationNotEqualError(u"SPI>", self.start_id, self._io, u"/types/simple/seq/8")
            self.firmware_version = self._io.read_u1()
            self.time_year = self._io.read_u1()
            self.time_month = self._io.read_u1()
            self.time_day = self._io.read_u1()
            self.time_hour = self._io.read_u1()
            self.time_minute = self._io.read_u1()
            self.time_second = self._io.read_u1()
            self.positioning_flag = self._io.read_u1()
            self.position_x = self._io.read_s4be()
            self.position_y = self._io.read_s4be()
            self.position_z = self._io.read_s4be()
            self.velocity_x = self._io.read_s4be()
            self.velocity_y = self._io.read_s4be()
            self.velocity_z = self._io.read_s4be()
            self.battery_mode = self._io.read_u1()
            self.battery_voltage = self._io.read_u2be()
            self.end_id = (self._io.read_bytes(5)).decode(u"UTF-8")
            if not self.end_id == u"<RONE":
                raise kaitaistruct.ValidationNotEqualError(u"<RONE", self.end_id, self._io, u"/types/simple/seq/25")

        @property
        def month(self):
            """only for calculation, do not display."""
            if hasattr(self, '_m_month'):
                return self._m_month

            self._m_month = (u"0" + str(self.time_month) if len(str(self.time_month)) == 1 else str(self.time_month))
            return getattr(self, '_m_month', None)

        @property
        def minute(self):
            """only for calculation, do not display."""
            if hasattr(self, '_m_minute'):
                return self._m_minute

            self._m_minute = (u"0" + str(self.time_minute) if len(str(self.time_minute)) == 1 else str(self.time_minute))
            return getattr(self, '_m_minute', None)

        @property
        def satellite_time(self):
            if hasattr(self, '_m_satellite_time'):
                return self._m_satellite_time

            self._m_satellite_time = u"20" + self.year + u"-" + self.month + u"-" + self.day + u"T" + self.hour + u":" + self.minute + u":" + self.second + u"Z"
            return getattr(self, '_m_satellite_time', None)

        @property
        def year(self):
            """only for calculation, do not display."""
            if hasattr(self, '_m_year'):
                return self._m_year

            self._m_year = (u"0" + str(self.time_year) if len(str(self.time_year)) == 1 else str(self.time_year))
            return getattr(self, '_m_year', None)

        @property
        def beacon_type(self):
            if hasattr(self, '_m_beacon_type'):
                return self._m_beacon_type

            self._m_beacon_type = u"simple"
            return getattr(self, '_m_beacon_type', None)

        @property
        def second(self):
            """only for calculation, do not display."""
            if hasattr(self, '_m_second'):
                return self._m_second

            self._m_second = (u"0" + str(self.time_second) if len(str(self.time_second)) == 1 else str(self.time_second))
            return getattr(self, '_m_second', None)

        @property
        def day(self):
            """only for calculation, do not display."""
            if hasattr(self, '_m_day'):
                return self._m_day

            self._m_day = (u"0" + str(self.time_day) if len(str(self.time_day)) == 1 else str(self.time_day))
            return getattr(self, '_m_day', None)

        @property
        def hour(self):
            """only for calculation, do not display."""
            if hasattr(self, '_m_hour'):
                return self._m_hour

            self._m_hour = (u"0" + str(self.time_hour) if len(str(self.time_hour)) == 1 else str(self.time_hour))
            return getattr(self, '_m_hour', None)




import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib
import random

from libraries.bluetooth import constants
from Utils.logger import Logger
import struct
log = Logger('battery_service_logs')


class BatteryService(dbus.service.Object):
    def __init__(self, bus, index, mainloop):
        #self.path = constants.service_path + f"{instance_id}_service{index}"
        self.path = constants.service_path + f"_service{index}"

        self.bus = bus
        self.uuid = constants.battery_service_uuid  # "180F"
        self.primary = True
        self.characteristics = []
        dbus.service.Object.__init__(self, bus, self.path)
        self.battery_level_char = BatteryLevelCharacteristic(bus, 0, self, mainloop)
        self.characteristics.append(self.battery_level_char)
        self.battery_level_status = BatteryLevelStatusCharacteristic(bus, 1, self, mainloop)
        self.characteristics.append(self.battery_level_status)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def get_properties(self):
        return {
            constants.gatt_service_interface: {
                'UUID': self.uuid,
                'Primary': dbus.Boolean(self.primary),
                'Characteristics': dbus.Array(
                    [char.get_path() for char in self.characteristics],
                    signature='o'
                )
            }
        }

    def get_characteristics(self):
        return self.characteristics


class BatteryLevelCharacteristic(dbus.service.Object):
    def __init__(self, bus, index, service, mainloop):
        #self.path = service.get_path() + f'/char{index}_{instance_id}'
        self.path = service.get_path() + f'/char{index}'

        self.bus = bus
        self.service = service
        self.uuid = constants.battery_level_uuid
        self.flags = ['read', 'notify']
        self.notifying = False
        self.mainloop = mainloop
        dbus.service.Object.__init__(self, bus, self.path)
        self.descriptor = BatteryLevelDescriptor(bus, 0, self)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def get_properties(self):
        return {
            constants.gatt_characteristic_interface: {
                'UUID': self.uuid,
                'Service': self.service.get_path(),
                'Flags': dbus.Array(self.flags, signature='s'),
                'Descriptors': dbus.Array([self.descriptor.get_path()], signature='o')
            }
        }

    @dbus.service.method(constants.gatt_characteristic_interface, in_signature='a{sv}', out_signature='ay')
    def ReadValue(self, options):
        """Return current battery level"""
        level = random.randint(10, 100)
        log.info(f"Battery Level read: {level}%")
        return [dbus.Byte(level)]

    @dbus.service.method(constants.gatt_characteristic_interface, in_signature='', out_signature='')
    def StartNotify(self):
        if self.notifying:
            return
        self.notifying = True
        log.info("Battery Level: Notifications started")
        GLib.timeout_add(3000, self.notify_battery_level)

    @dbus.service.method(constants.gatt_characteristic_interface, in_signature='', out_signature='')
    def StopNotify(self):
        self.notifying = False
        log.info("Battery Level: Notifications stopped")

    def notify_battery_level(self):
        if not self.notifying:
            return False
        level = random.randint(5, 100)
        value = [dbus.Byte(level)]
        log.debug(f"Sending battery level notification: {level}%")
        self.PropertiesChanged(constants.gatt_characteristic_interface, {'Value': value}, [])
        return True  # Continue timeout

    @dbus.service.signal(dbus_interface='org.freedesktop.DBus.Properties', signature='sa{sv}as')
    def PropertiesChanged(self, interface, changed, invalidated):
        pass



class BatteryLevelDescriptor(dbus.service.Object):
    def __init__(self, bus, index, characteristic):
        #self.path = characteristic.get_path() + f'/desc{index}_{instance_id}'
        self.path = characteristic.get_path() + f'/desc{index}'

        self.bus = bus
        self.characteristic = characteristic
        self.uuid = constants.client_characteristic_config_uuid
        self.flags = ['read', 'write']
        dbus.service.Object.__init__(self, bus, self.path)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def get_properties(self):
        return {
            constants.gatt_descriptor_interface: {
                'UUID': self.uuid,
                'Characteristic': self.characteristic.get_path(),
                'Flags': dbus.Array(self.flags, signature='s'),
            }
        }

    @dbus.service.method(constants.gatt_descriptor_interface, in_signature='a{sv}', out_signature='ay')
    def ReadValue(self, options):
        log.debug("Battery Level Descriptor: ReadValue")
        return [dbus.Byte(0x00), dbus.Byte(0x00)]

    @dbus.service.method(constants.gatt_descriptor_interface, in_signature='aya{sv}', out_signature='')
    def WriteValue(self, value, options):
        log.debug(f"Battery Level Descriptor: WriteValue {value}")


class BatteryLevelStatusCharacteristic(dbus.service.Object):
    """Simulated Battery Level Status characteristic (0=Unknown, 1=Good, 2=Low, 3=Critical)"""
    def __init__(self, bus, index, service, mainloop):
       # self.path = service.get_path() + f'/char{index}_{instance_id}'
        self.path = service.get_path() + f'/char{index}'
        self.bus = bus
        self.descriptor = BatteryLevelDescriptor(bus, 0, self)
        self.service = service
        self.uuid = constants.battery_level_status_uuid  # "2A1B"
        self.flags = ['read', 'notify']
        self.notifying = False
        self.mainloop = mainloop
        dbus.service.Object.__init__(self, bus, self.path)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def get_properties(self):
        return {
            constants.gatt_characteristic_interface: {
                'UUID': self.uuid,
                'Service': self.service.get_path(),
                'Flags': dbus.Array(self.flags, signature='s'),
                'Descriptors': dbus.Array([self.descriptor.get_path()], signature='o')
            }
        }

    @dbus.service.method(constants.gatt_characteristic_interface,
                         in_signature='a{sv}', out_signature='ay')
    def ReadValue(self, options):
        status = random.choice([1, 2, 3])
        status_map = {1: "Good", 2: "Low", 3: "Critical"}
        log.info(f"Battery Level Status read: {status_map.get(status)}")
        return [dbus.Byte(status)]

    @dbus.service.method(constants.gatt_characteristic_interface,
                         in_signature='', out_signature='')
    def StartNotify(self):
        if self.notifying:
            return
        self.notifying = True
        log.info("Battery Level Status: Notifications started")
        GLib.timeout_add(5000, self.notify_status)

    @dbus.service.method(constants.gatt_characteristic_interface,
                         in_signature='', out_signature='')
    def StopNotify(self):
        self.notifying = False
        log.info("Battery Level Status: Notifications stopped")

    def notify_status(self):
        if not self.notifying:
            return False
        status = random.choice([1, 2, 3])
        status_map = {1: "Good", 2: "Low", 3: "Critical"}
        log.debug(f"Sending Battery Level Status notification: {status_map.get(status)}")
        self.PropertiesChanged(constants.gatt_characteristic_interface,
                               {'Value': [dbus.Byte(status)]}, [])
        return True

    @dbus.service.signal(dbus_interface='org.freedesktop.DBus.Properties',
                         signature='sa{sv}as')
    def PropertiesChanged(self, interface, changed, invalidated):
        pass


class Advertisement(dbus.service.Object):
    def __init__(self, bus, service_uuid):
        self.service_uuid = service_uuid
        #self.path = constants.advertisement_path + f"{instance_id}"
        self.path = constants.advertisement_path

        self.bus = bus
        dbus.service.Object.__init__(self, bus, self.path)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    @dbus.service.method('org.freedesktop.DBus.Properties', in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != constants.le_advertisement_interface:
            raise dbus.exceptions.DBusException('org.freedesktop.DBus.Error.InvalidArgs', 'Invalid interface %s' % interface)
        return {
            'Type': 'peripheral',
            'LocalName': 'GATT_Test_Server',
            'ServiceUUIDs': [self.service_uuid],
            'IncludeTxPower': True
        }

    @dbus.service.method(constants.le_advertisement_interface, in_signature='', out_signature='')
    def Release(self):
        log.info('Advertisement Released')


class Application(dbus.service.Object):
    def __init__(self, bus):
        #self.path = f"/org/test/gatt/application{instance_id}"
        self.path = constants.gatt_application_path

        self.services = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_service(self, service):
        self.services.append(service)

    @dbus.service.method('org.freedesktop.DBus.ObjectManager', out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        response = {}
        for service in self.services:
            response[service.get_path()] = service.get_properties()
            for char in service.get_characteristics():
                response[char.get_path()] = char.get_properties()
                if hasattr(char, "descriptor"):
                    response[char.descriptor.get_path()] = char.descriptor.get_properties()
        return response

#Scan parameter service
class ScanParametersService(dbus.service.Object):
    """Scan Parameters Service (UUID 0x1813)"""

    def __init__(self, bus, index, mainloop):
        self.path = constants.service_path + f"_service{index}"
        self.bus = bus
        self.uuid = constants.scan_parameters_service_uuid
        self.primary = True
        self.mainloop = mainloop
        self.characteristics = []

        self.scan_interval = None
        self.scan_window = None

        dbus.service.Object.__init__(self, bus, self.path)

        self.scan_int_win_char = ScanIntervalWindowCharacteristic(bus, 0, self, mainloop)
        self.characteristics.append(self.scan_int_win_char)

        self.scan_refresh_char = ScanRefreshCharacteristic(bus, 1, self, mainloop)
        self.characteristics.append(self.scan_refresh_char)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def get_properties(self):
        return {
            constants.gatt_service_interface: {
                'UUID': self.uuid,
                'Primary': dbus.Boolean(self.primary),
                'Characteristics': dbus.Array(
                    [c.get_path() for c in self.characteristics], signature='o'
                )
            }
        }

    def get_characteristics(self):
        return self.characteristics


class ScanIntervalWindowCharacteristic(dbus.service.Object):
    """Scan Interval Window Characteristic (UUID 0x2A4F)"""

    def __init__(self, bus, index, service, mainloop):
        self.path = service.get_path() + f"/char{index}"
        self.bus = bus
        self.service = service
        self.uuid = constants.scan_interval_window_uuid
        self.flags = ['write-without-response']
        self.mainloop = mainloop

        dbus.service.Object.__init__(self, bus, self.path)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def get_properties(self):
        return {
            constants.gatt_characteristic_interface: {
                'UUID': self.uuid,
                'Service': self.service.get_path(),
                'Flags': dbus.Array(self.flags, signature='s')
            }
        }

    @dbus.service.method(constants.gatt_characteristic_interface,
                         in_signature='aya{sv}', out_signature='')
    def WriteValue(self, value, options):
        """Client writes scan interval + scan window (4 bytes little endian)"""
        if len(value) != 4:
            log.error("[SPS] Invalid Scan Interval Window size")
            return

        interval = value[0] | (value[1] << 8)
        window = value[2] | (value[3] << 8)

        self.service.scan_interval = interval
        self.service.scan_window = window

        log.info(f"Scan Interval Window updated by client: interval={interval} window={window}")


class ScanRefreshCharacteristic(dbus.service.Object):
    """Scan Refresh Characteristic (UUID 0x2A31)"""

    def __init__(self, bus, index, service, mainloop):
        self.path = service.get_path() + f"/char{index}"
        self.bus = bus
        self.service = service
        self.uuid = constants.scan_refresh_uuid
        self.flags = ['notify']
        self.notifying = False
        self.mainloop = mainloop

        dbus.service.Object.__init__(self, bus, self.path)

        self.descriptor = ScanRefreshDescriptor(bus, 0, self)

        self.refresh_interval_ms = 10000
        GLib.timeout_add(self.refresh_interval_ms, self._refresh_loop)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def get_properties(self):
        return {
            constants.gatt_characteristic_interface: {
                'UUID': self.uuid,
                'Service': self.service.get_path(),
                'Flags': dbus.Array(self.flags, signature='s'),
                'Descriptors': dbus.Array([self.descriptor.get_path()], signature='o')
            }
        }

    @dbus.service.method(constants.gatt_characteristic_interface,
                         in_signature='', out_signature='')
    def StartNotify(self):
        if not self.notifying:
            self.notifying = True
            log.info("Scan Refresh notifications started")

    @dbus.service.method(constants.gatt_characteristic_interface,
                         in_signature='', out_signature='')
    def StopNotify(self):
        if self.notifying:
            self.notifying = False
            log.info("Scan Refresh notifications stopped")

    def send_refresh(self):
        """Notify client that refresh is required (0x00)"""
        if not self.notifying:
            return

        value = [dbus.Byte(0x00)]
        log.info("Sending Scan Refresh notification")
        self.PropertiesChanged(constants.gatt_characteristic_interface, {'Value': value}, [])

    def _refresh_loop(self):
        """Periodic loop to check if client notifications are enabled"""
        if self.notifying:
            self.send_refresh()
        return True

    @dbus.service.signal('org.freedesktop.DBus.Properties',
                         signature='sa{sv}as')
    def PropertiesChanged(self, interface, changed, invalidated):
        pass


class ScanRefreshDescriptor(dbus.service.Object):
    """CCCD for Scan Refresh (Notifications)"""

    def __init__(self, bus, index, characteristic):
        self.path = characteristic.get_path() + f"/desc{index}"
        self.bus = bus
        self.characteristic = characteristic
        self.uuid = constants.client_characteristic_config_uuid
        self.flags = ['read', 'write']

        dbus.service.Object.__init__(self, bus, self.path)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def get_properties(self):
        return {
            constants.gatt_descriptor_interface: {
                'UUID': self.uuid,
                'Characteristic': self.characteristic.get_path(),
                'Flags': dbus.Array(self.flags, signature='s'),
            }
        }

    @dbus.service.method(constants.gatt_descriptor_interface,
                         in_signature='a{sv}', out_signature='ay')
    def ReadValue(self, options):
        return [dbus.Byte(0x00), dbus.Byte(0x00)]

    @dbus.service.method(constants.gatt_descriptor_interface,
                         in_signature='aya{sv}', out_signature='')
    def WriteValue(self, value, options):
        """Enable/disable notifications via CCCD"""
        log.debug(f"Scan Refresh CCCD Write: {value}")

        if len(value) != 2:
            return

        cccd_value = value[0] | (value[1] << 8)

        if cccd_value == 0x0001:
            self.characteristic.StartNotify()
        elif cccd_value == 0x0000:
            self.characteristic.StopNotify()
        else:
            log.warning(f"Unknown CCCD value: {cccd_value}")

#FINDME Profile
class FindMeService(dbus.service.Object):
    """Immediate Alert Service for Find Me Profile (UUID 0x1802)"""

    def __init__(self, bus, index, mainloop):
        self.path = constants.service_path + f"_service{index}"
        self.bus = bus
        self.uuid = constants.immediate_alert_service_uuid
        self.primary = True
        self.mainloop = mainloop
        self.characteristics = []

        dbus.service.Object.__init__(self, bus, self.path)

        self.alert_char = ImmediateAlertCharacteristic(bus, 0, self)
        self.characteristics.append(self.alert_char)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def get_properties(self):
        return {
            constants.gatt_service_interface: {
                'UUID': self.uuid,
                'Primary': dbus.Boolean(self.primary),
                'Characteristics': dbus.Array(
                    [c.get_path() for c in self.characteristics],
                    signature='o'
                )
            }
        }

    def get_characteristics(self):
        return self.characteristics


class ImmediateAlertCharacteristic(dbus.service.Object):
    """Immediate Alert Level Characteristic (UUID 0x2A06)"""

    def __init__(self, bus, index, service):
        self.path = f"{service.get_path()}/char{index}"
        self.bus = bus
        self.service = service
        self.uuid = constants.immediate_alert_uuid
        self.flags = ['write-without-response']
        self.notifying = False
        dbus.service.Object.__init__(self, bus, self.path)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def get_properties(self):
        return {
            constants.gatt_characteristic_interface: {
                'UUID': self.uuid,
                'Service': self.service.get_path(),
                'Flags': dbus.Array(self.flags, signature='s')
            }
        }

    @dbus.service.method(constants.gatt_characteristic_interface, in_signature='aya{sv}', out_signature='')
    def WriteValue(self, value, options):
        if not value:
            log.warning("[FindMeService] Empty write received")
            return
        alert_level = value[0]
        level_map = {0x00: "No Alert", 0x01: "Mild Alert", 0x02: "High Alert"}
        msg = level_map.get(alert_level, "Unknown")
        log.info(f"[FindMeService] Immediate Alert Level Written: {msg}")


class HealthThermometerService(dbus.service.Object):
    def __init__(self, bus, index, mainloop):
        self.path = constants.service_path + f"_ht_service{index}"
        self.bus = bus
        self.uuid = constants.ht_uuid
        self.primary = True
        self.mainloop = mainloop

        dbus.service.Object.__init__(self, bus, self.path)

        self.char_temp_msrmt = TemperatureMeasurementCharacteristic(bus, 0, self, mainloop)
        self.char_int_temp = IntermediateTemperatureCharacteristic(bus, 1, self, mainloop)
        self.char_temp_type = TemperatureTypeCharacteristic(bus, 2, self)
        self.char_interval = MeasurementIntervalCharacteristic(bus, 3, self)

        self.characteristics = [
            self.char_temp_msrmt,
            self.char_int_temp,
            self.char_temp_type,
            self.char_interval,
        ]

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def get_properties(self):
        return {
            constants.gatt_service_interface: {
                "UUID": self.uuid,
                "Primary": dbus.Boolean(self.primary),
                "Characteristics": dbus.Array(
                    [c.get_path() for c in self.characteristics],
                    signature='o'
                )
            }
        }

    def get_characteristics(self):
        return self.characteristics

def encode_ieee_11073(temp):
    exponent = -2
    mantissa = int(temp * 100)

    return struct.pack("<bI", exponent, mantissa & 0xFFFFFF)[0:4]

class HTDescriptor(dbus.service.Object):
    def __init__(self, bus, index, characteristic, text):
        self.path = characteristic.get_path() + f"/desc{index}"
        self.bus = bus
        self.characteristic = characteristic
        self.uuid = constants.desc_uuid
        self.flags = ['read']
        self.text = text.encode()

        dbus.service.Object.__init__(self, bus, self.path)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def get_properties(self):
        return {
            constants.gatt_descriptor_interface: {
                "UUID": self.uuid,
                "Characteristic": self.characteristic.get_path(),
                "Flags": dbus.Array(self.flags, signature='s')
            }
        }

    @dbus.service.method(constants.gatt_descriptor_interface,
                         in_signature='a{sv}', out_signature='ay')
    def ReadValue(self, options):
        return [dbus.Byte(b) for b in self.text]


class TemperatureMeasurementCharacteristic(dbus.service.Object):
    def __init__(self, bus, index, service, mainloop):
        self.path = service.get_path() + f"/char{index}"
        self.bus = bus
        self.service = service
        self.mainloop = mainloop

        self.uuid = constants.ht_msrmt_uuid
        self.flags = ['indicate']
        self.notifying = False

        dbus.service.Object.__init__(self, bus, self.path)

        self.descriptor = HTDescriptor(bus, 0, self, "Temperature Measurement")

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def get_properties(self):
        return {
            constants.gatt_characteristic_interface: {
                "UUID": self.uuid,
                "Service": self.service.get_path(),
                "Flags": dbus.Array(self.flags, signature='s'),
                "Descriptors": dbus.Array([self.descriptor.get_path()], signature='o'),
            }
        }

    @dbus.service.method(constants.gatt_characteristic_interface,
                         in_signature='a{sv}', out_signature='ay')
    def ReadValue(self, options):
        temp = round(random.uniform(35.0, 39.0), 2)
        flags = 0x00
        encoded = encode_ieee_11073(temp)
        return [dbus.Byte(b) for b in bytes([flags]) + encoded]

    @dbus.service.method(constants.gatt_characteristic_interface,
                         in_signature='', out_signature='')
    def StartNotify(self):
        if self.notifying:
            return

        self.notifying = True
        log.info("Temp Measurement Indications Started")
        GLib.timeout_add(3000, self.send_indication)

    @dbus.service.method(constants.gatt_characteristic_interface,
                         in_signature='', out_signature='')
    def StopNotify(self):
        self.notifying = False
        log.info("Temp Measurement Indications Stopped")

    def send_indication(self):
        if not self.notifying:
            return False

        value = self.ReadValue({})
        self.PropertiesChanged(constants.gatt_characteristic_interface,
                               {"Value": value}, [])
        return True

    @dbus.service.signal("org.freedesktop.DBus.Properties",
                         signature="sa{sv}as")
    def PropertiesChanged(self, interface, changed, invalidated):
        pass


class IntermediateTemperatureCharacteristic(dbus.service.Object):
    def __init__(self, bus, index, service, mainloop):
        self.path = service.get_path() + f"/char{index}"

        self.bus = bus
        self.service = service
        self.mainloop = mainloop

        self.uuid = constants.int_temp_uuid
        self.flags = ['notify']
        self.notifying = False

        dbus.service.Object.__init__(self, bus, self.path)

        self.descriptor = HTDescriptor(bus, 0, self, "Intermediate Temperature")

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def get_properties(self):
        return {
            constants.gatt_characteristic_interface: {
                "UUID": self.uuid,
                "Service": self.service.get_path(),
                "Flags": dbus.Array(self.flags, signature='s'),
                "Descriptors": dbus.Array([self.descriptor.get_path()], signature='o')
            }
        }

    @dbus.service.method(constants.gatt_characteristic_interface,
                         in_signature='a{sv}', out_signature='ay')
    def ReadValue(self, options):
        temp = round(random.uniform(35.0, 39.0), 2)
        flags = 0x00
        encoded = encode_ieee_11073(temp)
        return [dbus.Byte(b) for b in bytes([flags]) + encoded]

    @dbus.service.method(constants.gatt_characteristic_interface,
                         in_signature='', out_signature='')
    def StartNotify(self):
        if self.notifying:
            return

        self.notifying = True
        log.info("Intermediate Temp Notifications Started")
        GLib.timeout_add(2000, self.send_notification)

    @dbus.service.method(constants.gatt_characteristic_interface,
                         in_signature='', out_signature='')
    def StopNotify(self):
        self.notifying = False
        log.info("Intermediate Temp Notifications Stopped")

    def send_notification(self):
        if not self.notifying:
            return False

        value = self.ReadValue({})
        self.PropertiesChanged(constants.gatt_characteristic_interface,
                               {"Value": value}, [])
        return True

    @dbus.service.signal("org.freedesktop.DBus.Properties",
                         signature="sa{sv}as")
    def PropertiesChanged(self, interface, changed, invalidated):
        pass


class TemperatureTypeCharacteristic(dbus.service.Object):
    def __init__(self, bus, index, service):
        self.path = service.get_path() + f"/char{index}"

        self.bus = bus
        self.service = service
        self.uuid = constants.temp_type_uuid
        self.flags = ['read']

        dbus.service.Object.__init__(self, bus, self.path)

        self.descriptor = HTDescriptor(bus, 0, self, "Temperature Type")
        self.value = 2  # Body

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def get_properties(self):
        return {
            constants.gatt_characteristic_interface: {
                "UUID": self.uuid,
                "Service": self.service.get_path(),
                "Flags": dbus.Array(self.flags, signature='s'),
                "Descriptors": dbus.Array([self.descriptor.get_path()], signature='o')
            }
        }

    @dbus.service.method(constants.gatt_characteristic_interface,
                         in_signature='a{sv}', out_signature='ay')
    def ReadValue(self, options):
        return [dbus.Byte(self.value)]


class MeasurementIntervalCharacteristic(dbus.service.Object):
    def __init__(self, bus, index, service):
        self.path = service.get_path() + f"/char{index}"

        self.bus = bus
        self.service = service
        self.uuid = constants.interval_uuid
        self.flags = ['read', 'write']

        self.interval = 5

        dbus.service.Object.__init__(self, bus, self.path)

        self.descriptor = HTDescriptor(bus, 0, self, "Measurement Interval")

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def get_properties(self):
        return {
            constants.gatt_characteristic_interface: {
                "UUID": self.uuid,
                "Service": self.service.get_path(),
                "Flags": dbus.Array(self.flags, signature='s'),
                "Descriptors": dbus.Array([self.descriptor.get_path()], signature='o')
            }
        }

    @dbus.service.method(constants.gatt_characteristic_interface,
                         in_signature='a{sv}', out_signature='ay')
    def ReadValue(self, options):
        lo = self.interval & 0xFF
        hi = (self.interval >> 8) & 0xFF
        return [dbus.Byte(lo), dbus.Byte(hi)]

    @dbus.service.method(constants.gatt_characteristic_interface,
                         in_signature='aya{sv}', out_signature='')
    def WriteValue(self, value, options):
        if len(value) != 2:
            log.error("Invalid interval size")
            return

        self.interval = value[0] | (value[1] << 8)
        log.info(f"Measurement Interval Updated: {self.interval}s")


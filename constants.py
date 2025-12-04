adapter_interface = 'org.bluez.Adapter1'
agent_path = '/test/agent'
agent="org.bluez.Agent1"
agent_interface = 'org.bluez.AgentManager1'
bluez_service = 'org.bluez'
bluez_path = '/org/bluez'
device_interface = "org.bluez.Device1"
properties_interface = "org.freedesktop.DBus.Properties"
pulseaudio_command = '/usr/local/bluez/pulseaudio-13.0_for_bluez-5.65/bin/pulseaudio -vvv'
media_control_interface = "org.bluez.MediaControl1"
media_player_interface = "org.bluez.MediaPlayer1"
media_transport_interface = "org.bluez.MediaTransport1"
obex_client = "org.bluez.obex.Client1"
obex_path = "/org/bluez/obex"
obex_service = "org.bluez.obex"
obex_object_push = "org.bluez.obex.ObjectPush1"
obex_object_transfer = "org.bluez.obex.Transfer1"
object_manager_interface = "org.freedesktop.DBus.ObjectManager"
ofono_bus = "org.ofono"
ofono_manager = "org.ofono.Manager"
# Maps device actions to corresponding handler function names.
# The first element in each list is the method name and second element is the handler function name.
device_action_map = {
    "pair": ["pair", "add_paired_device_to_list"],
    "connect": ["connect", "load_device_profile_tabs"],
    "disconnect": ["disconnect", "load_device_profile_tabs"],
    "unpair": ["unpair_device", "remove_device_from_list"]
}

#Maps pairing requests to corresponding handler function names.
#The first element is the pairing request type and the second element is the handler function name.
pairing_request_handlers = {
    "pin": "handle_pin_request",
    "passkey": "handle_passkey_request",
    "confirm": "handle_confirm_request",
    "authorize": "handle_authorize_request",
    "display_pin": "handle_display_pin_request",
    "display_passkey": "handle_display_passkey_request",
    "cancel": "handle_cancel_request",
}

profile_uuids = {
    "A2DP Sink": "0000110b-0000-1000-8000-00805f9b34fb",
    "A2DP Source": "0000110a-0000-1000-8000-00805f9b34fb",
    "OPP": "00001105-0000-1000-8000-00805f9b34fb",
    "HFP AG": "0000111f-0000-1000-8000-00805f9b34fb",
    "HFP HF": "0000111e-0000-1000-8000-00805f9b34fb"
}
#LE services and profiles

gatt_application_path = "/org/test/gatt/application"
gatt_service_interface = 'org.bluez.GattService1'
gatt_characteristic_interface = 'org.bluez.GattCharacteristic1'
gatt_descriptor_interface = 'org.bluez.GattDescriptor1'
client_characteristic_config_uuid = '00002902-0000-1000-8000-00805f9b34fb'
battery_service_uuid = '0000180F-0000-1000-8000-00805f9b34fb'
battery_level_uuid = '00002a19-0000-1000-8000-00805f9b34fb'
battery_level_status_uuid = '00002a1b-0000-1000-8000-00805f9b34fb'
service_path = '/org/test/gatt/service'
application_path = '/org/test/gatt/application'
gatt_manager_interface = 'org.bluez.GattManager1'
le_advertising_manager_interface = 'org.bluez.LEAdvertisingManager1'
le_advertisement_interface = 'org.bluez.LEAdvertisement1'
advertisement_path = '/org/bluez/example/advertisement'
'''scan_parameters_service_uuid = '00001813-0000-1000-8000-00805f9b34fb'
scan_interval_window_uuid = '00002a4f-0000-1000-8000-00805f9b34fb'
scan_refresh_uuid          = '00002a31-0000-1000-8000-00805f9b34fb'''''

# Custom sps uuids
scan_parameters_service_uuid = '12345678-1234-5678-1234-56789abcdef0'
scan_interval_window_uuid = '12345678-1234-5678-1234-56789abcdef1'
scan_refresh_uuid          = '12345678-1234-5678-1234-56789abcdef2'

#Find Me profile uuids
immediate_alert_service_uuid = "1802"
immediate_alert_uuid = "2A06"



int_temp_uuid = '00002A1E-0000-1000-8000-00805F9B34FB'
temp_type_uuid = '00002A1D-0000-1000-8000-00805F9B34FB'
ht_msrmt_uuid = '00002A1C-0000-1000-8000-00805F9B34FB'
ht_uuid = '00001809-0000-1000-8000-00805F9B34FB'
interval_uuid = '00002A21-0000-1000-8000-00805F9B34FB'
desc_uuid = '00002901-0000-1000-8000-00805f9b34fb'

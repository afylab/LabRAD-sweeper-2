""" This file contains list of servers and settings to be ignored by the sweeper (for selecting LabRAD servers and settings) """

# any server whose name ends with "_serial_server" is assumed to be a serial server, and is ignored automatically. No need to add it manually.
SERVERS = [
	"manager",
	"registry",
	"data_vault",
	"virtual_device_server",
	]

# note that signals are automatically excluded. If the setting name begins with 'signal__' it is assumed to be a signal.
SETTINGS = {
	"dcbox_quad_ad5780":["connect","debug","deselect_device","echo","id","initialize","list_devices","lock_device","ready","refresh_devices","release_device","select_device","send_voltage_signals"],
	}

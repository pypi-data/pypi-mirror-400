from dataclasses import dataclass

from py_mdr.ocsf_models.objects.base_model import BaseModel


@dataclass
class KeyboardInformation(BaseModel):
    """
    The Keyboard Information object contains details and attributes related to a computer or device keyboard. It encompasses information that describes the characteristics, capabilities, and configuration of the keyboard.

    Attributes:
    - Function Keys (function_keys) [Optional]: The number of function keys on the client keyboard.
    - IME (ime) [Optional]: The Input Method Editor (IME) file name.
    - Keyboard Layout (keyboard_layout) [Optional]: The keyboard locale identifier name (e.g., en-US).
    - Keyboard Subtype (keyboard_subtype) [Optional]: The keyboard numeric code.
    - Keyboard Type (keyboard_type) [Optional]: The keyboard type (e.g., xt, ico).
    """

    function_keys: int = None
    ime: str = None
    keyboard_layout: str = None
    keyboard_subtype: int = None
    keyboard_type: str = None


@dataclass
class Display(BaseModel):
    """
    The Display object contains information about the physical or virtual display connected to a computer system.

    Attributes:
    - Color Depth (color_depth) [Optional]: The numeric color depth.
    - Physical Height (physical_height) [Optional]: The numeric physical height of the display.
    - Physical Orientation (physical_orientation) [Optional]: The numeric physical orientation of the display.
    - Physical Width (physical_width) [Optional]: The numeric physical width of the display.
    - Scale Factor (scale_factor) [Optional]: The numeric scale factor of the display.
    """

    color_depth: int = None
    physical_height: int = None
    physical_orientation: int = None
    physical_width: int = None
    scale_factor: int = None


@dataclass
class DeviceHardwareInfo(BaseModel):
    """
    The Device Hardware Information object contains details and specifications of the physical components that make up a device. This information provides an overview of the hardware capabilities, configuration, and characteristics of the device.

    Attributes:
    - BIOS Date (bios_date) [Optional]: The BIOS date.
    - BIOS Manufacturer (bios_manufacturer) [Optional]: The BIOS manufacturer.
    - BIOS Version (bios_ver) [Optional]: The BIOS version.
    - CPU Bits (cpu_bits) [Optional]: The number of bits used for addressing in memory.
    - CPU Cores (cpu_cores) [Optional]: The number of processor cores in all installed processors.
    - CPU Count (cpu_count) [Optional]: The number of physical processors on a system.
    - Chassis (chassis) [Optional]: The system enclosure or physical form factor.
    - Desktop Display (desktop_display) [Optional]: The desktop display affiliated with the event.
    - Keyboard Information (keyboard_info) [Optional]: Detailed information about the keyboard.
    - Processor Speed (cpu_speed) [Optional]: The speed of the processor in Mhz.
    - Processor Type (cpu_type) [Optional]: The processor type.
    - RAM Size (ram_size) [Optional]: The total amount of installed RAM, in Megabytes.
    - Serial Number (serial_number) [Optional]: The device manufacturer serial number.
    """

    bios_date: str = None
    bios_manufacturer: str = None
    bios_ver: str = None
    cpu_bits: int = None
    cpu_cores: int = None
    cpu_count: int = None
    chassis: str = None
    desktop_display: str = None
    keyboard_info: str = None
    cpu_speed: int = None
    cpu_type: str = None
    ram_size: int = None
    serial_number: str = None

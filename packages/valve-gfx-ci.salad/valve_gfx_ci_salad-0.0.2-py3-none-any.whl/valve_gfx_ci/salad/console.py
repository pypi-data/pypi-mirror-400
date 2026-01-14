from .logger import logger

from functools import cached_property
from pathlib import Path
import threading
import traceback
import serial
import socket
import time
import os
import re


class ConsoleStream(threading.Thread):
    def __init__(self, salad, stream_name):
        super().__init__(name=f'ConsoleStream-{stream_name}')

        self.salad = salad
        self.stream_name = stream_name

        self.machine = None

        self._line_buffer = b""

        self.machine_id_re = \
            re.compile(b"SALAD.machine_id=(?P<machine_id>\\S+)")

        # NOTE: Some adapters send garbage at first, so don't assume
        # the ping is at the first byte offset (i.e., do not think you
        # can anchor to ^), sometimes '\x00\x00SALAD.ping' is seen,
        # othertimes '\xfcSALAD.ping', and so on.
        self.ping_re = re.compile(b"SALAD.ping\r?")

        self._is_valid = True
        self.start()

    @property
    def console_id(self):
        # Return an identifier that identifies the console across hotplug events (like USB paths), or None.
        return None

    @property
    def machine_id(self):
        return self.machine.id if self.machine is not None else None

    @property
    def is_valid(self):
        return self._is_valid

    def log_msg(self, data, is_input=True):
        mid = "UNKNOWN" if self.machine is None else self.machine.id
        dir = f"{mid} <--" if is_input else f"{self.name} <--"
        logger.info(f"{dir} {data}")

    def close(self):
        # To be implemented by the children of this class
        logger.error(f"WARNING: The console '{self.stream_name}' does not implement the close() method")
        self._is_valid = False

    def _send(self, data):  # pragma: nocover
        # To be implemented by the children of this class
        logger.error(f"WARNING: The console '{self.stream_name}' does not implement the _send() method")

    def reset(self):
        # To be implemented by the children of this class
        raise NotImplementedError("Resetting unsupported")

    def send(self, data):
        self.log_msg(data, is_input=False)
        try:
            self._send(data)
        except Exception:
            logger.error(traceback.format_exc())
            self.close()
            return

    def _recv(self, buf_size):  # pragma: nocover
        # To be implemented by the children of this class
        logger.error(f"WARNING: The console '{self.stream_name}' does not implement the _recv() method")
        return b''

    def associate_machine(self, machine_id: str | None):
        if machine_id:
            self.machine = self.salad.get_or_create_machine(machine_id, owner_console_id=self.console_id)

    def process_input_line(self, line):
        # Check if the new line indicate for which machine the stream is for
        m = self.machine_id_re.search(line)
        if m:
            # We found a machine!
            new_machine_id = m.groupdict().get('machine_id').decode()

            # Make sure users are aware when the ownership of a console changes
            if self.machine is not None and new_machine_id != self.machine.id:  # pragma: nocover
                logger.warning((f"WARNING: The console {self.stream_name}'s associated "
                                f"machine changed from {self.machine_id} "
                                f"to {new_machine_id}"))
            elif self.machine is None:
                logger.warning((f"NOTE: The console {self.stream_name} is now associated "
                                f"to {new_machine_id}."))

            # Make the new machine the associated machine of this session
            self.associate_machine(new_machine_id)

        self.log_msg(line)

        if self.ping_re.search(line):
            self.send(b"SALAD.pong\n")

    def stop(self):
        self.close()
        self.join()

    def run(self):
        while self.is_valid:
            try:
                data = self._recv(4096)
                if len(data) == 0:
                    continue
            except Exception:
                if self.is_valid:
                    logger.error(traceback.format_exc())
                    self.close()
                return

            # Perform our line-by-line processing before sending the data to the client
            lines = (self._line_buffer + data).split(b'\n')
            self._line_buffer = lines.pop()  # Keep the current line in the line buffer
            for line in lines:
                self.process_input_line(line)

            # Now that we may have associated the data to a machine, send the data to the clients
            if self.machine:
                self.machine.send_to_clients(data)


class UsbPort:
    def __init__(self, path: Path):
        self.path = path

        if not (path / "port").is_dir():
            raise ValueError("The path is not a valid USB port")

    @property
    def name(self):
        return self.path.name

    @property
    def bNumInterfaces(self) -> int | None:
        path = (self.path / "bNumInterfaces").resolve()

        if path.exists():
            try:
                return int(path.read_text().strip())
            except ValueError:
                pass

        return None

    def reset(self):
        disable_path = (self.path / "port" / "disable").resolve()

        if not disable_path.exists():
            # TODO: Add support for USB reset, for cases where the USB hub doesn't support PPPS
            raise ValueError("The serial console is not connected to a USB hub supporting Per-Port Power Switching")

        if os.environ.get("SALAD_CONSOLE_USB_RESET_DISABLE", "0") == "1":
            raise ValueError("The serial console reset is disabled by the farm admin")

        if self.bNumInterfaces != 1:
            raise ValueError("The serial console is part of a multi-interface USB device")

        # Compute the sleep time ahead of disabling the port, in case it fails
        sleep_time = 3
        try:
            sleep_time = int(os.environ.get("SALAD_CONSOLE_USB_RESET_POWER_OFF_TIME", sleep_time))
        except ValueError:
            pass

        # Perform the reset
        disable_path.write_text("1\n")
        time.sleep(sleep_time)
        disable_path.write_text("0\n")


class SerialConsoleStream(ConsoleStream):
    def __init__(self, salad, stream_name, dev):
        self.serial_dev = dev
        self.device = serial.VTIMESerial(self.serial_dev, baudrate=115200, timeout=0.2)

        super().__init__(salad, stream_name)

    @property
    def is_valid(self):
        return self.device is not None

    @cached_property
    def device_sysfs_path(self) -> Path:
        return (Path("/sys/class/tty") / Path(self.serial_dev).name).resolve()

    @cached_property
    def usb_port(self) -> UsbPort | None:
        if "usb" not in str(self.device_sysfs_path):
            return None

        # The port is located in a parent folder, so let's try to find the first parent folder that is a valid USB port
        sysfs_path = self.device_sysfs_path
        while sysfs_path != sysfs_path.root:
            sysfs_path = sysfs_path.parent

            try:
                return UsbPort(sysfs_path)
            except ValueError:
                pass

    @cached_property
    def console_id(self) -> str | None:
        port_sysfs_path = self.device_sysfs_path

        # For PIO-based serial ports, just return the `port` property
        try:
            if console_id := (port_sysfs_path / "port").read_text().strip():
                return console_id
        except OSError:
            pass
        except Exception:
            traceback.print_exc()

        # Handle USB devices
        if usb_port := self.usb_port:
            return usb_port.name

        return None

    def _send(self, data):
        if self.device:
            os.write(self.device.fd, data)

    def _recv(self, buf_size=4096):
        if self.device:
            return os.read(self.device.fd, buf_size)
        else:
            return b''

    def reset(self):
        if usb_port := self.usb_port:
            usb_port.reset()
        else:
            raise ValueError("Reset only supported on USB-based consoles")

    def close(self):
        if self.device:
            logger.info("Closing the %s serial port", self.serial_dev)
            device = self.device
            self.device = None
            device.close()


class TCPConsoleStream(ConsoleStream):
    def __init__(self, salad, stream_name, sock):
        logger.info("Opening %s", stream_name)
        self.sock = sock

        super().__init__(salad, stream_name)

    @property
    def is_valid(self):
        return self.sock is not None

    def _send(self, data):
        if self.sock:
            self.sock.sendall(data)

    def _recv(self, buf_size=4096):
        if self.sock:
            data = self.sock.recv(buf_size)
            if len(data) == 0:
                self.close()
            return data
        else:
            return b''

    def close(self):
        if self.sock:
            logger.info("Closing %s", self.stream_name)
            sock = self.sock
            self.sock = None
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()

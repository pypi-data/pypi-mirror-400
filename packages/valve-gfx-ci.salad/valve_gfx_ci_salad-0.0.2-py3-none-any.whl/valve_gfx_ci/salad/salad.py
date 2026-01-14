from collections import defaultdict
from threading import Thread
from .logger import logger

from .console import SerialConsoleStream
from .tcpserver import TCPLogServer, TCPNetconsoleServer

import os
import serial.tools.list_ports
import threading
import traceback


class Machine:
    def __init__(self, salad, machine_id):
        self.salad = salad
        self.id = machine_id

        self.server = TCPLogServer(salad, machine_id, rw=True)
        self.server_for_logs = TCPLogServer(salad, machine_id, rw=False)

        self.__clients_lock = threading.RLock()
        self.__clients = list()

        self.__console_lock = threading.Lock()
        self._console = None

    def stop(self):
        with self.__clients_lock:
            self.server.stop()
            self.server_for_logs.stop()

            for client in list(self.__clients):
                client.close()

            # Make sure our close() call removed the clients from the list of clients
            assert len(self.__clients) == 0

    @property
    def rw_client(self):
        with self.__clients_lock:
            for client in self.__clients:
                if client.rw:
                    return client
        return None

    @property
    def has_rw_client(self):
        return self.rw_client is not None

    @property
    def console(self):
        with self.__console_lock:
            # Ensure the console is still the right one for us
            if self._console is None or not self._console.is_valid or self._console.machine.id != self.id:
                self._console = self.salad.find_console_for_machine(self.id)

            return self._console

    def register_client(self, client):
        with self.__clients_lock:
            if client.rw and self.rw_client:
                raise ValueError("A client is already connected, re-try later!")

            self.__clients.append(client)

    def remove_client(self, client):
        with self.__clients_lock:
            try:
                self.__clients.remove(client)
            except ValueError:
                pass

    def send_to_machine(self, data):
        if console := self.console:
            console.send(data)

    def send_to_clients(self, data):
        with self.__clients_lock:
            for client in self.__clients:
                client.send(data)


class Salad(Thread):
    def __init__(self):
        super().__init__(name='SaladThread')
        self._stop_event = threading.Event()

        self.netconsole_server = TCPNetconsoleServer(self, os.getenv("SALAD_TCPCONSOLE_PORT", 8006))

        # List of all the consoles
        self.__consoles_lock = threading.RLock()
        self.__consoles = dict()
        self.__console_id_to_machine_id = dict()

        # Machines to Console association
        self.__machines_lock = threading.RLock()
        self.__machines = dict()

    def stop(self):
        # Signal for the main thread to stop polling for new devices
        self._stop_event.set()

        # Stop the netconsole TCP server
        self.netconsole_server.stop()

        # Stop all the Machine-related TCP servers
        with self.__machines_lock:
            for machine in self.__machines.values():
                machine.stop()
            self.__machines.clear()

        # Close all the consoles
        with self.__consoles_lock:
            for console in self.__consoles.values():
                if console:
                    console.stop()
            self.__consoles.clear()

        # Wait for the main thread to be over
        self.join()

    # Machines
    @property
    def machines(self):
        with self.__machines_lock:
            return list(self.__machines.values())

    def get_or_create_machine(self, machine_id, owner_console_id: str = None):
        with self.__machines_lock:
            machine = self.__machines.get(machine_id)
            if not machine:
                machine = Machine(self, machine_id)
            self.__machines[machine_id] = machine

            # Update the owning console id, if the information is known
            if owner_console_id:
                self.__console_id_to_machine_id[owner_console_id] = machine

            return machine

    # Consoles
    def add_console(self, console):
        with self.__consoles_lock:
            if console.stream_name in self.__consoles:
                raise ValueError("A console with the same name already exists")

            self.__consoles[console.stream_name] = console

            # If the console has a static identifier, check our console_id -> machine mapping
            # in case we already know this console and its previous association
            if console_id := console.console_id:
                if machine := self.__console_id_to_machine_id.get(console_id):
                    logger.info(f"Re-associating the {console.stream_name} console to {machine.id}")
                    console.associate_machine(machine.id)

    def mark_port_as_broken(self, port):
        with self.__consoles_lock:
            if port in self.__consoles:
                raise ValueError("A console with the same name already exists")

            self.__consoles[port] = None

    def find_console_for_machine(self, machine_id):
        with self.__consoles_lock:
            for console in self.__consoles.values():
                if console and console.machine_id == machine_id:
                    return console

    # Thread
    def run(self):
        # Upon hotplugging, serial ports may not be immediately available to SALAD due to a variety of reasons such as
        # udev not having had the time to update the permissions. Rather than failing immediately, let's keep track of
        # our instantiation attempts so that we may retry up to N times.
        port_failures = defaultdict(int)

        while not self._stop_event.is_set():
            with self.__consoles_lock:
                # Make sure all our consoles are valid
                for port, console in dict(self.__consoles).items():
                    try:
                        if console and not console.is_valid:
                            console.stop()
                            del self.__consoles[port]
                    except Exception:
                        logger.error(traceback.format_exc())

                # Enumerate the consoles plugged
                try:
                    cur_ports = {p.device for p in serial.tools.list_ports.comports()}

                    # Remove all the ports that got disconnected
                    for port in set(self.__consoles.keys()) - cur_ports:
                        if not port.startswith("/dev/"):
                            continue

                        try:
                            logger.info(f"The serial device {port} got removed")
                            if console := self.__consoles.pop(port):
                                console.close()

                            # Reset the failure counter for the port
                            port_failures.pop(port, None)
                        except Exception:
                            logger.error(traceback.format_exc())

                    # Add any port that we do not have
                    for port in cur_ports - set(self.__consoles.keys()):
                        try:
                            console = SerialConsoleStream(self, port, port)
                            self.add_console(console)

                            attempts = port_failures.pop(port, 0)
                            logger.info((f"Found new serial device {port} ({console.console_id or "No Console ID"}), "
                                         f"after {attempts} attempts"))
                        except Exception:
                            # Increment the port's failure counter
                            port_failures[port] += 1

                            # Show the error message if we ran out of attempts
                            if port_failures[port] >= 5:
                                logger.error((f"ERROR: Could not allocate a stream for the serial port {port}: "
                                              f"{traceback.format_exc()}"))
                                self.mark_port_as_broken(port)

                except Exception:
                    logger.error(traceback.format_exc())

            # Wait up to a second
            self._stop_event.wait(timeout=1.0)


salad = Salad()

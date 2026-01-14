from .console import TCPConsoleStream
from .logger import logger

import traceback
import threading
import socket


class Client(threading.Thread):
    def __init__(self, salad, machine_id, sock, rw=False):
        super().__init__(name=f'Client-{"rw" if rw else "ro"}-{machine_id}')

        self.salad = salad
        self.machine_id = machine_id
        self.sock = sock
        self.rw = rw

        self.machine = self.salad.get_or_create_machine(machine_id)
        self.machine.register_client(self)

        if self.rw:
            self.start()
        else:
            # Advertise to the client that we will not be reading anything
            self.sock.shutdown(socket.SHUT_RD)

    # Public interface
    def close(self):
        if self.sock is None:
            return

        try:
            sock = self.sock
            self.sock = None

            if sock:
                sock.shutdown(socket.SHUT_RDWR)
                sock.close()
        except Exception as e:
            if type(e) is not OSError or e.errno != 107:
                logger.warning(traceback.format_exc())

        try:
            self.machine.remove_client(self)
        except Exception:
            logger.warning(traceback.format_exc())

    # Machine -> Client
    def send(self, data):
        try:
            self.sock.send(data)
        except Exception:
            if self.sock:
                logger.warning(traceback.format_exc())
                self.close()

    def run(self):
        try:
            while self.sock:
                try:
                    data = self.sock.recv(4096)
                except Exception:
                    if self.sock:
                        logger.warning(traceback.format_exc())
                    break

                if len(data) == 0:
                    break

                self.machine.send_to_machine(data)
        except Exception:
            logger.warning(traceback.format_exc())

        self.close()


class TCPServer(threading.Thread):
    def __init__(self, name, endpoint=('', 0), queue_size=100):
        super().__init__(name=name)

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)      # Allow quick rebinding after restart
        self.server.bind(endpoint)
        self.server.listen(queue_size)

        self.start()

    @property
    def port(self):
        return self.server.getsockname()[1]

    def close(self):
        server = self.server
        self.server = None

        if server:
            try:
                server.shutdown(socket.SHUT_RDWR)
            except (OSError, Exception) as e:
                if not type(e) is OSError or e.errno != 107:
                    logger.warning(traceback.format_exc())
            finally:
                server.close()

    def stop(self):
        self.close()
        self.join()

    def new_client(self, sock, address):
        raise NotImplementedError()

    def run(self):
        while True:
            try:
                sock, address = self.server.accept()
            except (OSError, Exception) as e:
                if not type(e) is OSError or e.errno != 22:
                    logger.error(traceback.format_exc())
                self.close()
                return

            try:
                self.new_client(sock, address)
            except Exception:
                logger.warning(traceback.format_exc())


class TCPLogServer(TCPServer):
    def __init__(self, salad, machine_id, rw=False):
        self.salad = salad
        self.machine_id = machine_id
        self.rw = rw

        super().__init__(name=f'TCPLogServer-{"rw" if rw else "ro"}-{machine_id}')

    def new_client(self, sock, address):
        try:
            Client(self.salad, self.machine_id, sock, rw=self.rw)
        except Exception as e:
            logger.warning(traceback.format_exc())

            # Close the socket
            sock.send(b"ERROR: " + str(e).encode() + b"\r\n")
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()


class TCPNetconsoleServer(TCPServer):
    def __init__(self, salad, port):
        self.salad = salad
        super().__init__(name='TCPNetconsoleServer', endpoint=('', port))

    def new_client(self, sock, address):
        stream_name = 'netconsole@%s:%d' % address
        console = TCPConsoleStream(self.salad, stream_name, sock)
        self.salad.add_console(console)

from unittest.mock import patch, MagicMock, call
import socket

from salad.console import ConsoleStream, SerialConsoleStream, TCPConsoleStream


def test_ConsoleStream():
    salad = MagicMock()
    stream_name = "consoleName"

    ConsoleStream._recv = MagicMock(side_effect=[b'hello w', b'orld\nSALAD.ping\r\nSALAD.machine_id=machine1\ninterr', b'upted line...', b'', OSError()])
    ConsoleStream._send = MagicMock()
    salad.get_or_create_machine.return_value.id = "machine1"

    con = ConsoleStream(salad, stream_name)
    con.join()

    # Check that the init values are kept
    assert con.salad == salad
    assert con.stream_name == stream_name

    # Make sure the execution finished properly
    assert con._line_buffer == b"interrupted line..."
    assert not con.is_valid

    # Make sure the machine was detected
    assert con.machine_id == "machine1"
    assert con.machine == salad.get_or_create_machine.return_value
    salad.get_or_create_machine.assert_called_with("machine1", owner_console_id=None)

    # Make sure we answered the ping with a pong
    assert ConsoleStream._send.call_args_list == [call(b"SALAD.pong\n")]

    # Try sending data, but an exception happened
    ConsoleStream._send = MagicMock(side_effect=OSError())
    ConsoleStream.close = MagicMock()
    ConsoleStream.close.assert_not_called()
    data = b"My message"
    con.send(data)
    ConsoleStream._send.assert_called_with(data)
    ConsoleStream.close.assert_called_with()

    # Not much testing there, but at least we make sure the function exists :D
    con.stop()


@patch("salad.console.serial")
@patch("os.write")
@patch("os.read")
def test_SerialConsoleStream(read_mock, write_mock, serial_mock):
    con = SerialConsoleStream(None, "Helloworld", "/dev/mydev")

    assert con.serial_dev == "/dev/mydev"
    assert con.device == serial_mock.VTIMESerial.return_value

    serial_mock.VTIMESerial.assert_called_with(con.serial_dev, baudrate=115200, timeout=0.2)
    device_mock = serial_mock.VTIMESerial.return_value

    # Test send()
    data = b"mydata"
    write_mock.assert_not_called()
    con._send(data)
    write_mock.assert_called_with(con.device.fd, data)

    # Test recv()
    read_mock.return_value = b"hello world2"
    assert con._recv(4096) == read_mock.return_value
    read_mock.assert_called_with(con.device.fd, 4096)

    # Test close()
    assert con.is_valid
    device_mock.close.assert_not_called()
    con.close()
    device_mock.close.assert_called_with()
    assert not con.is_valid

    # Make sure further read/writes are nops
    con._send(b"blabla")
    assert con._recv(4096) == b''


def test_TCPConsoleStream():
    sock = MagicMock()
    sock.recv.return_value = b"hello world\n"
    con = TCPConsoleStream(None, "Helloworld", sock)

    assert con.sock == sock

    # Test send()
    data = b"mydata"
    sock.sendall.assert_not_called()
    con._send(data)
    sock.sendall.assert_called_with(data)

    # Test recv()
    assert con._recv(4096) == sock.recv.return_value
    sock.recv.assert_called_with(4096)

    # Test close()
    assert con.is_valid
    sock.shutdown.assert_not_called()
    sock.close.assert_not_called()
    con.close()
    sock.shutdown.assert_called_with(socket.SHUT_RDWR)
    sock.close.assert_called_with()
    assert not con.is_valid

    # Make sure further read/writes are nops
    con._send(b"blabla")
    assert con._recv(4096) == b''

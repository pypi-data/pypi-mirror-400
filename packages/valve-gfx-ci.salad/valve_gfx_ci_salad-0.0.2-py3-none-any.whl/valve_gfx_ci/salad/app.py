#!/usr/bin/env python3

from .salad import salad, Machine
from waitress import serve

import socket
import flask
import json
import os


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Machine):
            return {
                "id": obj.id,
                "tcp_port": obj.server.port,
                "has_client": obj.has_rw_client,
                "tcp_port_logs": obj.server_for_logs.port,
            }

        return super().default(self, obj)


class CustomJSONProvider(flask.json.provider.JSONProvider):
    def dumps(self, obj, *args, **kwargs):
        return json.dumps(obj, cls=CustomJSONEncoder, *args, **kwargs)

    def loads(self, s, **kwargs):
        return json.loads(s)


app = flask.Flask(__name__)
app.json = CustomJSONProvider(app)


@app.route('/api/v1/machine', methods=['GET'])
def machines():
    return {
        "machines": dict([(m.id, m) for m in salad.machines]),
    }


@app.route('/api/v1/machine/<machine_id>', methods=['GET'])
def machine_id(machine_id):
    machine = salad.get_or_create_machine(machine_id)
    return CustomJSONEncoder().default(machine)


@app.route('/api/v1/machine/<machine_id>/reset', methods=['POST'])
def machine_console_reset(machine_id):
    machine = salad.get_or_create_machine(machine_id)

    if console := machine.console:
        try:
            console.reset()
            return flask.Response(response="Reset executed successfully", status=200)
        except NotImplementedError:
            return flask.Response(response="Reset unsupported on this console", status=501)  # Not Implemented
        except Exception as e:
            return flask.Response(response=str(e), status=503)  # Service Unavailable
    else:
        return flask.Response(response="No console associated", status=501)  # Not Implemented


def socket_activated_sockets():
    def socket_from_fd(fd):
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM, fileno=fd)

    # Ignore any FDs that were not meant for us
    if os.environ.get('LISTEN_PID', None) != str(os.getpid()):
        return []

    try:
        listen_fds_nr = int(os.getenv("LISTEN_FDS"))
    except Exception:
        return []

    FIRST_SOCKET_FD = 3
    return [socket_from_fd(FIRST_SOCKET_FD + i) for i in range(listen_fds_nr)]


def run():
    salad.start()
    if listen_sockets := socket_activated_sockets():
        serve(app, sockets=listen_sockets, asyncore_use_poll=True)
    else:
        serve(app, port=int(os.getenv("SALAD_PORT", "8005")), asyncore_use_poll=True)
    salad.stop()


if __name__ == '__main__':  # pragma: nocover
    run()

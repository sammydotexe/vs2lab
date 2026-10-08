"""
Client and server using classes
"""

import logging
import socket
from unittest.mock import call

import const_cs
from context import lab_logging

lab_logging.setup(stream_level=logging.INFO)  # init loging channels for the lab

# pylint: disable=logging-not-lazy, line-too-long

class Server:
    """ The server """
    _logger = logging.getLogger("vs2lab.lab1.clientserver.Server")
    _serving = True
    dictionary = {"Hans": "1234", "Peter": "5678", "Klaus": "9876", "Sophie": "4321", "Anna": "1111", "Lena": "2222", "Max": "3333", "Tom": "4444", "Lisa": "5555", "Julia": "6666"}

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # prevents errors due to "addresses in use"
        self.sock.bind((const_cs.HOST, const_cs.PORT))
        self.sock.settimeout(3)  # time out in order not to block forever
        self._logger.info("Server bound to socket " + str(self.sock))

    def Get(self, name):
        """ Handle Get request """
        if isinstance(name, bytes):
            name = name.decode('ascii')
        if name in self.dictionary:
            self._logger.info("Found " + name + " in dictionary.")
            return self.dictionary[name]
        else:
            self._logger.info("Did not find " + name + " in dictionary.")
            return "Not found"
        pass    

    def GetAll(self):
        """ Handle GetAll request """
        self._logger.info("Returning all entries in dictionary.")
        return "\n".join([f"{name}: {number}" for name, number in self.dictionary.items()])

    def serve(self):
        """ Serve echo """
        self.sock.listen(1)
        while self._serving:  # as long as _serving (checked after connections or socket timeouts)
            try:
                # pylint: disable=unused-variable
                (connection, address) = self.sock.accept()  # returns new socket and address of client
                while True:  # forever
                    data = connection.recv(1024)  # receive data from client
                    if not data:
                        break  # stop if client stopped
                    if data.startswith(b"1"):
                        # Handle Get request
                        self._logger.info("Received Get request for name: " + data[1:].decode('ascii'))
                        name = data[1:].decode('ascii')
                        connection.send(self.Get(name).encode('ascii')) # return number for name
                    elif data.startswith(b"2"):
                        # Handle GetAll request
                        self._logger.info("Received GetAll request.")
                        connection.send(self.GetAll().encode('ascii')) # return all entries in dictionary
                    else:
                        # Handle invalid request
                        self._logger.info("Received invalid request. Fallback to echoing back the data.")
                        connection.send(data[1:] + " is an invalid input".encode('ascii'))  # return sent data plus an "*"
                connection.close()  # close the connection
            except socket.timeout:
                pass  # ignore timeouts
        self.sock.close()
        self._logger.info("Server down.")


class Client:
    """ The client """
    logger = logging.getLogger("vs2lab.a1_layers.clientserver.Client")

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((const_cs.HOST, const_cs.PORT))
        self.logger.info("Client connected to socket " + str(self.sock))

    def message(self):
        """ Ask user for message to send """
        msg_type = input("Enter Get or GetAll: ")
        if msg_type == "Get":
            name = input("Enter Name to search for: ")
            msg_in = b"1" + name.encode('ascii')
        elif msg_type == "GetAll":
            msg_in = b"2"
        else:
            msg_in = b"0"+msg_type.encode('ascii')  # invalid request
        self.call(msg_in)

    def call(self, msg_in):
        """ Call server """
        if isinstance(msg_in, str):
            msg_in = msg_in.encode('ascii')

        self.sock.send(msg_in)  # send encoded data
        data = self.sock.recv(1024)  # receive the response
        msg_out = data.decode('ascii')
        print(msg_out)  # print the result
        self.sock.close()  # close the connection
        self.logger.info("Client down.")
        return msg_out

    

    def close(self):
        """ Close socket """
        self.sock.close()

# A module for streaming .wav files.
# Usage: python audiostreamer.py filename host:port

import sys
import wave
import socket
import pickle
import time


class AudioStreamer:
    def __init__(self, filename, address=None, n_frames=None):
        self.filename = filename
        self.wav = wave.open(filename, 'rb')
        self.params = self.wav.getparams()
        # Number of frames to send in each transfer.
        if n_frames is not None:
            self.n_frames = n_frames
        else:
            self.n_frames = 1024
        if address is not None:
            try:
                self.hostname, self.port = address.split(':')
                self.port = int(self.port)
            except ValueError:
                print('No port given. Defaulting to port 6000.')
                self.hostname = address
                self.port = 6000
        else:
            self.hostname = 'localhost'
            self.port = 6000
        # Create a socket connection for connecting to the server:
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.hostname, self.port))
        # Send data
        self.send_params()
        time.sleep(0.1)  # Something is not blocking correctly. This sleep fixes it...
        self.send_data()

    def send_params(self):
        # Send the params pickled.
        params_send = pickle.dumps(self.params)
        self.client_socket.send(params_send)

    def send_data(self):
        data = self.wav.readframes(self.n_frames)
        while data != b'':
            self.client_socket.send(data)
            data = self.wav.readframes(self.n_frames)


if __name__ == '__main__':
    # Read filename and host from command line.
    # Filename includes path relative to run directory.
    filename = sys.argv[1]
    # Host is in the format address:port.
    host = sys.argv[2]
    # Initialize AudioStreamer
    streamer = AudioStreamer(filename, host)

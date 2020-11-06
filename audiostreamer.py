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
            self.hostname, self.port = address.split(':')
            self.port = int(self.port)
        else:
            self.hostname = 'localhost'
            self.port = 6000
        # Create a socket connection for connecting to the server:
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.hostname, self.port))
        # Send data
        self.send_params()
        time.sleep(0.1)  # Something is not blocking correctly. This sleep fixes it.
        self.send_data()

    def send_params(self):
        # Send the params pickled.
        params_send = pickle.dumps(self.params)
        self.client_socket.send(params_send)

    def send_data(self):
        data = self.wav.readframes(self.n_frames)
        print(len(data))
        while data != b'':
            self.client_socket.send(data)
            data = self.wav.readframes(self.n_frames)


if __name__ == '__main__':
    #filename = 'wav/AnnaBlanton_Rachel_Full/06_Violin.wav'
    filename = 'wav/Secretariat_Homebound/01_VoxBanjo.wav'
    #filename = 'wav/Secretariat_Homebound/02_VoxGuitar.wav'

    # Initialize AudioStreamer
    #host = "192.168.1.88:6000"
    host = "62.249.189.110:6000"
    streamer = AudioStreamer(filename, host)

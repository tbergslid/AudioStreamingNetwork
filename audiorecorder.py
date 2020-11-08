# A module for receiving, playing, and saving .wav files.
# Usage: python audiorecorder.py port

import sys
import pyaudio
import wave
import socket
import pickle
import time


class AudioRecorder:
    def __init__(self, port=None, n_frames=None):
        # Number of frames to receive in each transfer.
        if n_frames is not None:
            self.n_frames = n_frames
        else:
            self.n_frames = 1024
        self.audiobuffer = b''
        self.p = pyaudio.PyAudio()
        self.client_sockets = []
        self.address = []
        self.countConnections = -1
        # params is a _wave_params tuple with the following elements:
        # 0: nchannels, 1: sampwidth, 2: framerate, 3: nframes, 4: comptype, 5: compname
        self.params = []
        if port is not None:
            self.port = port
        else:
            self.port = 6000
        # Setup the listening socket.
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('', self.port))
        # Only receive one connection at a time.
        self.server_socket.listen(1)
        print("Your IP address is: ", socket.gethostbyname(socket.gethostname()))
        print("Server waiting for client on port ", self.port)

    def accept_connection(self):
        client_socket, address = self.server_socket.accept()
        self.client_sockets.append(client_socket)
        self.address.append(address)
        self.countConnections += 1

    def receive_params(self):
        params = self.client_sockets[self.countConnections].recv(128)
        # Convert the parameters back to a tuple.
        self.params = pickle.loads(params)
        print(self.params)

    def receive_and_play(self):
        # Clear the audiobuffer when receiving a new stream.
        self.audiobuffer = b''
        audioChunkSize = self.params[0] * self.params[1] * self.n_frames
        stream = self.p.open(format=self.p.get_format_from_width(self.params[1]),
                             channels=self.params[0], rate=self.params[2],
                             frames_per_buffer=2048,
                             output=True)
        packetCount = 0
        # Receive data from audiostreamers...
        while True:
            try:
                # Receive the data in chunks.
                data = self.client_sockets[self.countConnections].recv(audioChunkSize)
                # ...until there is no more data to receive.
                if data == b'':
                    print('Received {:d} packets from address {:s}.'.format(packetCount,
                                                                            self.address[self.countConnections][0]))
                    break
                # Play the received data.
                stream.write(data, self.n_frames)
                self.audiobuffer += data
                packetCount += 1
            except OSError as e:
                print(e.strerror)
                break
        self.client_sockets[self.countConnections].close()

    def write_wav(self, filename):
        wav_out = wave.open(filename, 'wb')
        wav_out.setparams(self.params)
        wav_out.writeframes(self.audiobuffer)


if __name__ == '__main__':
    # Read port from command line.
    port = int(sys.argv[1])
    try:
        dir_out = sys.argv[2]
    except IndexError:
        dir_out = ''
        print('No output directory specified. Writing file to current folder.')

    recorder = AudioRecorder(port)
    # Listen for new input until program is stopped.
    # Input will be written to wav file after each transfer is completed.
    while True:
        recorder.accept_connection()
        recorder.receive_params()
        time.sleep(0.1)  # Something is not blocking correctly. This sleep fixes it...
        recorder.receive_and_play()
        file_out = dir_out + 'output-' + str(recorder.countConnections) + '.wav'
        recorder.write_wav(file_out)

import pyaudio
import wave
import socket
import threading
import pickle
import time


class AudioRecorder:
    def __init__(self, port=None, n_frames=None):
        # Number of frames to receive in each transfer.
        if n_frames is not None:
            self.n_frames = n_frames
        else:
            self.n_frames = 1024
        self.audiobuffer = []
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
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('', self.port))
        self.server_socket.listen(1)
        print("Your IP address is: ", socket.gethostbyname(socket.gethostname()))
        print("Server waiting for client on port ", self.port)

    def accept_connection(self):
        client_socket, address = self.server_socket.accept()
        self.client_sockets.append(client_socket)
        self.address.append(address)
        self.countConnections += 1

    def receive_params(self):
        self.params, server = self.client_sockets[self.countConnections].recvfrom(256)
        # Convert the parameters back to a tuple.
        self.params = pickle.loads(self.params)
        print(self.params)

    def receive_and_play(self):
        # Clear the audiobuffer when receiving a new stream.
        self.audiobuffer = []
        audioChunkSize = self.params[0] * self.params[1] * self.n_frames
        stream = self.p.open(format=self.p.get_format_from_width(self.params[1]),
                             channels=self.params[0], rate=self.params[2],
                             frames_per_buffer=2048,
                             output=True)
        #data, server = self.client_sockets[self.countConnections].recvfrom(audioChunkSize)
        #self.audiobuffer.append(data)
        packetCount = 1
        print(audioChunkSize)
        #print(len(data))
        # Receive data from audiostreamers.
        #while data != b'':
        while True:
            try:
                #if len(data) == audioChunkSize:
                data, server = self.client_sockets[self.countConnections].recvfrom(audioChunkSize)
                if data == b'':
                    break
                stream.write(data, self.n_frames)
                self.audiobuffer.append(data)
                packetCount += 1
                #print('received data length: ', len(data), packetCount)
                #with threading.Lock():
            except OSError as e:
                print(e.strerror)
                break
        #print(self.client_socket)
        print(len(self.audiobuffer))
        #print(self.audiobuffer[-1:])
        self.client_sockets[self.countConnections].close()

    def write_wav(self, filename):
        wav_out = wave.open(filename, 'wb')
        wav_out.setparams(self.params)
        wav_out.writeframes(b''.join(self.audiobuffer))


if __name__ == '__main__':
    port = 6000

    recorder = AudioRecorder(port)
    # Listen for new input until program is stopped.
    # Input will be written to wav file after each transfer is completed.
    while True:
        recorder.accept_connection()
        recorder.receive_params()
        recorder.receive_and_play()
        file_out = 'wav/Secretariat_Homebound/output-' + str(recorder.countConnections) + '.wav'
        recorder.write_wav(file_out)

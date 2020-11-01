import wave
import socket
import pickle
import wavio
import time

from twisted.internet import reactor, protocol


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
    host = "192.168.1.88:6000"
    streamer = AudioStreamer(filename, host)

    #host = "62.249.189.110:8000"

    #host = "192.168.1.88"
    #port = 6000
    #reactor.connectTCP(host, port, AudiostreamerFactory(filename=filename))
    #reactor.run()

    # Open the sound file
    #wf = wave.open(filename, 'rb')
    #streamer = AudioStreamer(wf, host)
    #wf.close()
    #streamer_g = AudioStreamer(host)

    # Send data to the recorder.
    #streamer.send_socket(wf)
    #wf.close()

    #wf_g = wave.open(filename_g, 'rb')
    #print(wf.readframes(5))

    # Figuring out how to mix the data in Audionode.
    #wav_wavio = wavio.read(filename)
    #print(wav_wavio)
    #print(wav_wavio.data[20000:20050])
    #print(wav_wavio.data[20000:20050, 0])
    #print(wav_wavio.data[20000:20050, 1])
    #print(list(zip(*wav_wavio.data[20000:20050]))[0])
    #print(list(zip(*wav_wavio.data[20000:20050]))[1])
    #print(max(list(zip(*wav_wavio.data))[0]))
    #print(min(list(zip(*wav_wavio.data))[1]))

    #streamer_g.send_socket(wf_g)

    #n_frames = 1024
    #FORMAT = pyaudio.paInt16
    #CHANNELS = 1
    #RATE = 44100

    #channels, sampwidth, framerate, nframes, _, _ = wf.getparams()
    #metadata = (channels, sampwidth, framerate, nframes)

#import pyaudio
#import wave
#
#filename = 'wav/AnnaBlanton_Rachel_Full/06_Violin.wav'
#
## Set chunk size of 1024 samples per data frame
#chunk = 1024
#
## Open the sound file
#wf = wave.open(filename, 'rb')
#
## Create an interface to PortAudio
#p = pyaudio.PyAudio()
#
## Open a .Stream object to write the WAV file to
## 'output = True' indicates that the sound will be played rather than recorded
#stream = p.open(format = p.get_format_from_width(wf.getsampwidth()),
#                channels = wf.getnchannels(),
#                rate = wf.getframerate(),
#                output = True)
#
## Read data in chunks
#data = wf.readframes(chunk)
#
## Play the sound by writing the audio data to the stream
#while data != '':
#    stream.write(data)
#    data = wf.readframes(chunk)
#
## Close and terminate the stream
#stream.close()
#p.terminate()
#
#
#import pyaudio
#
#
#class AudioStream:
#    def __init__(self, address=None, filename=None, n_frames=None):
#        print('Init AudioClient')
#        if filename is not None:
#            self.filename = filename
#        else:
#            self.filename = ''
#        # Number of frames to send in each transfer.
#        if n_frames is not None:
#            self.n_frames = n_frames
#        else:
#            self.n_frames = 1024
#        if address is not None:
#            self.hostname, self.port = address.split(':')
#            self.port = int(self.port)
#        else:
#            self.hostname = 'localhost'
#            self.port = 6000
#        print('Init AudioClient end')
#
#
#class AudioClient(protocol.Protocol):
#    def __init__(self, filename=None):
#        if filename is not None:
#            self.filename = filename
#        else:
#            self.filename = ''
#
#    #def sendMessage(self, wav):
#    def connectionMade(self):
#        print('sendMessage')
#        #filename = 'wav/Secretariat_Homebound/01_VoxBanjo.wav'
#        n_frames = 1024
#        wav = wave.open(self.filename, 'rb')
#        params = wav.getparams()
#        params_send = pickle.dumps(params)
#        self.transport.write(params_send)
#        data = wav.readframes(n_frames)
#        print(len(data))
#        while data != b'':
#            self.transport.write(data)
#            data = wav.readframes(n_frames)
#
#
#class AudiostreamerFactory(protocol.ClientFactory):
#    def __init__(self, filename=None):
#        if filename is not None:
#            self.filename = filename
#        else:
#            self.filename = ''
#
#    def clientConnectionLost(self, connector, reason):
#        print('clientConnectionLost')
#        #connector.connect()
#
#    def buildProtocol(self, addr):
#        print('buildProtocol')
#        return AudioClient(self.filename)
#    print(channels)
#    print(sampwidth)
#    print(framerate)
#    print(nframes)
#    print(metadata)
#    print(len(metadata))



    #p = pyaudio.PyAudio()
    #stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, output=True, frames_per_buffer=MSGLEN)
    # Open a .Stream object to write the WAV file to
    # 'output = True' indicates that the sound will be played rather than recorded
    #stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
    #                channels=wf.getnchannels(),
    #                rate=wf.getframerate(),
    #                output=True)

    # Create a socket connection for connecting to the server:
    #client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #client_socket.connect((IP, PORT))

    #while True:
    # Send data to the recorder.
#    data = wf.readframes(n_frames)
#    print(len(data))
#    #stream.write(data, n_frames)
#    while data != b'':
#        #print(data)
#        test.client_socket.sendto(data, (IP, PORT))
#        data = wf.readframes(n_frames)
#        #stream.write(data, n_frames)
#        # print data

    #client_socket.close()

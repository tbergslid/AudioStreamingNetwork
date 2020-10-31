import pyaudio
import wave
import socket
import threading
import pickle
import time

#from twisted.internet import reactor, protocol
#from twisted.internet.threads import deferToThread

class AudioRecorder:
    def __init__(self, port=None, n_frames=None):
        self.filename = ''
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
        data, server = self.client_sockets[self.countConnections].recvfrom(audioChunkSize)
        self.audiobuffer.append(data)
        packetCount = 1
        while data != b'':
            # Receive data from audiostreamers.
            try:
                stream.write(data, self.n_frames)
                data, server = self.client_sockets[self.countConnections].recvfrom(audioChunkSize)
                packetCount += 1
                #print('received data length: ', len(data), packetCount)
                with threading.Lock():
                    self.audiobuffer.append(data)
            except OSError as e:
                print('UH OH')
                break
        print(self.client_socket)
        print(len(self.audiobuffer))
        self.client_sockets[self.countConnections].close()

    def write_wav(self, filename):
        wav_out = wave.open(filename, 'wb')
        wav_out.setparams(self.params)
        wav_out.writeframes(b''.join(self.audiobuffer))


if __name__ == '__main__':
    port = 6000

    #reactor.listenTCP(port, AudioFactory())
    #reactor.run()

    recorder = AudioRecorder(port)
    # Listen for new input until program is stopped.
    # Input will be written to wav file after each transfer is completed.
    while True:
        recorder.accept_connection()
        recorder.receive_params()
        recorder.receive_and_play()
        file_out = 'wav/Secretariat_Homebound/output-' + str(recorder.countConnections) + '.wav'
        recorder.write_wav(file_out)


#def receive_socket(n_frames):
#    print(threading.get_ident())
#    global audiobuffer
#    # Socket setup
#    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create the socket
#    #server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # create the socket
#    server_socket.bind(('', port))  # Assign port to listen on
#    server_socket.listen(5)  # Queue max 5 connections
#    client_socket, address = server_socket.accept()
#    print(address)
#
#    server_socket.setblocking(0)
#
#    print("Your IP address is: ", socket.gethostbyname(socket.gethostname()))
#    print("Server Waiting for client on port ", port)
#
#    #    metadata, server = client_socket.recvfrom(27)
#    #    # Convert the metadata back into a string.
#    #    metadata = pickle.loads(metadata)
#    #    print(metadata)
#    #    #channels, sample_width, rate, n_frames = str(metadata).split(',')
#    #    channels = metadata[0]
#    #    sample_width = metadata[1]
#    #    rate = metadata[2]
#    #    n_frames = metadata[3]
#    #    print(channels, sample_width, rate, n_frames)
#
#    #audioChunkSize = format * channels * n_frames
#    #audioChunkSize = sample_width * channels * n_frames
#    audioChunkSize = 3 * 2 * 1024
#    packetCount = 0
#    #while True:
#
#
#    stream = p.open(format=format, channels=channels, rate=rate,
#                    frames_per_buffer=1024,
#                    output=True)
#
#    data, server = client_socket.recvfrom(audioChunkSize)
#    with threading.Lock():
#        audiobuffer.append(data)
#    while data != b'':
#        # Receive data from audiostreamers.
#        try:
#            #stream.start_stream()
#            stream.write(data, n_frames)
#            data, server = client_socket.recvfrom(audioChunkSize)
#            packetCount += 1
#            print('received data length: ', len(data), packetCount)
#            with threading.Lock():
#                audiobuffer.append(data)
#                #print('socket audiobuffer length: ', len(audiobuffer))
#            #stream.write(audiobuffer[0], n_frames)
#            #if data == b'':
#            #    print('File received!')
#            #    break
#            #    #raise RuntimeError('Socket connection broken')
#        except OSError as e:
#            print('UH OH')
#            break
#
#
##def play_audio(stream, n_frames):
#def play_audio(n_frames):
#    print(threading.get_ident())
#    global audiobuffer
#    stream = p.open(format=format, channels=channels, rate=rate,
#                    frames_per_buffer=1024,
#                    output=True)
#    BUFFER = 100
#    print(len(audiobuffer))
#    bufferCount = 0
#    while True:
#        if len(audiobuffer) > BUFFER:
#            #audio = audiobuffer[bufferCount:BUFFER+bufferCount]
#            audio = audiobuffer[:BUFFER]
#            print('play audio length: ', len(audio))
#            #with threading.Lock():
#            #    print('play audiobuffer length: ', len(audiobuffer))
#            #    audiobuffer = audiobuffer[BUFFER+bufferCount:]
#            stream.write(audio[0], n_frames*BUFFER)
#            bufferCount += 1
#            print('bufferCount: ', bufferCount)
#    #stream.stop_stream()
#    #stream.close()
#
#
#def get_callback(client_socket):
#    def callback(in_data, frame_count, time_info, status_flags):
#        data, server = client_socket.recvfrom(audioChunkSize)
#        return data, pyaudio.paContinue
#    return callback


#p = pyaudio.PyAudio()
#sample_width = wf.getsampwidth()
#format = p.get_format_from_width(sample_width)
##channels = wf.getnchannels()
#channels = 2
#rate = wf.getframerate()
#print(format)
#print(channels)
#print(rate)
#
#
#
### Open pyaudio stream
##stream = p.open(format=format, channels=channels, rate=rate,
##                output=True)
###                frames_per_buffer=1024,
###                stream_callback=get_callback(client_socket))
##audiobuffer = []
##audioChunkSize = format*channels*n_frames
##while True:
##    # Receive data from streamers.
##    try:
##        #stream.start_stream()
##        data, server = client_socket.recvfrom(audioChunkSize)
##        audiobuffer.append(data)
##        print(len(audiobuffer))
##        #print(data)
##        #print(server)
##        if len(audiobuffer) > 50:
##            #stream.write(audiofile.pop(0), n_frames)
##            audio = audiobuffer[:50]
##            #print(audio)
##            audiobuffer = audiobuffer[50:]
##            #print(audiobuffer)
##            #play_audio(stream, audio, n_frames)
##            #print(audio)
##            stream.write(audio[0], n_frames*50)
##            #stream.start_stream()
##            #play = threading.Thread(target=play_audio, args=(stream, audiobuffer, n_frames))
##            #play.start()
##        if data == b'':
##            raise RuntimeError('Socket connection broken')
##    except OSError as e:
##        print('UH OH')
##        break
#
#T_socket = threading.Thread(target=receive_socket, args=(n_frames,))
##T_play = threading.Thread(target=play_audio, args=(stream, n_frames,))
##T_play = threading.Thread(target=play_audio, args=(n_frames,))
#
#T_socket.start()
##T_play.start()
#T_socket.join()
##T_play.join()
##stream.stop_stream()
##stream.close()
##server_socket.close()
#
## Print audiobuffer to file
#wav_out = wave.open(file_out, 'wb')
#wav_out.setnchannels(channels)
#wav_out.setsampwidth(sample_width)
#wav_out.setframerate(rate)
#wav_out.writeframes(b''.join(audiobuffer))
#
#p.terminate()
#class TwistedRecorder(protocol.Protocol):
#    def __init__(self, port=None, n_frames=None):
#        print('init TwistedRecorder')
#        self.filename = ''
#        # Number of frames to receive in each transfer.
#        if n_frames is not None:
#            self.n_frames = n_frames
#        else:
#            self.n_frames = 1024
#        self.audiobuffer = []
#        self.buffer = []
#        self.p = pyaudio.PyAudio()
#        self.stream = []
#        self.client_socket = []
#        self.address = []
#        self.countConnections = -1
#        self.packetCount = 0
#        self.audioChunkSize = 0
#        # params is a _wave_params tuple with the following elements:
#        # 0: nchannels, 1: sampwidth, 2: framerate, 3: nframes, 4: comptype, 5: compname
#        self.params = []
#        if port is not None:
#            self.port = port
#        else:
#            self.port = 6000
#        print('init TwistedRecorder end')
#
#    def connectionMade(self):
#        print('connection made')
#        self.countConnections += 1
#        # Clear the audiobuffer when receiving a new stream.
#        self.audiobuffer = []
#        print('connection made end')
#
#    def connectionLost(self, reason=protocol.connectionDone):
#        self.packetCount = 0
#
#    def dataReceived(self, data):
#        print(len(data))
#        print(len(self.audiobuffer))
#        # First data received should be the wav parameters.
#        if self.packetCount == 0:
#            self.params = pickle.loads(data)
#            print(self.params)
#            self.audioChunkSize = self.params[0] * self.params[1] * self.n_frames
#            self.stream = self.p.open(format=self.p.get_format_from_width(self.params[1]),
#                                      channels=self.params[0], rate=self.params[2],
#                                      frames_per_buffer=2048,
#                                      output=True)
#        else:
#            self.buffer.append(data)
#            #self.stream.write(data, 1024)
#            print('receiving more data')
#            #print(len(self.buffer))
#            #self.audiobuffer.append(data)
#            #print(self.audiobuffer)
#            #data, server = self.client_socket[self.countConnections].recvfrom(audioChunkSize)
#            if self.packetCount % 10 == 0:
#                self.audiobuffer.append(self.buffer)
#                #self.stream.write(self.buffer[0], 10000)
#                play = deferToThread(self.play_audio)
#            #self.stream.write(data, self.audioChunkSize)
#            #self.stream.write(data, self.n_frames * 6)
#        self.packetCount += 1
#    #            while data != b'':
#    #                # Receive data from audiostreamers.
#    #                try:
#    #                    stream.write(data, self.n_frames)
#    #                    data, server = self.client_socket[self.countConnections].recvfrom(audioChunkSize)
#    #                    packetCount += 1
#    #                    # print('received data length: ', len(data), packetCount)
#    #                    with threading.Lock():
#    #                        self.audiobuffer.append(data)
#    #                except OSError as e:
#    #                    print('UH OH')
#    #                    break
#
#    def play_audio(self):
#        self.stream.write(self.buffer[0], 20000)
#        with threading.Lock():
#            self.buffer = []
#
#
#class AudioFactory(protocol.Factory):
#    def buildProtocol(self, addr):
#        print('buildProtocol')
#        return TwistedRecorder()

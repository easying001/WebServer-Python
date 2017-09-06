import wave

class FileRecoder(object):
    def __init__(self, file_path):
        self.fd = wave.open(file_path, 'rb')
        self.params = self.fd.getparams()
        self.nchannels, self.sampwidth, self.framerate, self.nframes = self.params[:4]
        print "channel = %d, width = %d, framerate = %d, nframes = %d" %(self.nchannels, self.sampwidth,
                                                                         self.framerate, self.nframes)

    def __del__(self):
        self.fd.close()

    def read(self, offset, size):
        frames = size/self.nchannels/self.sampwidth
        print "read num = %d frames" %(frames)
        if frames < self.nframes:
            self.fd.setpos(size)
            str_data = self.fd.readframes(frames)

        return str_data
import wave
import json
from hyper import HTTP20Connection


bearer='Bearer '
token='21.a27d49b449aa58116fd36d74683e37d5.2592000.1497106502.1813294370-9508810'
authorization=bearer+token
dueros_device_id='ffffffff-e76f-1bdf-0000-000063ec21a0'
host='dueros-h2.baidu.com'
path_get_directives='/dcs/v1/directives'
path_upload_voice_data='/dcs/v1/events'
boundary='this-is-a-boundary'
crlf = '\r\n'

def read_wave_data(file_path):
    #open a wave file, and return a Wave_read object
    f = wave.open(file_path,"rb")
    #read the wave's format infomation,and return a tuple
    params = f.getparams()
    #get the info
    nchannels, sampwidth, framerate, nframes = params[:4]
    #Reads and returns nframes of audio, as a string of bytes.
    str_data = f.readframes(nframes)
    #close the stream
    f.close()
    return str_data

def get_multipart_data(message_id, dialog_id, format, data):
    event={'clientContext':['ai.dueros.device_interface.alerts.AlertsState','ai.dueros.device_interface.audio_player.PlaybackState','ai.dueros.device_interface.speaker_controller.VolumeState','ai.dueros.device_interface.voice_output.SpeechState'], \
           'event':{'header':{'namespace':'ai.dueros.device_interface.voice_input', \
                              'name':'ListenStarted', \
                              'messageId':message_id, \
                              'dialogRequestId':dialog_id}, \
                    'payload':{'format':format}}}

    event=json.dumps(event)

    post_data1=[]

    post_data1.append('--'+boundary)
    post_data1.append('Content-Disposition: form-data; name="metadata"')
    post_data1.append('Content-Type: text/plain; charset=utf-8')
    post_data1.append('')
    post_data1.append(event)
    #     post_data1.append('--'+boundary+'--')# test
    post_data1.append('')

    #     return crlf.join(post_data1).encode('utf-8')# test

    #     # Audio data
    post_data1.append('--'+boundary)
    post_data1.append('Content-Disposition: form-data; name="audio"')
    post_data1.append('Content-Type: application/octet-stream')
    post_data1.append('')

    body1=crlf.join(post_data1).encode('utf-8')

    body2=data

    post_data3=[]
    post_data3.append('--'+boundary+'--')
    post_data3.append('')
    body3=crlf.join(post_data3).encode('utf-8')

    upload_data=body1+b'{0}'.format(crlf)+body2+b'{0}'.format(crlf)+body3

    return upload_data

if __name__ == "__main__":

    httpConn = HTTP20Connection(host)
    requestHeaders = {'authorization':authorization, \
                      'dueros-device-id':dueros_device_id, \
                      'content-type':'multipart/form-data; boundary={0}'.format(boundary)}

    message_id = "123456"
    dialog_id = "adcdefg"
    audio_format = "AUDIO_L16_RATE_16000_CHANNELS_1"
    print "start reading user's speech file"
    audio_data = read_wave_data('voice.wav')
    print "start building multipart body"
    post_body = get_multipart_data(message_id, dialog_id, audio_format, audio_data)
    print "post http request"
    httpConn.request('POST', path_upload_voice_data, headers=requestHeaders, body=post_body)
    response = httpConn.get_response();
    print response

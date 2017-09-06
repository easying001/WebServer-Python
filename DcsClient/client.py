import wave
import json
import cgi
import datetime
from hyper import HTTP20Connection
from recoder import FileRecoder

bearer='Bearer '
token='21.a27d49b449aa58116fd36d74683e37d5.2592000.1497106502.1813294370-9508810'
authorization=bearer+token
dueros_device_id='ffffffff-e76f-1bdf-0000-000063ec21a0'
host='dueros-h2.baidu.com:443'
path_get_directives='/dcs/v1/directives'
path_upload_voice_data='/dcs/v1/events'
boundary='this-is-a-boundary'
crlf = '\r\n'



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
    host_url = 'dueros-h2.baidu.com'
    access_token = 'Bearer 21.a27d49b449aa58116fd36d74683e37d5.2592000.1497106502.1813294370-9508810'
    device_id = 'ffffffff-e76f-1bdf-0000-000063ec21a0'
    api = 'dcs/v1'
    message_id = '123456'
    dialog_id = 'abcdefg'
    format = ''
    context = {"clientContext":['ai.dueros.device_interface.alerts.AlertsState',
                                'ai.dueros.device_interface.audio_player.PlaybackState',
                                'ai.dueros.device_interface.speaker_controller.VolumeState',
                                'ai.dueros.device_interface.voice_output.SpeechState'],}
    event = {'header':
                 {'namespace':'ai.dueros.device_interface.voice_input', \
                  'name':'ListenStarted', \
                  'messageId':message_id, \
                  'dialogRequestId':dialog_id
                 },
            'payload':
                {'format':format
                }
            }

    done = False
    recoder = FileRecoder('voice.wav')

    while not done:
        recoder.read(0, 320)
        httpConn = HTTP20Connection('{}:443'.format(host_url), force_proto='h2')
        headers = {'authorization': 'Bearer {}'.format(access_token)}
        headers['dueros-device-id'] = device_id

        downChannelId = httpConn.request('GET', '/{}/directives'.format(api), headers=headers)
        response = httpConn.get_response(downChannelId)
        if response.status != 200:
            print 'request returns status = %d' %(response.status)

        # print 'headers for response = %s' %(response.headers)
        ctype, pdict = cgi.parse_header(response.headers['content-type'][0].decode('utf-8'))
        boundary = '--{}'.format(pdict['boundary']).encode('utf-8')
        downchannel = httpConn.streams[downChannelId]
        ping_period = datetime.datetime.utcnow() + datetime.timedelta(seconds=240)

        headers = {
            ':method': 'POST',
            ':scheme': 'https',
            ':path': '/{}/events'.format(api),
            'authorization': 'Bearer {}'.format(token),
            'content-type': 'multipart/form-data; boundary={}'.format(boundary)
        }

        headers['dueros-device-id'] = device_id
        # this should be the first call for sending a given http request to a server.
        # it returns a stream ID for the given connection that should be passed to all
        # subsequent request building calls
        stream_id = httpConn.putrequest(headers[':method'], headers[':path'])

        default_headers = (':method', ':scheme', ':authority', ':path')
        for name, value in headers.items():
            is_default = name in default_headers
            # send an http header to server with name header and its value
            # it queues the headers up to be sent when you call endheaders()
            httpConn.putheader(name, value, stream_id, replace=is_default)

        httpConn.endheaders(final=False, stream_id=stream_id)

        metadata = {
            'context': context,
            'event': event
        }
        json_part = '--{}\r\n'.format(boundary)
        json_part += 'Content-Disposition: form-data; name="metadata"\r\n'
        json_part += 'Content-Type: application/json; charset=UTF-8\r\n\r\n'
        json_part += json.dumps(metadata)
        print json_part.encode('utf-8')

        httpConn.send(json_part.encode('utf-8'), final=False, stream_id=stream_id)


        done = True

    print 'end of mainloop'

'''
    httpConn = HTTP20Connection(host, force_proto='h2')
    requestHeaders = {'authorization':authorization, \
                      'dueros-device-id':dueros_device_id, \
                      'content-type':'multipart/form-data; boundary={0}'.format(boundary)}

    downchannel_id = httpConn.request('GET', path_get_directives, headers=requestHeaders)
    downchannel_resp = httpConn.get_response(downchannel_id)
    print downchannel_resp.status
    print downchannel_resp.headers

    ctype, pdict = cgi.parse_header(downchannel_resp.headers['content-type'][0].decode('utf-8'))
    downchannel_boundary = '--{}'.format(pdict['boundary']).encode('utf-8')
    downchannel = httpConn.streams[downchannel_id]

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
    print response.status '''

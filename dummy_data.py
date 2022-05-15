#this will store santized data for tests

#data returned from extract recent logs
parsed_data = { 
0:{'@timestamp': ['2022-05-08T09:17:02.000Z'],
 'host.hostname': ['Linux-test'],
 'host.ip': ['127.0.0.1'],
 'message': ['Received disconnect from 104.248.62.102 port 50254:11: Bye Bye '
             '[preauth]\n'],
 'process.name': ['sshd'],
 'process.pid': [463269],
 'sort': [1652329022000]}, 
1:{'@timestamp': ['2022-05-10T14:17:02.000Z'],
 'host.hostname': ['Linux-test'],
 'host.ip': ['127.0.0.1'],
 'message': ['Received disconnect from 104.248.62.102 port 50254:11: Bye Bye '
             '[preauth]\n'],
 'process.name': ['sshd'],
 'process.pid': [463269],
 'sort': [1652329022000]}
2:{'@timestamp': ['2022-05-11T04:17:02.000Z'],
 'host.hostname': ['Linux-test'],
 'host.ip': ['127.0.0.1'],
 'message': ['Received disconnect from 104.248.62.102 port 50254:11: Bye Bye '
             '[preauth]\n'],
 'process.name': ['sshd'],
 'process.pid': [463269],
 'sort': [1652329010470]},
'sort': [1652329010470]
}

# data returned from the elastic instance
raw_request = {
0 : {'_id': 'GDJRroABv-hSv77dMuC5',
 '_index': 'test-index',
 '_score': None,
 'fields': {'@timestamp': ['2022-05-10T14:13:18.000Z'],
            'host.hostname': ['Linux-test'],
            'host.ip': ['127.0.0.1'],
            'message': ['Failed password for invalid user ftptest from '
                        '189.146.219.34 port 51750 ssh2\n'],
            'process.name': ['sshd'],
            'process.pid': [425640]},
 'sort': [1652191998000]},
1:{'_id': '0jOhr4ABv-hSv77ds0Sv',
 '_index': 'test-index',
 '_score': None,
 'fields': {'@timestamp': ['2022-05-10T20:20:51.000Z'],
            'host.hostname': ['Linux-test'],
            'host.ip': ['127.0.0.1'],
            'message': ['Received disconnect from 20.231.45.255 port 45236:11: '
                        'Bye Bye [preauth]\n'],
            'process.name': ['sshd'],
            'process.pid': [431725]},
 'sort': [1652214051000]} ,
2:{'_id': 'ZDOIsIABv-hSv77dw5Ik',
 '_index': 'test-index',
 '_score': None,
 'fields': {'@timestamp': ['2022-05-11T00:33:14.000Z'],
            '_id': ['ZDOIsIABv-hSv77dw5Ik'],
            'host.hostname': ['Linux-test'],
            'host.ip': ['127.0.0.1'],
            'message': ['Failed password for invalid user clouduser from '
                        '43.154.110.78 port 36818 ssh2\n'],
            'process.name': ['sshd'],
            'process.pid': [436717]},
 'sort': [1652229194000]}
}

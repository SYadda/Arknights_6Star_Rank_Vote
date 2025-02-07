from flask import request

def get_client_ip():
    try:
        real_ip = request.headers.get('X_FORWARDED_FOR', type=str)
        client_ip = real_ip.split(",")[0]
    except:
        try:
            client_ip = request.headers.get('X-Real-IP', type=str)
        except:
            client_ip = request.remote_addr
    return client_ip

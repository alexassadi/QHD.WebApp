from datetime import datetime

def global_timestamp(request):
    return {'timestamp': int(datetime.now().timestamp())}

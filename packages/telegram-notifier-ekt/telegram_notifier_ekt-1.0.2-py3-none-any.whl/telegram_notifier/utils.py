from datetime import datetime

def get_current_date_format():
    today = datetime.now()
    date_format = today.strftime("%d%m%Y")
    return date_format
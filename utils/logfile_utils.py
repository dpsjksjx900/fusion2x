import os, datetime, random, string

def make_log_filename():
    dt = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    rid = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    os.makedirs("logs", exist_ok=True)
    return os.path.join("logs", f"fusion2x_{dt}_{rid}.log")

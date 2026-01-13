import requests
from datetime import datetime,timezone
import time

def send_heartbeat(job_name, metadata=None):
    url = "https://api.ansrstudio.com/heartbeat"
    headers = {
        "Authorization": "df_b1c79d118073b82f9aa961458253057f208d9d32d388df91a46343bbeca079b4",
        "Content-Type": "application/json"
    }
    
    payload = {
        "job_name": job_name,
        "current_time": datetime.now(timezone.utc).isoformat(sep=' '),
        "metadata": metadata or {"status": "healthy"}
    }
    
    response = requests.post(url, headers=headers, json=payload)
    print(response.json())
    return response.json()

# Send heartbeat every 5 minutes during long-running job
def long_running_job():
    job_name = "test"
    
    for i in range(100):
        # Do work
        #process_batch(i)
        
        # Send heartbeat every 10 iterations
        if i % 10 == 0:
            send_heartbeat(job_name, {
                "progress": f"{i}%",
                "status": "healthy"
            })
        
        time.sleep(30)  # Simulate work

long_running_job()
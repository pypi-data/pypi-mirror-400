from seerpy import Seer
import time
seer = Seer(apiKey='df_b1c79d118073b82f9aa961458253057f208d9d32d388df91a46343bbeca079b4')

# # import pandas as pd
# # import requests

# from seerpy import Seer
# import time

# # Initialize SEER
# seer = Seer(apiKey='df_b1c79d118073b82f9aa961458253057f208d9d32d388df91a46343bbeca079b4')

# # def long_running_job():
# #     for i in range(120):
# #         # Do some work
# #         #process_batch(i)
        
# #         # Send heartbeat every iteration
# #         seer.heartbeat(
# #             job_name="test",
# #             metadata={"batch": i, "status": "processing"}
# #         )
        
# #         time.sleep(1)  # Wait 1 minute

# # # Run the job
# # long_running_job()  



import pandas as pd
def run_report():
    # Your script logic here
    #data = pd.read_csv(r"C:\Users\xlor1\Downloads\tests\daily_report.csv")
    #print(data)
    #time.sleep(30)
    d = {'region': [1, 2], 'col2': [3, 4]}
    data = pd.DataFrame(data=d)
    processed = data.groupby("region").sum()
    #data.to_csv(r"C:\Users\xlor1\Downloads\tests\sales_data.csv")

# Wrap your script with     SEER monitoring
with seer.monitor("test",True,metadata={'run_type':'ADHOC'}):
        run_report() # + your script logic here
# # # # # seer.heartbeat("a",metadata={'run_type':'ADHOC'})   

# # # Import SEER monitoring
from seerpy import payloads

#payloads.replay_failed_payloads('df_b1c79d118073b82f9aa961458253057f208d9d32d388df91a46343bbeca079b4')

# import requests
# import time
# import os
# import json
# from datetime import datetime

# def post_with_backoff(url, payload, is_email,headers=None,max_retries=5, base_delay=1, max_delay=30,request_type='post'):
#     for attempt in range(max_retries):
#         try:
#             if is_email:
#                 response = requests.post(
#                     url,
#                     auth=("api", "20627a63fde9bbb6a4df5eaa4fc060d3-f3238714-52b8b23c"),
#                     data=payload
#                 )
#             else:
#                 if request_type == 'post':
#                     response = requests.post(url, json=payload,headers=headers)
#                 else:
#                     response = requests.get(url, json=payload,headers=headers)
#             print(response)
#             print(response.headers)
#             return response
#         except Exception as e:
#             if attempt == max_retries - 1:
#                 #save_failed_payload(payload, endpoint)
#                 raise  # Give up after max_retries
            
#             delay = min(base_delay * (2 ** attempt), max_delay)
#             time.sleep(delay)
            
# url = "https://api.mailgun.net/v3/mg.ansrstudio.com/messages"
# email_payload={
#             "from": "SEER <no-reply@mg.ansrstudio.com>",
#             "to": "formatted_contacts",
#             "subject": f"Job 1 had a s event."
#         }
# for i in range(120):
#     post_with_backoff(url, email_payload,is_email=True, max_retries=5, base_delay=1, max_delay=30)


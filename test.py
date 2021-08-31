import superlog
import sys
# from google.cloud import datastore
# google cloud datastore tutorial: https://cloud.google.com/datastore/docs/reference/libraries#client-libraries-install-python
# https://stackoverflow.com/questions/39062334/google-cloud-datastore-api-in-python-code
# https://github.com/GoogleCloudPlatform/python-docs-samples/tree/master/datastore/cloud-client
# export GOOGLE_APPLICATION_CREDENTIALS="[PATH]"

# source .bashrc first, GOOGLE_APPLICATION_CREDENTIALS

# def upload_datastore(kind):
#     datastore_client = datastore.Client()
#     task_key = datastore_client.key(kind)
#     #read to the end
#     while 1:
#         msg = superlog.superlog_read()
#         if msg == False:
#             break
#         task = datastore.Entity(key=task_key)
#         task["Timestamp"] = msg[0]
#         task["Pid"] = msg[1]
#         task["Tid"] = msg[2]
#         task["Name"] = msg[3]
#         task["Data"] = msg[4]
#         # datastore_client.put(task)
#         print(msg)


def show():
    while 1:
        msg = superlog.superlog_read()
        if msg == False:
            break
        print(msg)


# init and open shm
if superlog.superlog_init() == False:
    print("openfile fail")
    sys.exit(0)



# upload_datastore("Serverless")
show()


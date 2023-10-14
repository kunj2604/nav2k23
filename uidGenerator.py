import uuid


def UID():
    myuuid = uuid.uuid4()
    return str(myuuid)


for i in range(0, 486):
    uid = UID()
    print(uid)

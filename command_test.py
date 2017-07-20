def createmessage(command):
    print(command)
    # lookup node info against database or OPC tree here - hardcoded values right now
    discrete = True
    address = 3
    # initialize messages
    msg1 = 0
    msg2 = -1
    if discrete:
        # type bit is 0, write command bit
        msg1 |= command[1] << 1
    else:
        # write type bit
        msg1 |= 1 << 0
        # write output value
        msg2 = command[1]
    # add address
    msg1 |= address << 3
    # q.task_done()
    if msg2 != -1:
        return msg1, msg2
    else:
        return msg1

m = createmessage((3,False))
print(m)
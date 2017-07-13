class LamportClock():
    def __init__(self):
        self.time = 0
        self.timestamp = 0

    def increaseTimeAfterRecv(self, msg_ts):
        self.time = max(msg_ts, self.time) + 1

    def increaseTimeBeforeSend(self):
        self.time += 1
        self.timestamp = self.time

    def getTime(self):
        return self.time

    def getTimeStamp(self):
        return self.timestamp
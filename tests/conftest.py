class UploadedCsv:
    def __init__(self, text):
        self.text = text

    def getvalue(self):
        return self.text.encode("utf-8")

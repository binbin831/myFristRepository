from burp import IBurpExtender
from java.io import PrintWriter
from java.lang import RuntimeException


class BurpExtender(IBurpExtender):

    # implement IBurpExtender
    def registerExtenderCallbacks(self, callbacks):
        callbacks.setExtensionName("Hello world extension")

        stdout = PrintWriter(callbacks.getStdout(), True)

        # write a message to our output stream
        stdout.println("Hello output")
        return
#Class Anode: Defines only the interface between Argos node.
#
class ArNodeIntf():

    #Consumer: Subscribe with an input feed
    def InputFeed_subscribe(self, feedName, feedIndex):
        return self.InputFeed_subscribeImpl()
    def InputFeed_subscribeImpl(selfs, feedName, feedIndex):
        raise NotImplementedError

    #Consumer: Poll for new datapoints
    def InputFeed_poll(self, feedName, feedIndex):
        return self.InputFeed_pollImpl(feedName, feedIndex)
    def InputFeed_pollImpl(self, feedName, feedIndex):
        raise NotImplementedError

    #Consumer: Subscribe with a feedback data stream
    def Feedback_subscribe(self, feedbackName, feedbackIndex):
        return self.Feedback_subscribeImpl(feedbackName, feedbackIndex)
    def Feedback_subscribeImpl(self, feedbackName, feedbackIndex):
        raise NotImplementedError

    #Consumer: Poll for new entries of feedback data
    def Feedback_poll(self, feedbackName, feedbackIndex):
        return self.Feedback_pollImpl(feedbackName, feedbackIndex)
    def Feedback_pollImpl(self, feedbackName, feedbackIndex):
        raise NotImplementedError

    #Producer: Make data visible in the stream; Subscribers and pollers will see new datapoints
    def OutputStream_write(self, streamName, streamIndex, data):
        return self.OutputStream_writeImpl(streamName, streamIndex, data)
    def OutputStream_writeImpl(self, streamName, streamIndex, data):
        raise NotImplementedError

    #Producer: Notify subsribers to check for datapoins in the stream
    def OutputStream_notify(self, streamName, streamIndex):
        return self.OutputStream_notifyImpl(streamName, streamIndex)
    def OutputStream_notifyImpl(self, streamName, streamIndex):
        raise NotImplementedError

    #Producer: Make feedback data visible; Subscribers and pollers will see new entries of feedback data
    def OutputFeedback_write(self, feedbackName, feedBackIndex, data):
        return self.OutputFeedback_writeImpl(feedbackName, feedBackIndex, data)
    def OutputFeedback_writeImpl(self, feedbackName, feedBackIndex, data):
        raise NotImplementedError

    #Producer: Notify subscribers to check for new entries of feedback data
    def OutputFeedback_notify(selfs, feedbackName, feedbackIndex):
        return self.OutputFeedback_notifyImpl(feedbackName, feedbackIndex)
    def OutputFeedback_notifyImpl(selfs, feedbackName, feedbackIndex):
        raise NotImplementedError
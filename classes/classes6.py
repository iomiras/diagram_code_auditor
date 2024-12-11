class Logger:
    def log(self, message):
        return f"Log: {message}"


class Notifier:
    def notify(self, message):
        return f"Notify: {message}"


class AlarmSystem(Logger, Notifier):
    def alert(self, message):
        log_message = self.log(message)
        notify_message = self.notify(message)
        return f"{log_message}\n{notify_message}"

# [
#     ['AlarmSystem', 'alert()', 'Logger'],
#     ['AlarmSystem', 'alert()', 'Notifier']
# ]
from logkit import log


class AppInterface:
    def __init__(self):
        log.info("Welcome to the interface.")
        pass

    def start(self):
        log.info("Starting App Interface.")
        input("Please Enter: ")
        pass

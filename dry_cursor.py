class DryCursor:
    def __init__(self, cursor):
        self.cursor = cursor

    def execute(self, command, *args, **kwargs):
        print (command, args, kwargs)
        if command.startswith("SELECT"):
            self.cursor.execute(command, *args, **kwargs)

    def fetchall(self, *args, **kwargs):
        return self.cursor.fetchall(*args, **kwargs)

    @property
    def connection(self):
        return self.cursor.connection


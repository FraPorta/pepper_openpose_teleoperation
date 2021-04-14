import naoqi
import qi

class MyService:

    def echo(self, message):
        return message

    def do_something(self):
        pass

def main():
    app = qi.Application()
    app.start()
    session = app.session
    myService = MyService()
    session.registerService("MyService", myService)
    app.run()

if __name__ == "__main__":
    main()
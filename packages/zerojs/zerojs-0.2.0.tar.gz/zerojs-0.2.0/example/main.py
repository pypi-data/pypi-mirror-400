"""Example ZeroJS application."""

from zerojs import ZeroJS

app = ZeroJS(title="ZeroJS Example")

if __name__ == "__main__":
    app.start(reload=True)

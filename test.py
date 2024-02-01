import traceback


class Test:
    def __init__(self, v):
        self.v = v

    def __enter__(self):
        print("In enter")
        return self.v

    def __exit__(self, type, value, traceback):
        print("In exit")


def main():
    t = Test("Hi")
    val = t.__enter__()
    exc = None
    tb = None
    try:
        print(f"Got {val}")
        raise Exception("Exception")
    except Exception as e:
        exc = e
        tb = traceback.format_exc()
    finally:
        t.__exit__(type(exc), exc, tb)

    if exc is not None:
        raise exc

    # with Test("Hi") as val:
    #     print(f"Got {val}")
    #     raise Exception("Exception")


main()

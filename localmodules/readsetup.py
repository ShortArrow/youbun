from os import replace


setupfilename = "setup/setup"


def __read__(configname: str) -> str:
    test_data = open(setupfilename, "r")
    lines = test_data.readlines()
    test_data.close()
    buf = ""
    for line in lines:
        if line.split(sep=" ")[0] == configname:
            buf = line.split(sep=" ")[2]
            break
    buf = buf[buf.find('"') + 1 : buf.rfind('"')]
    return buf


def apikey() -> str:
    return __read__("apikey")


def secret() -> str:
    return __read__("secret")

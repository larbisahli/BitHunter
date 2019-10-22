"""
{"currency_Price": 1233, "currency": "CAD", "time": 134144}

"""

def small_value(value):
    pass_ = str(value).split("-")
    if pass_[0] != "":
        if len(str(value).split("-")) >= 2:
            zero = ""
            for i in range(int(pass_[1])):
                zero += "0"
            return f"0.{zero}{pass_[0].split('e')[0]}"
        else:
            return value
    else:
        if len(pass_[1].split("e")) >= 2:
            zero = ""
            for i in range(int(pass_[2])):
                zero += "0"
            return f"-0.{zero}{pass_[1].split('e')[0]}"
        else:
            return value

print(small_value(-5))
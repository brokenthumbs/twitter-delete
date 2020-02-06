import re
status = "Verifying myself: I am brokenthumbs on http://Keybase.io. b0GpF6YUYnPEr7pPP5UPRK0jaFC6CGSwvc65"
if re.match("Verifying myself: I am .* on http://Keybase.io", status) is not None:
    print("match")
else:
    print("no match")

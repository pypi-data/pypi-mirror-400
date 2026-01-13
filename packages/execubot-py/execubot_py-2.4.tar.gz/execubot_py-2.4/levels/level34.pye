grid = [["yellow","green","green","green","green","green","blue"],["green","green","green","green","green","blue","blue"],["green","green","maroon","green","blue","blue","blue"],["blue","blue","maroon","blue","blue","blue","green"],["blue","green","maroon","green","green","green","green"],["green","green","green","green","green","fuchsia","fuchsia"],["green","green","green","green","green","fuchsia","yellow"]]
row = 0
col = 0

while not maroon():
    right()
    down()
for _ in range(3):
    down()
while green():
    for _ in range(7):
        if green() or fuchsia():
            right()
        elif yellow():
            up()
    if not yellow():
        down()

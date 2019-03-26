import random

x = random.randint(0, 1000)

def write_to_log(message):
    with open("logs/log{}.txt".format(x), "a+") as log_file:
        log_file.write(message)

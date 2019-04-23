import random

x = random.randint(0, 1000)


def write_to_log(message):
    message = message.strip("\n") + "\n"
    with open("logs/log{}.txt".format(x), "a+") as log_file:
        log_file.write(message)

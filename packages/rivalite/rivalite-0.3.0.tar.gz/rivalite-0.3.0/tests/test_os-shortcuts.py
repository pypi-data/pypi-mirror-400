from rivalite import clear, stdout
import time
print("This should disappear after 2 seconds.")
time.sleep(2)
clear()
print("New message")
print("ls:")
print(stdout(["ls"]))

import random
from datetime import datetime
from threading import Timer

#random.seed(datetime.now().timestamp())
#for i in range (0, 50):
#    print(random.choices([0, 1], [50, 50], k=10))
def hello():
    print ("hello, world")

t = Timer(5, hello)
t.start()
print("-------")
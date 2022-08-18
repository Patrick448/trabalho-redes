import random
from datetime import datetime

random.seed(datetime.now().timestamp())
for i in range (0, 50):
    print(random.choices([0, 1], [50, 50], k=10))
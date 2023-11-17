# %%
__depends__ = []
__dest__ = "../results/data.json"

# %%
import random
import json
import os

# %%
random.seed("92831")
data = [random.random() for x in range(100)]

if not os.path.exists("../results"):
    os.mkdir("../results")

with open(__dest__, "w") as fh:
    json.dump(data, fh)
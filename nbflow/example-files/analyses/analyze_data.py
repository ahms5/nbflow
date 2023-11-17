# %%
__depends__ = ["../results/data.json"]
__dest__ = "../results/stats.json"

# %%
import json
import time
time.sleep(5) # Simulate long running task

# %%
with open("../results/data.json", "r") as fh:
    data = json.load(fh)

# %%
mean = sum(data) / len(data)
var = sum(((x - mean) ** 2) / (len(data) - 1) for x in data)
results = dict(mean=mean, var=var)

# %%
with open(__dest__, "w") as fh:
    json.dump(results, fh)


# make the code as Python 3 compatible as possible
from __future__ import print_function, division
from __future__ import absolute_import


import pypsa,os

import pandas as pd

import numpy as np

from itertools import chain

network = pypsa.Network()

folder_name = "ac-dc-data"
network.import_from_csv_folder(folder_name)

now = network.snapshots[4]
network.now = now

network.lopf(network.snapshots)

for sn in network.sub_networks.obj:
    print(sn,sn.carrier,len(sn.buses()),len(sn.branches()))

print("\nControllable branches:")

print(network.links)

now = network.snapshots[5]


print("\nCheck power balance at each branch:")

branches = network.branches()

for bus in network.buses.index:
    print("\n"*3+bus)
    generators = sum(network.generators_t.p.loc[now,network.generators.bus==bus])
    loads = sum(network.loads_t.p.loc[now,network.loads.bus==bus])
    print("Generators:",generators)
    print("Loads:",loads)
    print("Total:",generators-loads)

    p0 = 0.
    p1 = 0.

    for cls in pypsa.components.branch_types:
        df = getattr(network,cls.list_name)
        pnl = getattr(network,cls.list_name+"_t")

        bs = (df.bus0 == bus)

        if bs.any():
            print(cls.__name__,"\n",pnl.p0.loc[now,bs])
            p0 += pnl.p0.loc[now,bs].sum()

        bs = (df.bus1 == bus)

        if bs.any():
            print(cls.__name__,"\n",pnl.p1.loc[now,bs])
            p1 += pnl.p1.loc[now,bs].sum()

    print("Branches",p0+p1)

    np.testing.assert_allclose(generators-loads+1.,p0+p1+1.)

    print("")

print(sum(network.generators_t.p.loc[now]))

print(sum(network.loads_t.p.loc[now]))

results_folder_name = os.path.join(folder_name,"results-lopf")

if True:
    network.export_to_csv_folder(results_folder_name)

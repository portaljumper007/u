from collections import defaultdict

source = [1, 1, 1, 1, 2, 2, 3]

def list_duplicates(seq):
    tally = defaultdict(list)
    for i,item in enumerate(seq):
        tally[item].append(i)
    return ((key,locs) for key,locs in tally.items()
                            if len(locs)>1)

for dup in sorted(list_duplicates(source)):
    print(dup)
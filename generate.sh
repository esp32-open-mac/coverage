#!/bin/bash
mkdir esp32-open-mac
mkdir -p output/branches
gunzip -f -k trace_tx_example_no_powermanagement-esp32-plain_mapped.txt.gz
git clone --mirror https://github.com/esp32-open-mac/esp32-open-mac.git esp32-open-mac/.git
cd esp32-open-mac
git config core.bare false
git reset HEAD --hard
allbranches=""

for rawbranch in $(git ls-remote --refs -q origin 'refs/heads/*' | cut -f2); do
    branch="${rawbranch##*/}"
    if [[ "$branch" =~ [^a-zA-Z0-9_\-] ]]; then
        echo "WARN: not processing $branch because of its name"
        continue;
    fi
    allbranches="$allbranches:$branch"
    git checkout "$branch"
    commit=$(git rev-parse HEAD)
    cd ..
    mkdir -p "output/branches/${branch}"
    python3 collect_coverage.py | python3 flame_graph.py trace_tx_example_no_powermanagement-esp32-plain_mapped.txt "output/branches/${branch}/data.json"
    python3 generate_branch_output.py "$branch" "$commit"
    cd esp32-open-mac
done

cd ..
python3 generate_index.py "$allbranches"

#!/bin/bash

export H2
count=0
for i in 1 2 3 4
do
	((count+=$(curl -s -H "$H2" --url "https://api.github.com/repos/datamove/linux-git2/pulls?state=all&per_page=100&page=$i" | jq '[ .[] | .user.login=="'"$1"'" | select(.) ] | length')))
done
echo PULLS $count

min_date=$(echo '1' | jq 'now | todateiso8601')
for i in 1 2 3 4
do
	page_min=$(curl -s -H "$H2" --url "https://api.github.com/repos/datamove/linux-git2/pulls?state=all&per_page=100&page=$i" | jq '[.[] | select(.user.login=="'"$1"'") | .created_at] | min | if . then fromdate else now end')
	min_date=$(echo [$min_date, $page_min] | jq 'if .[0] < .[1] then .[0] else .[1] end')
done
min_date=$(echo $min_date | jq 'todate')

min_merged=$(echo '1' | jq 'now | todateiso8601')
for i in 1 2 3
do
        page_min=$(curl -s -H "$H2" --url "https://api.github.com/repos/datamove/linux-git2/pulls?state=closed&per_page=100&page=$i" | jq '[.[] | select(.user.login=="'"$1"'") | .created_at] | min | if . then fromdate else now end')
        min_merged=$(echo [$min_merged, $page_min] | jq 'if .[0] < .[1] then .[0] else .[1] end')
done
min_merged=$(echo $min_merged | jq 'todate')
merged=$(echo [$min_merged, $min_date] | jq 'if .[0] == .[1] then 1 else 0 end')
echo EARLIEST $min_date
echo MERGED $merged


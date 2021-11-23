#!/bin/bash

export H2
count=0
for i in 1 2 3 4
do
	((count+=$(curl -s -H "$H2" --url "https://api.github.com/repos/datamove/linux-git2/pulls?state=all&per_page=100&page=$i" | jq '[ .[] | .user.login=="'"$1"'" | select(.) ] | length')))
done
echo PULLS $count

min_date=$(echo '1' | jq 'now | todate')
merged=0
for i in 1 2 3 4
do
	page_min=$(curl -s -H "$H2" --url "https://api.github.com/repos/datamove/linux-git2/pulls?state=all&per_page=100&page=$i" | jq '[.[] | select(.user.login=="'"$1"'") | .created_at] | min | if . then fromdate else now end')
	min_date=$(echo [$min_date, $page_min] | jq 'if .[0] < .[1] then .[0] else .[1] end')
done
min_date=$(echo $min_date | jq 'todate')
number=0
for i in 1 2 3 4
do 
	merged=$(curl -s -H "$H2" --url "https://api.github.com/repos/datamove/linux-git2/pulls?state=all&per_page=100&page=$i" | jq '.[] | select(.created_at=='$min_date') | if .merged_at then 1 else 0 end')
	if [[ $merged == 1 ]];
	then 
		number=$(curl -s -H "$H2" --url "https://api.github.com/repos/datamove/linux-git2/pulls?state=all&per_page=100&page=$i" | jq '.[] | select(.created_at=='$min_date') | .number')
		break
	fi
done

echo EARLIEST $number
echo MERGED $merged


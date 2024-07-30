#!/bin/sh

if [ "$1" = "" ]; then
    echo "Give me a server start cmd, example: $0 'python index.py production'"
    exit 1
fi

file_map="iDuSh22faxqj:6q1d i0gZ322ututi: i7tit9c:6svq i4wk2oh: iRujgdfrkza: dkbdv7:"
server_run_cmd="$1"
test_server="http://localhost:3000"

$server_run_cmd >/dev/null 2>&1 &
server_pid=$!
sleep 2
if ! kill -0 $server_pid 2>/dev/null; then
    echo "Starting server failed"
    exit 1
fi

ln_fmt="%10s%10s%20s%15s\n"
printf "$ln_fmt" RET FUN FID PWD
has_error=0
for file in $file_map; do
    fid=${file%:*}
    pwd=${file#*:}
    url="$test_server/?url=https://wwbg.lanpw.com/$fid&pwd=$pwd"
    status_code=$(curl -sm5 -o /dev/null -I -w "%{http_code}" "$url&type=down")
    ret="OK"
    if [ "$status_code" != "302" ]; then
        ret="FAILED"
        has_error=1
    fi
    printf "$ln_fmt" "$ret" DLOAD "$fid" "$pwd"

    ret="OK"
    json_repl=$(curl -sm5 "$url&type=json")
    code=$(echo "$json_repl" | grep -oP '"code":\K[^,]*')
    if [ "$code" != "200" ]; then
        ret="FAILED"
        has_error=1
    fi
    printf "$ln_fmt" "$ret" GJSON "$fid" "$pwd"
done

if [ $has_error -eq 0 ]; then
    echo "All test passed"
fi

kill $server_pid 1>/dev/null 2>&1
exit $has_error

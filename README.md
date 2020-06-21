### Introduction

https://github.com/paulmaunders/delivery-slot-bot/ is an amazing software to check for slots availability on Tesco (and others).
Unfortunately there is no way to be notified for slots on specific days only, so here we are.

### Usage
```
$ ./start.sh
```

### start.sh
This is the shell script to launch the **wrap.py** utility and it's where you will define:
- PO_USER_KEY
- PO_API_TOKEN
- where https://github.com/paulmaunders/delivery-slot-bot/ is installed on (--dtb-path)
- the days you are interested in (--days)
i.e.:
```
$ cat start.sh
#!/bin/sh

export PO_USER_KEY="foo"
export PO_API_TOKEN="bar"

./wrap.py --days 2020-07-02 2020-07-03 2020-07-04 --dtb-path $HOME/somewhere
```
so it's _docker friendly_, let's say :)


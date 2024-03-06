#!/bin/bash
for (( i=1 ; i<=105 ; i++ )); 
do
   python3 client.py 127.0.0.1 /www/test_visual/index.html GET -m 3 &
   sleep 0.5
done

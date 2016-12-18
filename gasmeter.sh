#!/bin/bash
IFS=,
while read t d1 d2 id d3 d4 d5 value chksum; do
	echo TIMESTAMP is $t ID is $id and VALUE is $value
	curl "https://data.sparkfun.com/input/n1yYj38OKVtdw32J2OXv?private_key=XXXXXXX&capturetime=$t&cubicfeet=$value&meterid=$id"
done


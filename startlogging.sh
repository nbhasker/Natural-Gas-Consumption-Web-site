./rtlamr -quiet=true -format=csv -filterid=XXXXXX | awk '{if (NR == 1 || NR % 25 == 0) print $0; fflush(stdout)}' | bash gasmeter.sh

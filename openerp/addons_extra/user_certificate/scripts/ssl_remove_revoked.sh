crlnumber=$1

grep -v "\t$crlnumber\t" index.txt > temp

mv temp index.txt
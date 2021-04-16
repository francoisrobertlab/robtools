find . -regex ".*[0-9]*-[0-9]*-cov.bw" -exec rm {} \;
find . -regex ".*[0-9]*-[0-9]*-cov.bed" -exec rm {} \;
find . -regex ".*[0-9]*-[0-9]*-forcov.bed" -exec rm {} \;
find . -regex ".*[0-9]*-[0-9]*.bed" -exec rm {} \;

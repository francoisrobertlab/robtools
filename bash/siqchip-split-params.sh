FILE=$1
COLUMNS=$(awk "{print NF; exit}" "$FILE")

for ((i=1;i<=$COLUMNS;i++)); 
do
  FILENAME=$(awk "NR==1 {print \$$i}" "$FILE")
  FILENAME="$FILENAME-params.in"
  echo "Saving parameters to file: $FILENAME"
  awk "NR>1 {print \$$i}" "$FILE" > "$FILENAME"
done


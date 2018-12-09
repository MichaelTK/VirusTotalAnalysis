#!/bin/bash
OUTPUT="$(grep 'pastebin' /home/kamyk/Documents/VirusTotalReports/itw_urls.txt)"
#echo $OUTPUT >> pastebinurls.txt
if [ -z "$OUTPUT" ]
then
      	echo "\$OUTPUT is empty"
else
	echo $OUTPUT >> pastebinurls.txt
fi
OUTPUT=""

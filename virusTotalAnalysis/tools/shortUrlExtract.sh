#!/bin/bash
OUTPUT="$(grep 'goo.gl' /home/kamyk/Documents/VirusTotalReports/itw_urls.txt)"
OUTPUT2="$(grep 'tinyurl' /home/kamyk/Documents/VirusTotalReports/itw_urls.txt)"
OUTPUT3="$(grep 'adf.ly' /home/kamyk/Documents/VirusTotalReports/itw_urls.txt)"
OUTPUT4="$(grep 'ow.ly' /home/kamyk/Documents/VirusTotalReports/itw_urls.txt)"
OUTPUT5="$(grep 'buff.ly' /home/kamyk/Documents/VirusTotalReports/itw_urls.txt)"
OUTPUT6="$(grep 'bit.do' /home/kamyk/Documents/VirusTotalReports/itw_urls.txt)"
OUTPUT7="$(grep 'mcaf.ee' /home/kamyk/Documents/VirusTotalReports/itw_urls.txt)"
OUTPUT8="$(grep 'ow.ly' /home/kamyk/Documents/VirusTotalReports/itw_urls.txt)"
OUTPUT12="$(grep 'budurl' /home/kamyk/Documents/VirusTotalReports/itw_urls.txt)"
OUTPUT13="$(grep 'moourl' /home/kamyk/Documents/VirusTotalReports/itw_urls.txt)"
OUTPUT14="$(grep 'bitly' /home/kamyk/Documents/VirusTotalReports/itw_urls.txt)"
OUTPUT15="$(grep 'bit.ly' /home/kamyk/Documents/VirusTotalReports/itw_urls.txt)"
#echo $OUTPUT >> pastebinurls.txt
if [ -z "$OUTPUT" ]
then
      	echo "\$OUTPUT is empty"
else
	echo $OUTPUT >> shortenedurls.txt
	echo $OUTPUT2 >> shortenedurls.txt
	echo $OUTPUT3 >> shortenedurls.txt
	echo $OUTPUT4 >> shortenedurls.txt
	echo $OUTPUT5 >> shortenedurls.txt
	echo $OUTPUT6 >> shortenedurls.txt
	echo $OUTPUT7 >> shortenedurls.txt
	echo $OUTPUT8 >> shortenedurls.txt
	echo $OUTPUT12 >> shortenedurls.txt
	echo $OUTPUT13 >> shortenedurls.txt
	echo $OUTPUT14 >> shortenedurls.txt
	echo $OUTPUT15 >> shortenedurls.txt
fi

#!/bin/bash

LOANS_HTML=$1
NEW_COMPLETED=$2
PERIOD=$3

BOOKREADER=`grep "BookReader" $LOANS_HTML | wc -l `
PDF=`grep "PDF" $LOANS_HTML | wc -l `
EPUB=`grep "ePub" $LOANS_HTML | wc -l `
ACS_IN_PROGRESS=`grep "Not yet downloaded" $LOANS_HTML | wc -l `
BORROWED=`grep "Borrowed" $LOANS_HTML | wc -l `
EXPIRED=`grep -v "Borrowed" $LOANS_HTML | grep -i "ago" | wc -l `

CURRENT=$(($BORROWED-$ACS_IN_PROGRESS-$EXPIRED))
PDF_PERCENT=`echo "print '%.2f' % (( $PDF / $BORROWED. ) * 100)" | python`
EPUB_PERCENT=`echo "print '%.2f' % (( $EPUB / $BORROWED. ) * 100)" | python`
BOOKREADER_PERCENT=`echo "print '%.2f' % (( $BOOKREADER / $BORROWED. ) * 100)" | python`

DISAPPEARED=$(($BORROWED-$NEW_COMPLETED))
NEW_SUCCESSFUL=$(($DISAPPEARED-$EXPIRED ))
FAILED=$(( $ACS_IN_PROGRESS - $NEW_SUCCESSFUL ))
SUCCESS_RATE=`echo "print '%.2f' % (( $NEW_SUCCESSFUL / $ACS_IN_PROGRESS. ) * 100)" | python`

echo "Loan completion stats for $PERIOD"
echo
echo "Total outstanding (current + expired + in progress) before refresh: $BORROWED"
echo "ACS loans in progress before refresh: $ACS_IN_PROGRESS"
echo "Expired (successful) loans that will disappear: $EXPIRED"
echo "Current (non-expired) loans: $CURRENT"
echo
echo "Total outstanding after refresh (all these loans are current): $NEW_COMPLETED"
echo "New successful ACS loans: $NEW_SUCCESSFUL (out of $ACS_IN_PROGRESS attempted)"
echo "ACS success rate: $SUCCESS_RATE%"
echo 
echo "BookReader loans: $BOOKREADER ($BOOKREADER_PERCENT%)"
echo "PDF loans attempted: $PDF ($PDF_PERCENT%)"
echo "EPUB loans attempted: $EPUB ($EPUB_PERCENT%)"
echo
echo "Books currently loaned out: $NEW_COMPLETED"
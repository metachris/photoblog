#!/bin/sh
echo "Building css files with recess..."
for fn in $( find ./ -name "*.less" ); do
	fn_css=$( echo $fn | sed "s/.less$/.css/g" )
	echo "$fn -> $fn_css"
    recess --compile $fn > $fn_css
done


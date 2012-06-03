#!/bin/sh
echo "Building css files with recess..."
for fn in $( find . -name "*.less" ); do
	fn_css=$( echo $fn | sed "s/.less$/.css/g" )
	fn_target="../css/$fn_css"
	echo "$fn -> $fn_target"
    recess --compile $fn > $fn_target
done


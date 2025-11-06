#!/bin/bash

MOD_NAME="wotstat.debug-utils"
d=false

while getopts "v:d" flag
do
    case "${flag}" in
        v) v=${OPTARG};;
        d) d=true;;
    esac
done


rm -rf ./build
mkdir ./build
cp -r ./res ./build

# Set version
configPath="./build/res/scripts/client/gui/mods/wotstatDebugUtils/WotstatDebugUtils.py"
perl -i -pe "s/{{VERSION}}/$v/g" "$configPath"

# Set debug mode
utilsPath="./build/res/scripts/client/gui/mods/wotstatDebugUtils/WotstatDebugUtils.py"
if [ "$d" = true ]; then
    echo "Building DEBUG version."
    perl -i -pe "s/'{{DEBUG_MODE}}'/True/g" "$utilsPath"
else
    echo "Building RELEASE version."
    perl -i -pe "s/'{{DEBUG_MODE}}'/False/g" "$utilsPath"
fi

python2 -m compileall ./build

cd ./js
bun run build
cd ../

mkdir -p ./build/res/gui/gameface/mods/wotstat-debug-utils/
cp -R ./js/dist/ ./build/res/gui/gameface/mods/wotstat-debug-utils/

meta=$(<meta.xml)
meta="${meta/\{\{VERSION\}\}/$v}"

cd ./build
echo "$meta" > ./meta.xml

folder=$MOD_NAME"_$v.wotmod"

rm -rf $folder

zip -dvr -0 -X $folder res -i "*.pyc"
zip -vr -0 -X $folder meta.xml
zip -dvr -0 -X $folder res -i "*.json"
zip -dvr -0 -X $folder res -i "*.js"
zip -dvr -0 -X $folder res -i "*.html"
zip -dvr -0 -X $folder res -i "*.css"
# zip -dvr -0 -X $folder res "*.css"
# zip -vr -0 -X $folder res -i "*.png"

cd ../
cp ./build/$folder $folder
rm -rf ./build

cp $folder $MOD_NAME"_$v.mtmod"

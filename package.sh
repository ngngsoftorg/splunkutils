#/bin/bash

cd ~/sandbox
rm importutil-$1.tar.gz
tar cvzf importutil-$1.tar.gz --exclude=".git" --exclude="LINKS" --exclude="importtable.xcodeproj" --exclude="make*" --exclude="TODOS" --exclude="package.sh" importutil

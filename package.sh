#/bin/bash

cd ~/sandbox
rm importutil-$1.tar.gz
#The COPYFILE_DISABLE=1 is needed on a mac.
COPYFILE_DISABLE=1 tar cvzf importutil-$1.tar.gz --exclude=".gitignore" --exclude=".DS_Store" --exclude=".git" --exclude="LINKS" --exclude="importtable.xcodeproj" --exclude="make*" --exclude="TODOS" --exclude="package.sh" --exclude="Crypto" --exclude="paramiko" importutil

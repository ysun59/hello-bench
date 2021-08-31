#!/bin/bash
#pullimage2CollectCheckpointTo2.sh

#DEST="helloRes_harddisk"
#DEST="helloRes_ramdisk"
DEST="helloRes_harddisk_withcache_notrm"

#arrayECHO_HELLO=("alpine1" "crux1" "debian1" "ubuntu1" "ubuntu-upstart1" "ubuntu-debootstrap1" "centos1" "fedora1" "mageia1")
#arrayECHO_HELLO=("mysql1" "mariadb1" "redis1" "rethinkdb1" "ghost1" "glassfish1" "drupal1" "cassandra1" "httpd1" "mongo1" "rabbitmq1")
#arrayECHO_HELLO=("perl1" "rakudo-star1" "pypy1" "python1" "hello-world1" "nginx1" "iojs1" "node1" "registry1")
arrayECHO_HELLO=("php1" "ruby1" "jruby1" "julia1" "gcc1" "golang1" "clojure1" "django1" "rails1" "haskell1" "hylang1" "java1" "mono1" "r-base1" "thrift1")

for((i=0; i<${#arrayECHO_HELLO[@]}; i++)) do
	echo ${arrayECHO_HELLO[i]}

#	python hello.py --registry= --op=run ${arrayECHO_HELLO[i]} |tee -a "${DEST}/Echo_HellO.txt"
#	python hello.py --registry= --op=run ${arrayECHO_HELLO[i]} |tee -a "${DEST}/CMD_ARG_WAIT.txt"

        grep 'postContainersCreate begin' "${DEST}/${arrayECHO_HELLO[i]}.txt"
        grep 'postContainersStart end' "${DEST}/${arrayECHO_HELLO[i]}.txt"
	echo " "

#	grep 'volumes.Create cost' "${DEST}/${arrayECHO_HELLO[i]}.txt"
#	grep 'Time 10' "${DEST}/${arrayECHO_HELLO[i]}.txt"
#	grep 'Time 11' "${DEST}/${arrayECHO_HELLO[i]}.txt"
#	echo " "

#       grep 'initNetworking cost:' "${DEST}/${arrayECHO_HELLO[i]}.txt"
#       grep 'CreateLayer cost:' "${DEST}/${arrayECHO_HELLO[i]}.txt"
#       grep 'prepareRootfs cost:' "${DEST}/${arrayECHO_HELLO[i]}.txt"


        echo " "
        echo " "
	echo " "
<<'COMMENT'
	grep 'Get-overlay2.go cost:' "${DEST}/${arrayECHO_HELLO[i]}.txt"
	echo " "
	grep 'Put-ovl.go cost:' "${DEST}/${arrayECHO_HELLO[i]}.txt"


        echo " "
        echo " "
	grep 'CheckpointTo cost:' "${DEST}/${arrayECHO_HELLO[i]}.txt"
	grep 'registerLinks cost:' "${DEST}/${arrayECHO_HELLO[i]}.txt"
COMMENT


#	grep 'client.go Create cost:' "${DEST}/${arrayECHO_HELLO[i]}.txt"
#       grep 'client.go Start cost:' "${DEST}/${arrayECHO_HELLO[i]}.txt"


        echo " "
        echo " "

done

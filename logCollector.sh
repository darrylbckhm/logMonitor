#!/usr/bin/bash
#Author: Darryl Beckham

logs=find / -name *\.log -not -path '/home/darrylb/[A-Za-z0-9]*'
printf("%s",$logs)
for i in {2}`
do
    grep -i -E 'error|warning|denied|failed|broken|incompatible|unable'
done

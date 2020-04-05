#!/bin/bash
cd build
ls
rm -f target/lambda.zip
zip -r target/lambda.zip .
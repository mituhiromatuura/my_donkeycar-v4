#!/bin/bash

export TF_FORCE_GPU_ALLOW_GROWTH=true

rm -r /run/shm/$1/mycar/models
mkdir /run/shm/$1/mycar/models

time donkey train --tub /run/shm/$1/mycar/data/ --model /run/shm/$1/mycar/models/mypilot.h5

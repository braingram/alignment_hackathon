#!/bin/bash

qdel `qstat | grep graham | awk '{print $1}'`
rm /groups/visitors/home/hackathon/graham/servers/*

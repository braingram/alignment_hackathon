#!/bin/bash

qdel `qstat | grep tileviewer | awk '{print $1}'`
rm /groups/visitors/home/hackathon/graham/servers/*

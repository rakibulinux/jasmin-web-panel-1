#!/bin/bash
./env/bin/celery worker -A main.taskapp -l info --autoscale=10,3
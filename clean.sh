#!/bin/bash

# Probably don't need to do this often. I created this just as a reminder.
# The reason I needed this was when I renamed the project to mysite.

find . -name "*.pyc" -exec rm -rf {} \;

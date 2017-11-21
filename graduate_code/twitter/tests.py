# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import time
from django.test import TestCase
from multiprocessing import Process, freeze_support


# Create your tests here.
import psutil
# for pid in psutil.pids():
    # print pid, psutil.Process(pid).name
psutil.Process(13488).terminate()
# 13488
import multiprocessing
# print psutil.pid_exists(16112)
# print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))


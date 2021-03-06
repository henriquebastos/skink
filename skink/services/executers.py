#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import os
import time

from skink.imports import *

class ShellExecuter(object):
    def __init__(self):
        self.start_execute = None
        self.finish_execute = None
        self.execute_beat = None
        self.timed_out = None

    def ellapsed(self, start_time=None, end_time=None):
        '''The number of milliseconds that this story took to run.'''
        if start_time is None:
            return 0

        if end_time is None:
            return time.time() - start_time

        return end_time - start_time

    def execute(self, command, base_path, change_dir=True, timeout=None):
        try:
            start_time = time.time()

            executer = Executer(command=command, working_dir=base_path)

            if self.start_execute:
                self.start_execute(executer=executer)
            executer.execute()

            while not executer.poll():
                if self.execute_beat:
                    self.execute_beat(executer=executer)

                time.sleep(0.5)
                print "[%s] - %.2f secs" % (command, self.ellapsed(start_time=start_time)) 

                if timeout and self.ellapsed(start_time=start_time) > timeout:
                    executer.kill()
                    if self.timed_out:
                        self.timed_out(executer=executer)

                    error_message = "\nThe build timed out after %d seconds!!! \n\nLOG: \n%s" % (timeout, executer.result.log)
                    return ExecuteResult(command, error_message, 1)

            log = executer.result.log
            if self.finish_execute:
                self.finish_execute(executer=executer)

            print "[%s] - Finished after %.2f secs" % (command, self.ellapsed(start_time=start_time)) 

            return ExecuteResult(command, log, executer.result.exit_code)
        except Exception, err:
            error_message = "An error occured while executing command %s: %s" % (command, err)
            return ExecuteResult(command, error_message, 1)

class ExecuteResult(object):
    def __init__(self, command, run_log, exit_code):
        self.command = command
        self.run_log = run_log
        self.exit_code = exit_code

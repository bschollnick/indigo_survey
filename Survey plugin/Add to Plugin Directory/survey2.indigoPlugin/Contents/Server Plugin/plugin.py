#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################
# Copyright(c) 2010, Perceptive Automation, LLC. All rights reserved.
# http://www.perceptiveautomation.com

##########################################################################
# Python imports
import os
import random
import shutil
import subprocess
import time
from Cheetah.Template import Template

##########################################################################
# Globals
##########################################################################

plugin_id = "com.schollnick.indigoplugin.Survey"

jquery_filename = "jquery-1.11.1.min.js"
morris_filename = "morris.min.js"
raphael_filename = "raphael-min.js"

offline = False

use_sendstatus = True

hop_seconds = {0: 125,
               1: 250,
               2: 375,
               3: 500,
               4: 625,
               5: 750,
               6: 875,
               7: 1000,
               8: 1125,
               9: 1250,
               10: 1400}

hop_colors = {0: "#0000FF",
              1: "#0000FF",
              2: "#3333CC",
              3: "#3333CC",
              4: "#FFCC99",
              5: "#CC6600",
              6: "#993300",
              7: "#990033",
              8: "#FF0000",
              9: "#CC0033",
              10: "#FF0033",
             }


def return_hops(timing):
    """
    Returns the number of estimated hops, based off the timing submitted.
    """
    for x in hop_seconds.keys():
        if hop_seconds[x] >= timing:
            return x
    return 7


def return_hop_colors(timing):
    hop_count = return_hops(timing)
    return hop_colors[hop_count]

##########################################################################


class Plugin(indigo.PluginBase):
    ########################################

    def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
        indigo.PluginBase.__init__(self,
                                   pluginId,
                                   pluginDisplayName,
                                   pluginVersion,
                                   pluginPrefs)
    # Setting debug to True will show you verbose debugging
    # information in the Indigo Event Log
        self.debug = pluginPrefs.get("showDebugInfo", False)
        self.list_of_devices = {}
        self.total_success = 0
        self.total_failure = 0
        self.time_elapsed = 0
        self.sorted_order = []
        self.survey_path = os.path.expanduser(
            os.path.normpath("~/Documents/surveys"))
    ########################################

    def __del__(self):
        indigo.PluginBase.__del__(self)

    ########################################
    # Built-in control methods
    ########################################
    def startup(self):
        # indigo.devices.subscribeToChanges()
        self.debugLog("Debug Mode is activated. (Only use if testing...)")
        self.clear_data()

    def clear_data(self):
        self.list_of_devices = {}
        self.total_success = 0
        self.total_failure = 0
        self.time_elapsed = 0
        self.sorted_order = []
        self.survey_path = os.path.expanduser(
            os.path.normpath("~/Documents/surveys"))
    ########################################

    def shutdown(self):
        # Nothing to do since deviceStopComm will be called for each of our
        # devices and that's how we'll clean up
        pass

    def make_report(self,
                    number_of_passes=1,
                    model_filter=None,
                    device_filter=None,
                    open_report=True,
                    timestamp=time.ctime(),
                    filename="survey_index.html",
                    template_name="survey_index_template.cheetah"):
        human_report_time = timestamp
        report_time = human_report_time.replace(":", "_")
        report_filename = filename
        report_path = os.path.expanduser(os.path.join(self.survey_path,
                                                      report_time))
        images_path = os.path.expanduser(os.path.join(self.survey_path,
                                                      report_time, 'images'))
        devices_path = os.path.expanduser(os.path.join(self.survey_path,
                                                       report_time, 'devices'))
        if not os.path.exists(report_path):
            os.makedirs(report_path)
            os.makedirs(devices_path)
            shutil.copytree(os.path.abspath(os.path.join(".", "templates")),
                            images_path)
        template_file = os.path.abspath('./templates/%s' % template_name)
        tmpl = ''.join(open(template_file, 'r').readlines())
        try:
            report_template = Template(tmpl)
            report_template.datatables = r"""
            $(document).ready(function() {
   $('#%s').dataTable({
       "aaSorting"	: [ [0,'desc']],
       "sDom"		:'ipflrt',
       "paging"     : false,
       "oLanguage"	: {
            "sLengthMenu": "Display _MENU_ devices per page",
            "sZeroRecords": "Nothing found - sorry",
            "sInfo": "Showing _START_ to _END_ of _TOTAL_ devices",
            "sInfoEmpty": "Showing 0 to 0 of 0 devices",
            "sInfoFiltered": "(filtered from _MAX_ total devices)"
        }  }); });
"""
            report_template.device_data = self.list_of_devices
            report_template.device_filter = device_filter
            report_template.hops = return_hops
            report_template.hop_colors = return_hop_colors
            report_template.jquery_filename = jquery_filename
            report_template.model_filter = model_filter
            report_template.morris_filename = morris_filename
            report_template.number_of_devices = len(
                self.list_of_devices.keys())
            report_template.number_of_passes = number_of_passes
            report_template.report_time = report_time
            report_template.raphael_filename = raphael_filename
            report_template.sorted_order = self.sorted_order
            report_template.timestamp = human_report_time
            report_template.total_success = self.total_success
            report_template.total_failure = self.total_failure
            report_template.time_elapsed = self.time_elapsed
            if device_filter:
                data_file = open(
                    os.path.join(devices_path, report_filename), 'w')
            else:
                data_file = open(
                    os.path.join(report_path, report_filename), 'w')

            data_file.write(str(report_template))
            data_file.close()
        finally:
            pass
        if open_report:
            subprocess.call(
                ['open', os.path.join(report_path, report_filename)])

    def gather_data(self, model=None, number_of_passes=1):
        self.clear_data()
        start_time = time.time()
        #models_to_ignore = ["TriggerLinc", "RemoteLinc"]
        for survey_pass in range(1, number_of_passes + 1):
            indigo.server.log("Survey Pass - %s" % survey_pass)
            for device in indigo.devices.iter():#"indigo.insteon"):
                reply = None

                if device.supportsStatusRequest != True:
                    continue

                if not device.protocol in [indigo.kProtocol.Insteon, indigo.kProtocol.ZWave]:
                    continue

                if model != None and \
                   device.model.strip().upper() != model.strip().upper():
                    continue

                if device.batteryLevel is not None:
                    #indigo.server.log("The device (%s) has a Battery (it might be asleep)" % (device.name))
                    continue

                if device.globalProps.has_key ("com.perceptiveautomation.indigoplugin.zwave"):
                     zwaveProps = device.globalProps["com.perceptiveautomation.indigoplugin.zwave"]
                     if zwaveProps.get("zwDevSubIndex", None) != 0:
#                         indigo.server.log("This is a secondary device %s, skipping..." % device.name)
                         continue

                if not device.address in self.list_of_devices.keys():
                    self.sorted_order.append((device.name, device.address))
                    self.list_of_devices[device.address] = {}
                    self.list_of_devices[device.address]["data"] = device
                    self.list_of_devices[device.address]["pings"] = {}
                    self.list_of_devices[device.address][
                        "pings"]["passes"] = {}
                    self.list_of_devices[device.address][
                        "pings"]["pingcount"] = number_of_passes
                    self.list_of_devices[device.address][
                        "pings"]["failure"] = 0
                    self.list_of_devices[device.address][
                        "pings"]["success"] = 0
                    self.list_of_devices[device.address]["pings"]["avg"] = 0
                    self.list_of_devices[device.address][
                        "pings"]["elapsedtime"] = 0

                if device.name <>  self.list_of_devices[device.address]["data"].name :
                    if device.model.upper().find ("FANLINC")==-1:
                        indigo.server.log ("You appear to have a duplicate device! %s and %s" %
                            (device.name, self.list_of_devices[device.address]["data"].name))
                    continue

                begin_ping_time = time.time()
                if offline:
                    timeelapsed = random.randint(0, 10) / 1.5
                    self.list_of_devices[device.address]["pings"][
                        "passes"][survey_pass] = float(timeelapsed)
                    self.list_of_devices[device.address]["pings"][
                        "elapsedtime"] += float(timeelapsed)
                    if timeelapsed >= 2000:
                        self.list_of_devices[device.address][
                            "pings"]["failure"] += 1
                        self.total_failure += 1
                    else:
                        self.list_of_devices[device.address][
                            "pings"]["success"] += 1
                        self.total_success += 1

                else:
                    reply = None
                    self.sleep (2)
                    indigo.server.waitUntilIdle()
                    result = indigo.device.ping (device, suppressLogging=True)
                    if result["Success"]:
                        timeelapsed = result["TimeDelta"]
                        self.list_of_devices[device.address]["pings"][
                            "passes"][survey_pass] = timeelapsed
                        self.list_of_devices[device.address][
                            "pings"]["elapsedtime"] += timeelapsed
                        self.list_of_devices[device.address][
                            "pings"]["success"] += 1
                        self.total_success += 1
                    else:
                        timeelapsed = 2000
                        indigo.server.log(
                            "\t%s Timed-Out, No Reply Received" % device.name)
                        self.list_of_devices[device.address][
                            "pings"]["passes"][survey_pass] = 2000
                        self.list_of_devices[device.address][
                            "pings"]["elapsedtime"] += 2000
                        self.list_of_devices[device.address][
                            "pings"]["failure"] += 1
                        self.total_failure += 1
#                self.sleep(.2)
#                indigo.server.waitUntilIdle()
        self.time_elapsed = time.time() - start_time
        indigo.server.log("Total Successes - %s" % self.total_success)
        indigo.server.log("Total Failures - %s" % self.total_failure)
        self.sorted_order = sorted(self.sorted_order, reverse=False)
        indigo.server.log("Done processing devices")

    def runConcurrentThread(self):
        #
        #
        try:
            while True:
                self.sleep(300)  # in seconds
        except self.StopThread:
            pass

    def make_individual_reports(self,
                                number_of_passes=1,
                                timestamp=time.ctime()):
        for name, addr in self.sorted_order:
            self.make_report(number_of_passes=number_of_passes,
                             model_filter=None,
                             device_filter=addr,
                             filename="%s.html" % addr,
                             open_report=False,
                             timestamp=timestamp,
                             template_name="survey_ind_device.cheetah")

    def manualDeviceUpdate(self, action):
        #
        #   Update requested via Trigger Action
        #
        indigo.server.log("1 Pass Survey Requested....")

    def survey_1pass_manualUpdate(self):
        indigo.server.log("1 Pass Survey Requested....")
        self.gather_data(model=None, number_of_passes=1)
        timestamp = time.ctime()
        self.make_report(number_of_passes=1,
                         model_filter=None,
                         filename="survey_index.html",
                         timestamp=timestamp,
                         template_name="survey_index_template.cheetah")
        self.make_individual_reports(number_of_passes=1,
                                     timestamp=timestamp)

    def survey_3pass_manualUpdate(self):
        indigo.server.log("3 Pass Survey Requested....")
        timestamp = time.ctime()
        self.gather_data(model=None, number_of_passes=3)
        self.make_report(number_of_passes=3,
                         model_filter=None,
                         filename="survey_index.html",
                         timestamp=timestamp,
                         template_name="survey_index_template.cheetah")
        self.make_individual_reports(number_of_passes=3,
                                     timestamp=timestamp)

    def survey_5pass_manualUpdate(self):
        indigo.server.log("5 Pass Survey Requested....")
        timestamp = time.ctime()
        self.gather_data(model=None, number_of_passes=5)
        self.make_report(number_of_passes=5,
                         model_filter=None,
                         filename="survey_index.html",
                         timestamp=timestamp,
                         template_name="survey_index_template.cheetah")
        self.make_individual_reports(number_of_passes=5,
                                     timestamp=timestamp)

    def survey_10pass_manualUpdate(self):
        indigo.server.log("10 Pass Survey Requested....")
        timestamp = time.ctime()
        self.gather_data(model=None, number_of_passes=10)
        self.make_report(number_of_passes=10,
                         model_filter=None,
                         filename="survey_index.html",
                         timestamp=timestamp,
                         template_name="survey_index_template.cheetah")
        self.make_individual_reports(number_of_passes=10,
                                     timestamp=timestamp)

    def survey_20pass_manualUpdate(self):
        indigo.server.log("20 Pass Survey Requested....")
        self.gather_data(model=None, number_of_passes=20)
        timestamp = time.ctime()
        self.make_report(number_of_passes=20,
                         model_filter=None,
                         filename="survey_index.html",
                         timestamp=timestamp,
                         template_name="survey_index_template.cheetah")
        self.make_individual_reports(number_of_passes=20,
                                     timestamp=timestamp)

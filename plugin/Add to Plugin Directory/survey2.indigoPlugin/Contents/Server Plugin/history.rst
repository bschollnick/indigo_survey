v2.21 (2014-07-03)
++++++++++++++++++
* Fixed issue where pinging a Plugin device could cause a problem with the HA Interface.
* Fixed ZWave survey bug

v2.20 (2014-06-30)
++++++++++++++++++
* Fixed percentage errors with Fanlincs
* Added code to deal with Zwave subdevices
* First version to support ZWave devices


2.10 (2014-06-27)
+++++++++++++++++
* Switched to using the Ping results from Indigo’s API.  This should be more accurate and dependable.
* Switched to API v1.16 Ping Command
* v2.10 REQUIRES Indigo v6.0.13 or higher, due to the dependency on API v1.16.
* Using Indigo API V1.16’s Ping command, so we can now test Insteon and Z-Wave (Pending) devices in a cross-platform manner.
* Started to update to PEP 8 standards
* v2.10 now uses the WaitUntilIdle Server command, so this should help prevent any stalls from other requests from Indigo.
* Due to the switch to Indigo’s results, I am switching the timings to Milliseconds, instead of seconds.

2.04 (2014-06-22)
+++++++++++++++++
* Suppress the duplicate address warning for fanlinc devices. The duplicate device won’t be counted / pinged, but you won’t receive the warning message for it.

2.03 (2014-06-21)
+++++++++++++++++
* Added warning message regarding duplicate devices with identical addresses
* The plugin will ignore the 2+ device with a duplicate device ID

2.02 (2014-06-20)
+++++++++++++++++
* Fixed a typo in the hop heat map lookup table

2.01 (2014-06-20)
+++++++++++++++++
* Bundled the wrong version for previous release. Re-released as v2.01.

2.00 (2014-06-19)
+++++++++++++++++
* First general release of v2.00
* Now supports actually pinging the devices, and generating a health rating based off the Pings. 

What is the Survey Plugin?

The Survey plugin is primarily used for helping diagnose or identifying issues with the
Indigo device network.  The plugin will send a “ping” out to each device on the network and
track how long it takes the device to respond.  These metrics can help identify devices that
are slow to respond, or responding erratically.

Installation

	1.	Open the "Add to Plugin Directory", and Double click on the Survey2.indigoPlugin
	    file.  Indigo will prompt you to install the plugin or upgrade any existing plugin.
	    If Indigo does not prompt you, please upgrade to the latest version, or Open the
        "Add to Plugin Directory" folder, and take the survey2.indigoPlugin file and place
        it into /Library/Application Support/Perceptive Automation/Indigo 7/Plugins
	2.	Restart the Indigo 7 Server

Basic Usage:

	⁃	From the Plugin Menu, choose the Survey Plugin, and choose How many Passes to run.
	⁃	Each Pass is a complete examination of all Insteon devices.  So the more passes
	    (and more devices you have) the longer it will take to process the report.
	⁃	While the report is running Indigo maybe slower to respond to other Home Automation
	    requests.  While I have written the software to allow Indigo to process other
	    requests, it is a good idea to run the survey’s when the system is reasonably idle.
	⁃	Survey’s will be stored in ~/Documents/Surveys, and can be deleted, or preserved
	    as required.
	⁃	This plugin currently supports all Insteon devices that support the Insteon
	    StatusRequest command.  Generally that means that any battery powered Insteon
	    device will not be tested with this plugin.

Once the report is done, Indigo will open a web browser that contains the results of the survey.

The Plugin does not have a Web Interface.

Support:

For issues or questions, please contact Benjamin@schollnick.net.

Donations:

To help fund the continued development of this plugin...  Please consider donating.

At this time my software is free, including the Indigo Web Plugin’s and attachment scripts…

But the cost to make the plugins and other software is not cheap.  Not to mention the additional cost of
keeping current in the Home Automation field, and research, etc…

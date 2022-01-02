# Residential Natural Gas Consumption Web-site

This is a JQuery and Google Charts based web-site to display residential natural gas consumption captured using an RTL-SDR software defined radio that decodes AMR transmissions from the gas meter. The data from
the gas meter - transmitted using the AMR protocol in the 900MHz band is decoded by the RTLAMR software and then transmitted using a couple of simple shell scripts to a free data repository at data.sparkfun.com. 
The web-site retrieves the data from data.sparkfun.com and renders a 7-day or 30-day view with a variety of graphs and tables. 

Cumulative, daily, hourly and instantaneous consumption are calculated and displayed.

Try it out at http://nbhasker.weebly.com/.

**Please note that as of September 2017, the data repository has been switched to Thingspeak.com as data.sparkfun.com was abruptly shut down. Scroll down for more information.**

## Getting Started

There are three distinct parts to the project:
* Setting up the SW defined radio with RTLAMR using downloadable software to capture data from the gas meter
* Using the two simple scripts included in this project to send the data to data.sparkfun.com
* Setting up a web-site using the HTML/JavaScript included above

### Setting up the SW Defined Radio
Follow the excellent quick-start guide at http://www.rtl-sdr.com/. I have the USB dongle running on a Windows 10 laptop though all the usual platforms are supported. 
I want to move this to a Raspberry Pi soon but haven't started the process yet.

1. You will of course have to obtain a USB dongle for the radio receiver. This will run you about $20-$30. 
There are several suggestions in the quick-start guide. 
I use the RTL-SDR dongle that I purchased from Amazon at the end of 2015. I believe there's now a new improved version.

2. Follow the software installation instructions for drivers and the basic software that you can use to tune in an FM radio station to make sure everything is working. I use rtl_tcp.exe to manage the USB device and the applications communicate to it via TCP/IP. This is included in the base sofwtare package.

3. You then need to install the RTLAMR software that decodes the transmissions from the natural gas meter. Start at http://www.rtl-sdr.com/rtlamr-rtl-sdr-receiver-900mhz-ism-smart-meters/.

4. Run RTLAMR and it will display the current meter readings and meter id for the meters it receives. Identify your meter by matching the meter ids displayed with the meter id on your gas meter to verify that you are able to decode your gas meter. And note your meter id as you will need it in the next step.

### Using the shell scripts to send data to data.sparkfun.com
You need to get a free data repository for the meter data by signing up at https://data.sparkfun.com/. 
You will get two keys - a "public" key that allows read access to the stream and a "private" key that allows write access to the stream. 
And no, despite the names these are not a public key cryptography key pair. 
They are just tokens and presumably you will want to keep the "private" key that allows write access secret. 
The "public" key that enables reading will be in the web-site JavaScript. 
Once you have these keys, replace the "XXXX" string in gasmeter.sh with your key.


I use two command line windows.

1. In the first, I run rtl_tcp.exe to control the USB dongle and deliver the raw data to clients over TCP/IP

2. In the second, window I run startlogging.sh. This launches RTLAMR with the appropriate parameters and pipes the output to the second shell 
script (gasmeter.sh) that parses the input it receives from RTLAMR and sends the data on to data.spark.fun using curl. 
Edit the filter-id parameter in startlogging.sh to select your gas meter id. 
Just to make things easier, the second command line window is a bash shell. 
It's currently cygwin but you could also use the Windows 10 Anniversary Edition built-in Ubuntu user mode and bash support.

Once this runs, log back in to https://data.sparkfun.com/ and verify that your data is being recorded there.

### Creating the web-site

The GasMeterVisualSummary.html can be used locally as is or copied into an actual web-page using whatever tools are available. On Weebly.com I used a "custom HTML" field and copied the code as is into that block.

## Troubleshooting

Open the developer tools window in your browser (e.g. CTRL+SHIFT+I in Chrome) and look at the console and network areas for hints. 
And of course check if the system that has the USB dongle is still running normally.
In my experience the most common failure has been that the sensing system had a Windows update and rebooted overnight. And I haven't set up the scripts to start automatically.

Data transfer from data.sparkfun.com is sometimes unreliable. The transfer sometimes fails with a "Chunked Encoding" Error or more straightforward error codes. 
Error handling for JSONP in JQuery seems hard and currently there's just a 30 second timeout.

The data occasionally gets returned with sensor values out of order. These are detected and discarded and logged to the console.

If there is missing data for a few hours, the consumption is evenly apportioned out over the intervening hours so that there isn't a misleading usage spike in the hourly consumption graphs. 
But this is not done over days if data is missing for several days. So in that case the daily consumption graph will show a spike.

The meters are assumed to roll-over at 999999 and this is handled. If your meter has a different roll-over point the code will have to be modified suitably.

## Acknowledgments
This is obviously built on some amazing foundational software!

* The excellent software available for the RTL-SDR dongles is truly amazing. Thank you!
* RTLAMR does all the heavy-lifting here. Thank you!
* There were other very helpful contributions on how to get started with JQuery and Google Charts to display data from data.sparkfun.com repositories. 
I need to track down the authors. But there help is much appreciated!

## Update: As of September 2017, the data repository is on Thingspeak.com as data.sparkfun.com was abruptly shut down

* Gasmeter.sh and GasMeterVisualSummary.html were modified to use the Thingspeak.com API. The changes were quite small
* Startlogging.sh now includes awk in the pipeline to send through only every sixth record received from RTLAMR to gasmeter.sh. This helps work around the limit of being able to retrieve only 8000 records at a time from Thingspeak.com. With a record every minute, this only covered about 5 days. By limiting the frequency of updates we should have data for a full 30 days

These changes have been checked in to the ThingSpeak branch.

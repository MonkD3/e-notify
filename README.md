# E-mail notifier :
___

This program is used to alert you (or a group of people) by mail if a given process has terminated. 

## Setup

The first step before utilizing this software comfortably is to run the following command to make sure you have all the necessary dependancies :
```cmd
pip install -r requirements.txt
```

The second is to change the [config file](./conf.ini).
You can configure this either by running the "e-notify config" option, or directly complete the [`conf.ini`](./conf.ini) file.

The critical things to check are the following :

```ini
[SMTP.servers]
server = <your SMTP server>

[SMTP.login]
sender = <your-email@domain>
```

The SMTP server is used to dispatch the mail you're sending. If you don't know it you can look it up 
on your mail application. For example in outlook office, you can find it like this : "Settings > mail > Sync email > SMTP settings".

Alternatively, you could do a google search for something like "SMTP server for \<your domain>"

The user is you, or a mail address you manage. It will be the sender of the mail.
## Example of use case :

### The use that made me develop this program
During my studies, I had to develop a lot of programs to do scientific computations. And if you ever did
that you know theses program can run for a _long time_. So I often had to wait for the end a process in 
order to analyse the result, thus leaving me doing other things not too far from the computer in case it finished.

Then I got the idea to develop this program. If I could just send a mail when the process had finished, I could 
leave the computer running and come back when I knew it had finished. 

### Other uses

Of course, I quickly realised that this program could be used for other purposes. For example, 
_critical process monitoring_. 
You could use this program to monitor a critical process of your choosing (web server, internal application, ...). 

Sending a mail to the relevant team with the error dump in case of a crash could make the recovery process faster.


## TODO :

* Add the possibility of running the command directly through the program (like an --exec option)
* Add a config file for the logger
* Add the possibility to get information on the process execution (CPU usage, memory, ...)
* Make possible to change the body of the mail (with a custom mail for example)


### Ideas 

* Make possible to monitor multiple processes ? ==> would be hard to manage the attachments for each
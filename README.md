# fbmsgsplit
Facebook lets you download an archive of all your information, including all
your messages (by going to "Settings" -> "Download a copy of your Facebook
data"). Unfortunately, the messages are all stored in one ungodly huge HTML
file, combining messages from ALL your friends. As a bonus, the messages are
not necessarily in chronological order. Are you kidding me?

fbmsgsplit is a simple python script I hacked up to split the messages file
into nicely formatted HTML files separated by user and in chronological order.
I roughly based the chat log formatting on the chat logs from the Pidgin IM
client. This script works quite well for me, but I have not done extensive
testing and your mileage may vary.

## Requirements
- Python 3 (I'm fairly certain Python 2 could work with minimal changes)
- [BeautifulSoup 4](http://www.crummy.com/software/BeautifulSoup/) (Install
  with `pip install beautifulsoup4` or your preferred package manager)

## Usage
```shell
fbmsgsplit.py messages.htm --output-dir=OUT
```
where messages.htm is the original message file and OUT is your desired output
directory.

By default, the conversation users include your own name. If you would like to
remove your name from the generated filenames, use the `--prune-users="Your
Name,Your second name"` flag, where you can specify multiple names separated by
commas. You may have multiple names in the chat logs (as I do: my actual name
and also my_facebook_id@facebook.com). This option is recommended.

You can also run 
```shell
fbmsgsplit.py -l
```
to show a list of your probable "names". This is just a guess, but should be
somewhat accurate, I hope.

As always, the `--help` flag is available when in doubt.

## Todo
Make an option to create a new file for each "day", similar to Pidgin's chat
logs.

## Issues
While I have not tested this out personally, I have a feeling that you may run
into weird problems if you have chat logs with two friends of the same name, as
Facebook's generated chat logs don't distinguish between users with the same
name. I don't think there is anything I can do about this on my end.

## License
Do whatever you want with it

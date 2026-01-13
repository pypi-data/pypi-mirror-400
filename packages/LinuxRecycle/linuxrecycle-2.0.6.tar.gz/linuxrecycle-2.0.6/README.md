# LinuxRecycle
A recycle system for linux
## How to install?
```bash
python setup.py install [--user]
```
or
```bash
pip install LinuxRecycle [--user]
```

## Usage

*  Delete a file or folder
```
del [options] filename
```
> * -f remove the file or dictory forcely without backing up.

* Show all files which have been deleted
```
del.printDB [options] [num]
```
For example, only show the last 10 file
```
del.printDB -n 5
```
you will see 
```
1220 Tue Dec 29 13:46:50 2020 xxxxxxxxx
1221 Tue Dec 29 13:46:50 2020 xxxxxxxxx
1222 Tue Dec 29 13:46:50 2020 xxxxxxxxx
1223 Tue Dec 29 13:46:56 2020 xxxxxxxxx
1224 Tue Dec 29 13:46:56 2020 xxxxxxxxx
1225 Tue Dec 29 13:53:16 2020 oh-my-god
```

* Recovery the file that deleted
```
del.recover [num] # i.e 1225
```

* Clean the trash folder
```
del.clean
```

##  Configuration

The  configuration file is located in ~/.mtdb/ with name mtrc
```
[core]
num_processor = 10
keep_days = 30
default_trash = /home/user/.trash
```
* num_processor: the number of processors used. Only increase the processors if you want to del millions files.
* keep_days: In command `del.clean`, the file has been deleted more than 30 days will be deleted. Choose the best setting for you.
* default_trash: All deleted file will back-up in this file. If you have a large disk, the file deleted from the disk will be back up in 
the disk. Such as the disk is /data, the trash folder will be /data/.trash or /data/user/.trash


## setup your crontab
* `crontab -e`
```
14 4 * * * python ~/.mtdb/clear.py
```

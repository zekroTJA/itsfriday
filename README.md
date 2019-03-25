<div align="center">
    <img src="data/testfiles/itsfriday1.jpg" height="300" />
    <h1>~ It's Friday! ~</h1>
    <strong>
        The tool for spreading friday-happiness to your Twitter followers!
    </strong><br><br>
    <!-- <a href="https://dc.zekro.de"><img height="28" src="https://img.shields.io/discord/307084334198816769.svg?style=for-the-badge&logo=discord" /></a>&nbsp; -->
    <!-- <a href="https://github.com/zekroTJA/shinpuru/releases"><img height="28" src="https://img.shields.io/github/tag/zekroTJA/shinpuru.svg?style=for-the-badge"/></a>&nbsp; -->
    <img height="28" src="https://forthebadge.com/images/badges/60-percent-of-the-time-works-every-time.svg" />&nbsp;
    <img height="28" src="https://forthebadge.com/images/badges/built-with-grammas-recipe.svg">
<br>
</div>

---

# Why?

Imagine waking up, looking on your phone and noticing: It's finally friday! You are going to work, full of aniticipation to the end of the workday - chilling with some beer or with your freinds on a tasty barbeque...

And this tool provides an easy way to spread some of your friday-happiness to your twitter followers! Just enter a collection of carefully picked, happy friday images into the config, create an [API app](https://developer.twitter.com/en/apps), enter your apps credentials and everything is ready to go.

Then, you can define a time when a randomly picked image out of the defined pool of files and URLs will be directly brought onto your followers timeline.

---

# Setup

## Requirements

- Python **(> v.3.6)**
- git
- GNU make *(optional)*

First of all, you need to [**create a Twitter API application**](https://developer.twitter.com/en/apps/create) to connect the tool to your account.

Then, clone this repository to your system and cd into the directory:

```
$ git clone https://github.com/zekroTJA/itsfriday --branch master --depth 1
$ cd itsfriday
```

Then, install the required dependencies:
```
$ python3 -m pip install -U --user -r requirements.txt
```
or simply use the make file for that:
```
$ make deps
```
*Maybe, you need to configure the Makefile before to use the right python command.*

After that was successful, run the main.py to generate a config file:
```
$ python3 ./main.py -c myConfig.json
```

Then, open the config and enter your Twitter API app credentials, the time when the event should fire every friday, a message text *(can be empty)*, and some local file directions *(directly to a file or to a folder containing image files)* or URLs to online images which should be used as pool for the randomly picked images to post.
```json
{
  "time": "9:00:00",
  "message": "Yay, it's friday!",
  "twitter": {
    "consumer_key": "s0m33x4mpl3c0n5um3rk3y",
    "consumer_secret": "4n0th3r3x4mpl3c0n5um3r53cr3t",
    "access_token_key": "th15154n3x4mpl3t0k3nk3y",
    "access_token_secret": "4ndth1s1s4l50ju5t4n3x4mpl3t0k3n53cr3t"
  },
  "image_files": [
    "https://example.com/myimagefile.png",
    "/home/you/icon.png",
    "/home/you/img"
  ]
}
```

Then, fire the handler once just for testing:
```
$ python3 ./main.py -c myConfig.json --once
```

Now, you can set up for automated tweet posting:

Therefore are two options to do so:

### I) Running as deamon

For this, you should use something like [`pm2`](https://github.com/Unitech/pm2) or [`screen`](https://www.rackaid.com/blog/linux-screen-tutorial-and-how-to).  
In this example, I will use pm2:

For that, create a start script which can be used as single executable to start the script:
> start.sh
```bash
#!/bin/bash
REPO="/path/to"
python3 ${REPO}/itsfriday/main.py -c ${REPO}/myConfig.json
```

Dont forget to make the script executable after!
```
$ chmod +x ./start.sh
```

Now, initialize the pm2 deamon:
```
$ pm2 start --name itsfriday ./start.sh
```

After that, assure that the deamon is running with
```
$ pm2 ls
```

Now, a timer is running frequently checking for the time and executing the twitter push if the trigegr time has been hit.  
If the script crashes for some reason, pm2 will restart and keep it alive *(except the script is crashing frequently directly after start to avoid an endless start loop)*.

### II) Using cron *(or something similar)*

For this example, I am using cron:

```
$ crontab -e
```

Now, create an entry to fire your post, for example, every friday at 9 AM:
```
0 9 * * 5 python3 /path/to/itsfriday/main.py -c /path/to/itsfriday/config.json --once
```

It is very important to set the flag **`--once`**, which will not start the timer loop and only fire the event once.

---

# Used 3rd-Party-Dependencies

| Dependency | Licence |
|------------|---------|
| [bear/python-twitter](https://github.com/bear/python-twitter) | [Apache V2](https://github.com/bear/python-twitter/blob/master/LICENSE) |

---

# Ideas and To-Do

- Maybe, an implementation of the API endpoint natively would be an idea to get independent from the `python-twitter` wrapper

---

© 2019 Ringo Hoffmann (zekro Development)  
Covered by MIT Licence.
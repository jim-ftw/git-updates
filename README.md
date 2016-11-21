# Git-Updates

A stupid set of python scripts that lets me automatically update single page sites. This one is written specifically for [Lovestar Race Club & Bicycle Bags](http://lovestarrace.club/).

## Requirements

1. Python 2.7
2. If you want to automate (which worker.py kind of depends on), a Heroku application with:
    1. Dead Man's snitch
    2. SparkPost
    3. Heroku Scheduler

## Usage

```python
python worker.py [-h] [-f] [--debug] [--bg BG [BG ...]]
                 [--rmbg RMBG [RMBG ...]] [--rmig RMIG [RMIG ...]]

optional arguments:
  -h, --help            show this help message and exit
  -f, --force           force html recreation
  --debug               debug logging level
  --bg BG [BG ...]      add new background image based on image number
  --rmbg RMBG [RMBG ...]
                        remove background images based on image number
  --rmig RMIG [RMIG ...]
                        remove instagram photos based on image number
```

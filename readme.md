## Cloning the Repository

To clone this repository, run the following command in your terminal:

```bash
git clone https://github.com/lupoinvesting/DC_charts_loader.git
```

load the files you wish to browse in data folder

rename config_default.json to config.json

enter the name of the file you want to browse (not the _data.feather file) in config.json



## CONTROLLING THE CHARTS
shift + 1 -> next chart
shift + 2 -> previous chart
shift + s -> screenshot


## TESTING
test with pytest:
```bash
python -m pytest --cov
```
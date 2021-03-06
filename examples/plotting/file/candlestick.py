
from math import pi
import pandas as pd

from bokeh.sampledata.stocks import MSFT
from bokeh.plotting import *

def candlestick():
    output_file("candlestick.html", title="candlestick.py example",
                js="relative", css="relative")

    hold()

    df = pd.DataFrame(MSFT)[:50]
    df['date'] = pd.to_datetime(df['date'])

    dates = df.date.astype(int) / 1000000  # source data was in microsec
    mids = (df.open + df.close)/2
    spans = abs(df.close-df.open)

    inc = df.close > df.open
    dec = df.open > df.close
    w = (dates[1]-dates[0])*0.7

    segment(dates, df.high, dates, df.low,
            x_axis_type = "datetime",
            color='#000000', tools="pan,zoom,resize", width=1000,
            name="candlestick")
    rect(dates[inc], mids[inc], w, spans[inc],
         fill_color="#D5E1DD", line_color="#000000" )
    rect(dates[dec], mids[dec], w, spans[dec],
         fill_color="#F2583E", line_color="#000000" )

    curplot().title = "MSFT Candlestick"
    xaxis()[0].major_label_orientation = pi/4
    xgrid()[0].grid_line_dash=""
    xgrid()[0].grid_line_alpha=0.3
    ygrid()[0].grid_line_dash=""
    ygrid()[0].grid_line_alpha=0.3

    return curplot()

if __name__ == "__main__":
    candlestick()
    show()  # open a browser

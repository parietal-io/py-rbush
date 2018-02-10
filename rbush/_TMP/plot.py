from bokeh.models import ColumnDataSource, DataRange1d, Plot, LinearAxis, Grid
from bokeh.models.glyphs import Rect
from bokeh.io import curdoc, show
from bokeh.plotting import figure

from rbush.data import generate_data_array
import rbush


def bboxes(js, items):
    print('node:',js['xmin'], js['ymin'], js['xmax'], js['ymax'], js['height'])
    items.append([js['xmin'], js['ymin'], js['xmax'], js['ymax'], js['height']])
    if js['height']==1:
        for c in js['children']:
            print('leaf:',c['xmin'], c['ymin'],c['xmax'],c['ymax'], 0)
            items.append([c['xmin'], c['ymin'], c['xmax'], c['ymax'], 0])
        return
    for c in js['children']:
        bboxes(c, items)


data = generate_data_array(20)
t = rbush.RBush()
t.load(data)

items = []
bboxes(rbush.to_dict(t._root), items)
items.sort(key=lambda l:-l[4])

x,y,w,h,height = [],[],[],[],[]
for x1,y1,x2,y2,hh in items:
    x.append(x1+(x2-x1)/2)
    y.append(y1+(y2-y1)/2)
    w.append(x2-x1)
    h.append(y2-y1)
    height.append('#ffcc00' if hh else '#00ccff')

source = ColumnDataSource(dict(x=x, y=y, w=w, h=h, height=height))

xdr = DataRange1d()
ydr = DataRange1d()

plot = figure(
    title=None, x_range=xdr, y_range=ydr, plot_width=300, plot_height=300,
    h_symmetry=False, v_symmetry=False, min_border=0, toolbar_location=None)

glyph = Rect(x="x", y="y", width="w", height="h", fill_alpha=0.5, fill_color="height")
plot.add_glyph(source, glyph)

show(plot)

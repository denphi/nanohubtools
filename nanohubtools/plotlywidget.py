import plotly
class FigureWidget (plotly.graph_objs.FigureWidget):
    def __init__(
        self,
        data=None,
        layout=None,
        frames=None,
        skip_invalid=False,
        **kwargs
    ):
        old_get_jconfig = plotly.offline.offline._get_jconfig
        _config = old_get_jconfig( {
            'editable':True, 
            'showLink':True, 
            'linkText' : 'Export Data',
            'displaylogo' : False
        })
        plotly.offline.offline._get_jconfig = lambda config = None : _config
        super(FigureWidget, self).__init__(data, layout, frames, skip_invalid, **kwargs)
        plotly.offline.offline._get_jconfig = old_get_jconfig

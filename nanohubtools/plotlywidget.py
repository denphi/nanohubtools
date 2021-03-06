"""
Copyright 2019 HUBzero Foundation, LLC.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

HUBzero is a registered trademark of Purdue University.

Authors:
Daniel Mejia (denphi), Purdue University (denphi@denphi.com)
"""


from _plotly_future_ import remove_deprecations
from plotly.basewidget import BaseFigureWidget as PlotlyWidget
from plotly.offline import offline

class FigureWidget (PlotlyWidget):
    def __init__(
        self,
        data=None,
        layout=None,
        frames=None,
        skip_invalid=False,
        **kwargs
    ):
        default_config = {
            'editable':True, 
            'showLink':True, 
            'linkText' : 'Export Data',
            'displaylogo' : False
        }
        config = kwargs.get('config', default_config);
        old_get_jconfig = offline._get_jconfig
        _config = old_get_jconfig( config )
        offline._get_jconfig = lambda config = None : _config
        super(FigureWidget, self).__init__(data, layout, frames, skip_invalid)
        offline._get_jconfig = old_get_jconfig

class SimplifiedFigureWidget (PlotlyWidget):
    def __init__(
        self,
        data=None,
        layout=None,
        frames=None,
        skip_invalid=False,
        **kwargs
    ):
        default_config = {
            'editable':False, 
            'showLink':False, 
            'linkText' : 'Export Data',
            'showSendToCloud' : True,
        }
        config = kwargs.get('config', default_config);
        old_get_jconfig = offline._get_jconfig
        _config = old_get_jconfig( config )
        offline._get_jconfig = lambda config = None : _config
        super(SimplifiedFigureWidget, self).__init__(data, layout, frames, skip_invalid)
        offline._get_jconfig = old_get_jconfig

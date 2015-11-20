'''
Float Layout
============

:class:`FloatLayout` honors the :attr:`~kivy.uix.widget.Widget.pos_hint`
and the :attr:`~kivy.uix.widget.Widget.size_hint` properties of its children.

.. only:: html

    .. image:: images/floatlayout.gif
        :align: right

.. only:: latex

    .. image:: images/floatlayout.png
        :align: right

For example, a FloatLayout with a size of (300, 300) is created::

    layout = FloatLayout(size=(300, 300))

By default, all widgets have their size_hint=(1, 1), so this button will adopt
the same size as the layout::

    button = Button(text='Hello world')
    layout.add_widget(button)

To create a button 50% of the width and 25% of the height of the layout and
positioned at (20, 20), you can do::

    button = Button(
        text='Hello world',
        size_hint=(.5, .25),
        pos=(20, 20))

If you want to create a button that will always be the size of layout minus
20% on each side::

    button = Button(text='Hello world', size_hint=(.6, .6),
                    pos_hint={'x':.2, 'y':.2})

.. note::

    This layout can be used for an application. Most of the time, you will
    use the size of Window.

.. warning::

    If you are not using pos_hint, you must handle the positioning of the
    children: if the float layout is moving, you must handle moving the
    children too.

'''

__all__ = ('FloatLayout', )

from kivy.uix.layout import Layout


class FloatLayout(Layout):
    '''Float layout class. See module documentation for more information.
    '''

    def __init__(self, **kwargs):
        kwargs.setdefault('size', (1, 1))
        super(FloatLayout, self).__init__(**kwargs)
        fbind = self.fbind
        update = self._trigger_layout
        fbind('children', update)
        fbind('pos', update)
        fbind('pos_hint', update)
        fbind('size_hint', update)
        fbind('size', update)

    def do_layout(self, *largs, **kwargs):
        # optimization, until the size is 1, 1, don't do layout
        if self.size == [1, 1]:
            return
        # optimize layout by preventing looking at the same attribute in a loop
        w, h = kwargs.get('size', self.size)
        x, y = kwargs.get('pos', self.pos)
        for c in self.children:
            # size
            shw, shh = c.size_hint
            if shw and shh:
                c.size = int(w * shw), int(h * shh)
            elif shw:
                c.width = int(w * shw)
            elif shh:
                c.height = int(h * shh)

            # pos
            for key, value in c.pos_hint.items():
                if key == 'x':
                    c.x = int(x + value * w)
                elif key == 'right':
                    c.right = int(x + value * w)
                elif key == 'pos':
                    c.pos = int(x + value[0] * w), int(y + value[1] * h)
                elif key == 'y':
                    c.y = int(y + value * h)
                elif key == 'top':
                    c.top = int(y + value * h)
                elif key == 'center':
                    c.center = int(x + value[0] * w), int(y + value[1] * h)
                elif key == 'center_x':
                    c.center_x = int(x + value * w)
                elif key == 'center_y':
                    c.center_y = int(y + value * h)

    def add_widget(self, widget, index=0):
        widget.bind(
            #size=self._trigger_layout,
            #size_hint=self._trigger_layout,
            pos=self._trigger_layout,
            pos_hint=self._trigger_layout)
        return super(FloatLayout, self).add_widget(widget, index)

    def remove_widget(self, widget):
        widget.unbind(
            #size=self._trigger_layout,
            #size_hint=self._trigger_layout,
            pos=self._trigger_layout,
            pos_hint=self._trigger_layout)
        return super(FloatLayout, self).remove_widget(widget)

"""
This file is used to test the docstring examples in the code.py file.
Just copy the code examples from the docstrings and paste them here.
Then run this file to see if there are any errors.
You can also use this file to test code snippets that are not in the
docstrings.

leave the first three lines as they are. They are used to set up the
path so that the imports work correctly. We add the
parent directory to the path so that we can import the morphui module.
In case the lines are missing, here they are again:

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parents[1].resolve()))
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parents[1].resolve()))

from morphui.app import MorphApp
from morphui.uix.label import MorphSimpleLabel
from morphui.uix.button import MorphIconButton
from morphui.uix.tooltip import MorphTooltip
from morphui.uix.floatlayout import MorphFloatLayout
from morphui.uix.gridlayout import MorphGridLayout

class MyApp(MorphApp):

    def build(self) -> MorphFloatLayout:
        self.theme_manager.theme_mode = 'Dark'
        self.theme_manager.seed_color = 'morphui_teal'

        icons=iter((
            'arrow-top-left-thick',
            'arrow-up-bold',
            'arrow-top-right-thick',
            'arrow-left-bold',
            'arrow-decision',
            'arrow-right-bold',
            'arrow-bottom-left-thick',
            'arrow-down-bold',
            'arrow-bottom-right-thick',))

        buttons = []
        for direction in ['up', 'center', 'down']:
            for anchor in ['left', 'center', 'right']:
                buttons.append(
                    MorphIconButton(
                        icon=next(icons),
                        tooltip=MorphTooltip(
                            MorphSimpleLabel(
                                text=f"Anchor pos: {anchor!r}",
                                auto_size=True),
                            MorphSimpleLabel(
                                text=f"Opening dir: {direction!r}",
                                auto_size=True),
                            menu_anchor_position=anchor,
                            menu_opening_direction=direction,),),)
        
        layout = MorphFloatLayout(
            MorphGridLayout(
                *buttons,
                cols=3,
                spacing=5,
                auto_size=(True, True),
                pos_hint={'center_x': 0.5, 'center_y': 0.5},),
            theme_color_bindings={
                'normal_surface_color': 'surface_color',},)
        return layout

if __name__ == '__main__':
    MyApp().run()

#
#   Imandra Inc.
#
#   decomps.py
#

from textual.containers import (
    HorizontalGroup,
    VerticalGroup,
    VerticalScroll,
)
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Button, Footer, Label, Rule

from ..common import MyHeader, bind, decomp_ui


class DecompsScreen(Screen):
    """ """

    mmodel = reactive(None, recompose=True)

    def on_mount(self):
        self.title = 'Region Decompositions'
        bind(self, 'mmodel')

    # def watch_mmodel(self, old_value: MetaModel, new_value: MetaModel):
    #     """ """
    #     pass

    def compose(self):
        """ """

        yield MyHeader()
        with VerticalScroll():
            if self.mmodel:
                for idx, (path, model) in enumerate(self.mmodel.models.items()):
                    yield Rule()
                    yield Label(f'[$primary][b]{path}[/b][/]')
                    with HorizontalGroup():
                        yield Button('View model', id=f'btn_{idx}_view_model')
                        with VerticalGroup() as v:
                            v.styles.padding = [0, 0, 0, 1]
                            for decomp in model.decomps():
                                yield Rule()
                                yield decomp_ui(decomp)

        yield Footer()


if __name__ == '__main__':
    pass

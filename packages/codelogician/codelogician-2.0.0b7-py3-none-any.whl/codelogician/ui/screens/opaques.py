#
#   Imandra Inc.
#
#   screen_opaques.py
#


from textual.containers import (
    HorizontalGroup,
    VerticalGroup,
    VerticalScroll,
)
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import (
    Button,
    Footer,
    Label,
    Rule,
    Static,
)

from ..common import MyHeader, bind, opaques_rich


class OpaquesScreen(Screen):
    """ """

    mmodel = reactive('', recompose=True)

    def on_mount(self):
        self.title = 'Opaques'
        bind(self, 'mmodel')

    # def watch_mmodel(self, old_value: MetaModel, new_value: MetaModel):
    #     pass

    def compose(self):
        """ """
        yield MyHeader()
        with VerticalScroll():
            # mmodel can still be None - `curr_meta_model` doesn't guarantee anything
            if self.mmodel:
                for model_idx, (path, model) in enumerate(self.mmodel.models.items()):
                    yield Rule()
                    yield Label(f'[$primary][b]{path}[/b][/]')
                    with HorizontalGroup():
                        yield Button('View model', id=f'view_{model_idx}')
                        # yield Rule("vertical")
                        with VerticalGroup():
                            if model.agent_state is not None:
                                _, table = opaques_rich(model.agent_state.opaque_funcs)
                                yield Static(table)
                            else:
                                yield Static(' [$foreground-muted]Not formalised[/]')
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed):
        """Need to go to the `model` screen and focus on the specific model"""
        # TODO Implement this
        pass

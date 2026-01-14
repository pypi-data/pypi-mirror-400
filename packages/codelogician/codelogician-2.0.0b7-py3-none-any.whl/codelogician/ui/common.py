import datetime
from enum import Enum
from functools import partial
from pathlib import Path

from pydantic import BaseModel
from rich.console import Group
from rich.text import Text
from textual.containers import HorizontalGroup, ScrollableContainer, VerticalGroup
from textual.reactive import reactive
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Button, Footer, Static
from textual.widgets._header import HeaderIcon, HeaderTitle

from ..util import maybe_else


def bind(screen, *names):
    def update(name, _, new):
        setattr(screen, name, new)

    for name in names:
        screen.watch(screen.app, name, partial(update, name))


class Source(Enum):
    NoSource = 'No_source'
    Server = 'Server'
    Disk = 'Disk'


class Status(BaseModel):
    source: Source

    disk_loaded: bool | None = None
    disk_error: str | None = None
    disk_path: Path | None = None

    server_addr: str | None = 'http://127.0.0.1:8000'
    server_last_update: datetime.datetime | None = None
    server_error: str | None = None

    def error_status(self):
        return (
            ('SERVER ERROR' if self.server_error else '')
            if self.source == Source.Server
            else ('DISK ERROR' if self.disk_error else '')
        )

    # fmt: off
    def __rich__(self):
        if self.source == Source.Server:
            fields = [('Source: ', 'Server'),
                      ('Server address: ', self.server_addr),
                      ('Server last update: ', self.server_last_update),
                      ('Server error: ', self.server_error)]
        else:
            fields = [('Source: ', 'Disk'),
                      ('Disk path: ', self.disk_path),
                      ('Disk loaded: ', self.disk_loaded),
                      ('Disk error: ', self.disk_error)]

        return Group(*(Text.assemble(label, (str(val), 'bold')) for label, val in fields))
    # fmt: on


class TUIConfig(BaseModel):
    using_server: bool = False
    disk_source: str = '/'
    server_source: str = 'localhost:8000'


class InfoScreen(Screen):
    def __init__(self, msg, screen_type='error', name=None, id=None, classes=None):
        super().__init__(name, id, classes)
        self._msg = msg
        self._type = screen_type

    def compose(self):
        yield MyHeader()

        # TODO This is just a placeholder - we should do more advanced conditional styling
        # fmt: off
        yield (Static(f'Error: {self._msg}') if self._type == 'error' else
               Static(f'Info: {self._msg}') if self._type == 'info' else
               Static(f'Scucess: {self._msg}'))
        # fmt: on

        yield Button('Ok')
        yield Footer()

    def on_button_pressed(self, event):
        self.app.pop_screen()


class Border(Widget):
    # foreground-muted?
    DEFAULT_CSS = """Border {
        border: round $foreground;
        border-title-align: left;
        height: auto;
        overflow-x: auto;
        }"""

    def __init__(self, title, *args, **kwargs):
        Widget.__init__(self, *args, **kwargs)
        if title:
            self.border_title = title


class HeaderStatus(Static):
    DEFAULT_CSS = 'HeaderStatus { height: 100%; width: auto; dock: right; }'
    status_summary = reactive('', layout=True)

    def render(self):
        return Text.from_markup(self.status_summary)


class MyHeader(Widget):
    DEFAULT_CSS = """
    MyHeader {
        dock: top;
        width: 100%;
        background: black;
        color: $foreground;
        height: 1;
        margin-bottom: 1;
    }
    """

    mmodel = reactive(None)
    status = reactive(None)
    status_summary = reactive('   ')

    def __init__(self):
        Widget.__init__(self)
        bind(self, 'mmodel', 'status')

    def watch_status(self):
        string = ''
        if self.status:
            string += f'[bright_red]{self.status.error_status()}[/bright_red]'

        if self.mmodel:
            from imandra.u.agents.code_logician.base import FormalizationStatus as FS

            # fmt: off
            counts = self.mmodel.summary()['frm_statuses']
            bad = counts[FS.INADMISSIBLE]
            ok = (counts[FS.TRANSPARENT]
                  + counts[FS.EXECUTABLE_WITH_APPROXIMATION]
                  + counts[FS.ADMITTED_WITH_OPAQUENESS])

            def is_in_progress(m): return 1 if m.status().outstanding_task_ID else 0

            in_progress = sum(map(is_in_progress, self.mmodel.models.values()))
            in_progress_str = f'[blink]{in_progress}[/blink]' if in_progress > 0 else '0'
            string += (f' waiting: [dim]{counts[FS.UNKNOWN] - in_progress}[/dim] | '
                       f'processing: {in_progress_str} | '
                       f'[light_green]✓ {ok}[/light_green] '
                       f'[bright_red]✘ {bad}[/bright_red]')
            # fmt: on

        self.status_summary = string

    def compose(self):
        icon = Text.assemble((' OIO', 'bold #3363FF'), (' IMANDRA', 'bold #00C6CF'))
        icon_widget = HeaderIcon()
        icon_widget.icon = icon
        icon_widget.styles.width = 'auto'
        icon_widget.styles.dock = 'left'
        yield icon_widget
        yield HeaderTitle()
        yield HeaderStatus().data_bind(MyHeader.status_summary)

    def on_mount(self):
        def set_title(title):
            try:
                self.query_one(HeaderTitle).update(self.screen.title or self.app.title)
            except Exception as e:
                print(f'???? {e}')

        self.watch(self.screen, 'title', set_title)


def opaques_rich(opaques, limit=None):
    from rich.table import Table

    header = Text(f'Opaque Functions ({len(opaques)}):', style='bold')
    table = Table(show_header=False, box=None, padding=(0, 1))
    for i, opa in enumerate(opaques[:limit], 1):
        num_assumptions = len(opa.assumptions) if hasattr(opa, 'assumptions') else 0
        has_approx = hasattr(opa, 'approximation') and opa.approximation is not None
        status_icon = (
            '[bright_green]✓[/bright_green]'
            if has_approx
            else '[bright_yellow]○[/bright_yellow]'
        )
        table.add_row(
            f'{i}.',
            f'{status_icon} {opa.name}',
            f'({num_assumptions} assumptions)',
        )
    if limit is not None and len(opaques) > limit:
        table.add_row('...', f'[dim]({len(opaques) - limit} more)[/dim]', '')

    return header, table


class HScroll(ScrollableContainer):
    DEFAULT_CSS = """
    HScroll {
        width: 150;
        height: auto;
        layout: vertical;
        overflow-y: hidden;
        overflow-x: scroll;
    }
    """


def named_vals(name_val_pairs):
    def hg(name, val):
        l = Static(f'[$primary]{name}[/]: ')
        v = Static(str(val))
        v.styles.width = '1fr'
        l.styles.width = 'auto'
        return HorizontalGroup(l, v)

    return VerticalGroup(*(hg(name, val) for name, val in name_val_pairs))


def decomp_ui(decomp):
    from imandra.u.agents.code_logician.base.region_decomp import (
        render_decomp_res_content,
    )
    from rich.panel import Panel

    parts = [  # list[(Optional(x), str, (x -> rich))]
        (
            decomp.raw,
            'Raw Request',
            lambda raw: Group(
                Text(f'Src func name: {raw.src_func_name}'),
                Text(f'IML func name: {raw.iml_func_name}'),
                Text(f'Description: {raw.description}'),
            ),
        ),
        (decomp.data, 'Request Data', lambda d: d.__rich__()),
        (decomp.res, 'Result', lambda c: Group(*render_decomp_res_content(c))),
        (decomp.test_cases, 'Test Cases', decomp.render_test_cases),
    ]
    return Static(Group(*[Panel(f(x), title=t) for x, t, f in parts if x]))


def vg_ui(vg):
    from rich.pretty import Pretty

    def req_repr(req):
        return named_vals(
            [
                ('Src func names', req.src_func_names),
                ('IML func names', req.iml_func_names),
                ('Description', req.description),
                ('Logical statement', req.logical_statement),
            ]
        )

    def data_repr(data):
        return named_vals([('Predicate', data.predicate), ('Kind', data.kind)])

    def maybe_(f, x):
        return maybe_else(Static('None'), f, x)

    def text_repr(x):
        return Text(repr(x))

    return VerticalGroup(
        Border('RawVerifyReq', maybe_(req_repr, vg.raw)),
        Border('VerifyReqData', maybe_(data_repr, vg.data)),
        Border(
            'Result', HScroll(Static(Pretty(vg.res, overflow='ellipsis', no_wrap=True)))
        ),
    )


def text_read(f):
    with open(f) as s:
        return s.read()


def local_file(name):
    return Path(__file__).parent / name

from _typeshed import Incomplete
from contextlib import contextmanager
from enum import Enum

class ENUM_RichColor(str, Enum):
    cE_RCH_BLACK = 'black'
    cE_RCH_RED = 'red'
    cE_RCH_GREEN = 'green'
    cE_RCH_YELLOW = 'yellow'
    cE_RCH_BLUE = 'blue'
    cE_RCH_MAGENTA = 'magenta'
    cE_RCH_CYAN = 'cyan'
    cE_RCH_WHITE = 'white'
    cE_RCH_GREY = 'grey'
    cE_RCH_ORANGE = 'orange'
    cE_RCH_PINK = 'pink'
    cE_RCH_PURPLE = 'purple'
    cE_RCH_BROWN = 'brown'
    cE_RCH_TEAL = 'teal'
    cE_RCH_BRIGHT_BLACK = 'bright_black'
    cE_RCH_BRIGHT_RED = 'bright_red'
    cE_RCH_BRIGHT_GREEN = 'bright_green'
    cE_RCH_BRIGHT_YELLOW = 'bright_yellow'
    cE_RCH_BRIGHT_BLUE = 'bright_blue'
    cE_RCH_BRIGHT_MAGENTA = 'bright_magenta'
    cE_RCH_BRIGHT_CYAN = 'bright_cyan'
    cE_RCH_BRIGHT_WHITE = 'bright_white'

class CLASS_RichTUI:
    console: Incomplete
    Pmi_RefreshRate: Incomplete
    Pmi_LogLines: Incomplete
    live: Incomplete
    tables: Incomplete
    logs: Incomplete
    single_line_msg: str
    progress_bar: Incomplete
    progress_task_id: Incomplete
    def __init__(self, Pmi_RefreshRate: int = 4, Pmi_LogLines: int = 10) -> None: ...
    def CUF_AddTable(self, Pms_TableID, Pml_Columns) -> None: ...
    def CUF_DisplayMulti(self, Pms_TableID, Pms_RowKey, Pml_ValueList) -> None: ...
    def CUF_Print(self, Pms_MsgStr: str): ...
    @contextmanager
    def CUF_Status(self, Pms_MsgSTR: str): ...
    def CUF_DisplaySingle(self, Pms_MsgSTR, Pms_Color: str = 'cyan') -> None: ...
    def CUF_AddLog(self, Pms_LogMsg, Pms_Color: str = 'white') -> None: ...
    def CUF_ProgressStartP(self, Pms_Description: str = 'Progress', Pmi_Total: int = 100, Pms_BarColor: str = 'green', Pmf_PercentWidth: float = 0.3) -> None: ...
    def CUF_ProgressAdvance(self, Pmi_Step: int = 1) -> None: ...
    def CUF_ProgressStop(self) -> None: ...
    def CUF_Clear(self) -> None: ...
    def CUF_Close(self) -> None: ...

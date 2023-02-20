from typing import Callable, Dict, Iterable, Optional, Union
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


keys = [Qt.Key.Key_T,
        Qt.Key.Key_P,]

buttons = [
    Qt.MouseButton.LeftButton,
    Qt.MouseButton.RightButton,
    Qt.MouseButton.MiddleButton
]


class MouseEvent(QObject):
    state_changed = pyqtSignal(bool, object)  # pressed(), QKeyEvent | QMouseEvent
    
    def __init__(self, btn: Qt.MouseButton, desc: str = '', slot: Optional[Callable] = None):
        super().__init__()
        self.__pressed = False
        self.__code = btn
        self.__desc = desc
        if slot is not None:
            self.state_changed.connect(slot)
        
    def set_pressed(self, is_pressed: bool, event: QMouseEvent):
        self.__pressed = is_pressed
        self.state_changed.emit(self.__pressed, event)
        
    def change_pressed(self, event: QMouseEvent):
        self.__pressed = not self.__pressed
        self.state_changed.emit(self.__pressed, event)
        
    def pressed(self) -> bool:
        return self.__pressed
    
    def code(self) -> int:
        return self.__code
    
    def desc(self) -> str:
        btn = {
            Qt.MouseButton.LeftButton: 'LMB',
            Qt.MouseButton.RightButton: 'RMB',
            Qt.MouseButton.MiddleButton: 'MMB'
        }.get(self.__code, '?')
        return f'{self.__desc} ({btn}):'
    
    def set_desc(self, desc: str):
        self.__desc = desc
    

class KeyEvent(QObject):
    state_changed = pyqtSignal(bool)
    
    def __init__(self, code: Qt.Key, desc: str = '', slot: Optional[Callable] = None):
        super().__init__()
        self.__pressed = False
        self.__code = code
        self.__desc = desc
        if slot is not None:
            self.state_changed.connect(slot)
        
    def set_pressed(self, is_pressed: bool, event: QKeyEvent=None):
        self.__pressed = is_pressed
        self.state_changed.emit(self.__pressed, event)
        
    def change_pressed(self, event: QKeyEvent=None):
        self.__pressed = not self.__pressed
        self.state_changed.emit(self.__pressed, event)
        
    def pressed(self) -> bool:
        return self.__pressed
    
    def code(self) -> int:
        return self.__code
    
    def desc(self) -> str:
        return f'{self.__desc} ({chr(self.__code)}):'
    
    def set_desc(self, desc: str):
        self.__desc = desc


class InputEventManager:
    def __init__(self, widget: QWidget,
                 mb_events: Iterable[MouseEvent]=[], 
                 key_events: Iterable[KeyEvent]=[]) -> None:
        self.__widget = widget
        self.__map: Dict[int, Union[MouseEvent, KeyEvent]] = {}
        self.__create_map(mb_events, key_events)
        
    def __getitem__(self, code: Union[Qt.Key, Qt.MouseButton]) -> bool:
        """
        >>> iem = InputEventManager(...)
        >>> event = KeyEvent(..., key=Qt.Key.Key_T)
        >>> iem.append_event(event)
        >>>
        >>> # Usage
        >>> iem[Qt.Key.Key_T]   # case 1
        >>> iem[event]          # case 2
        ... KeyEvent(..., key=Qt.Key.Key_T)
        """
        if not isinstance(code, (Qt.Key, Qt.MouseButton)):
            raise TypeError(f'{code} is not instance of [Qt.Key | Qt.MouseButton]')
        try:
            return self.__map[code].pressed()
        except KeyError:
            raise KeyError(f"InputEventManager hasn't this [KeyEvent | MouseEvent]: {code}") 
    
    def __setitem__(self, code: Union[Qt.Key, Qt.MouseButton], pressed: bool):
        """
        >>> iem = InputEventManager(...)
        >>> event = KeyEvent(..., key=Qt.Key.Key_T)
        >>> iem.append_event(event)
        >>>
        >>> # Usage
        >>> iem[Qt.Key.Key_T] = True    # case 1
        >>> iem[event] = True           # case 2
        >>> iem[Qt.Key.Key_T].pressed()
        True
        """
        if not isinstance(code, (Qt.Key, Qt.MouseButton)):
            raise TypeError(f'{code} is not instance of [Qt.Key | Qt.MouseButton]')
        if not isinstance(pressed, bool):
            raise TypeError(f'value is not instance of <bool>')
        try:
            self.__map[code].set_pressed(pressed)
        except KeyError:
            raise KeyError(f"InputEventManager hasn't this [KeyEvent | MouseEvent]: {code}") 
    
    def __delitem__(self, _):
        raise AttributeError('Please to use InputEventManager.remove_event()')

    def __create_map(self, mb_events, key_events):
        self.__map = {event.code(): event for event in mb_events + key_events}
                    
    def remove_event(self, event_or_code: Union[Qt.Key, Qt.MouseButton, MouseEvent, KeyEvent]):
        """ Removes event from map of `InputEventManager` """
        if isinstance(event_or_code, (MouseEvent, KeyEvent)):
            event_or_code = event_or_code.code()
        return self.__map.pop(event_or_code, None)
        
    def append_event(self, event: Union[MouseEvent, KeyEvent]) -> int:
        """ Appends event to map of `InputEventManager` """
        self.__map[event.code()] = event
        return event.code()
    
    def change_pressed(self, code: Union[Qt.Key, Qt.MouseButton]):
        """ Inverts `pressed` at `KeyEvent` or `MouseEvent` """
        try:
            self.__map[code].change_pressed()
        except KeyError:
            raise KeyError(f"InputEventManager hasn't this [KeyEvent | MouseEvent]: {code}")
    
    def set_pressed_without_key_error(self, code: Union[Qt.Key, Qt.MouseButton],
                                      pressed: bool, event: Union[QKeyEvent, QMouseEvent] = None):
        obj = self.__map.get(code)
        if obj is not None:
            obj.set_pressed(pressed, event)
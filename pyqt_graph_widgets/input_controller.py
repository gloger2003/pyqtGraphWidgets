from typing import Dict, Iterable, Union
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


class MBEvent:
    """ MouseButtonEvent """
    state_changed = pyqtSignal(bool)
    
    def __init__(self, btn: Qt.MouseButton, desc: str):
        self.__pressed = False
        self.__btn = btn
        self.__desc = desc
        
    def set_pressed(self, is_pressed: bool):
        self.__pressed = is_pressed
        self.state_changed.emit(self.__pressed)
        
    def change_pressed(self):
        self.__pressed = not self.__pressed
        self.state_changed.emit(self.__pressed)
        
    def pressed(self) -> bool:
        return self.__pressed
    
    def key(self) -> int:
        return self.__btn
    
    def desc(self) -> str:
        btn = {
            Qt.MouseButton.LeftButton: 'LMB',
            Qt.MouseButton.RightButton: 'RMB',
            Qt.MouseButton.MiddleButton: 'MMB'
        }.get(self.__btn, '?')
        return f'{self.__desc} ({btn}):'
    

class KeyEvent:
    """ KeyboardEvent """
    state_changed = pyqtSignal(bool)
    
    def __init__(self, code: Qt.Key, desc: str):
        self.__pressed = False
        self.__code = code
        self.__desc = desc
        
    def set_pressed(self, is_pressed: bool):
        self.__pressed = is_pressed
        self.state_changed.emit(self.__pressed)
        
    def change_pressed(self):
        self.__pressed = not self.__pressed
        self.state_changed.emit(self.__pressed)
        
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
                 mb_events: Iterable[MBEvent], 
                 key_events: Iterable[KeyEvent]) -> None:
        self.__widget = widget
        self.__map: Dict[int, Union[MBEvent, KeyEvent]] = self.__create_map(mb_events, key_events)
        
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
            return self.__map[code]
        except KeyError:
            raise KeyError(f"InputEventManager hasn't this [KeyEvent | MBEvent]: {code}") 
    
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
            self.__map[code] = pressed
        except KeyError:
            raise KeyError(f"InputEventManager hasn't this [KeyEvent | MBEvent]: {code}") 
    
    def __delitem__(self, _):
        raise AttributeError('Please to use InputEventManager.remove_event()')

    def __create_map(self, mb_events, key_events):
        for event in mb_events + key_events:
            self.__map[event.code(): event]
                    
    def remove_event(self, event_or_code: Union[Qt.Key, Qt.MouseButton, MBEvent, KeyEvent]):
        """ Removes event from map of `InputEventManager` """
        if isinstance(event_or_code, (MBEvent, KeyEvent)):
            event_or_code = event_or_code.code()
        return self.__map.pop(event_or_code, None)
        
    def append_event(self, event: Union[MBEvent, KeyEvent]) -> int:
        """ Appends event to map of `InputEventManager` """
        self.__map[event.code()] = event
        return event.code()
    
    def change_pressed(self, code: Union[Qt.Key, Qt.MouseButton]):
        """ Inverts `pressed` at `KeyEvent` or `MBEvent` """
        try:
            self.__map[code].change_pressed()
        except KeyError:
            raise KeyError(f"InputEventManager hasn't this [KeyEvent | MBEvent]: {code}") 
from dataclasses import field
from enum import Enum
from typing import List, Optional

import flet as ft


class FabDirection(Enum):
    """you can set where the child will appear"""

    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"


@ft.control("FabChild")
class FabChild(ft.LayoutControl):
    """you can determine which buttons will appear"""

    label: Optional[str] = None
    label_style: Optional[ft.TextStyle] = None
    label_bgcolor: Optional[ft.ColorValue] = None
    label_widget: Optional[ft.Control] = None
    label_shadow: Optional[List[ft.BoxShadowValue]] = None
    child: Optional[ft.Control] = None
    bgcolor: Optional[ft.ColorValue] = None
    foreground_color: Optional[ft.ColorValue] = None
    shape: Optional[ft.ShapeBorder] = None

    on_tap: Optional[ft.ControlEventHandler["FabChild"]] = None
    on_long_press: Optional[ft.ControlEventHandler["FabChild"]] = None


@ft.control("ExpandFab")
class FloatingActionButton(ft.LayoutControl):
    """
    With this class, you can create cool FABs.
    """

    children: List[FabChild] = field(default_factory=list)
    bgcolor: Optional[ft.ColorValue] = None
    foreground_color: Optional[ft.ColorValue] = None
    active_bgcolor: Optional[ft.ColorValue] = None
    active_foreground_color: Optional[ft.ColorValue] = None
    gradient: Optional[ft.Gradient] = None
    gradient_box_shape: ft.BoxShape = ft.BoxShape.RECTANGLE
    elevation: ft.Number = 6.0
    button_size: ft.Size = field(default_factory=lambda: ft.Size(56.0, 56.0))
    children_button_size: ft.Size = field(default_factory=lambda: ft.Size(56.0, 56.0))
    mini: bool = False
    visible: bool = True
    overlay_opacity: ft.Number = 0.8
    overlay_color: Optional[ft.ColorValue] = None
    hero_tag: Optional[str] = None
    icon: Optional[ft.IconDataOrControl] = None
    active_icon: Optional[ft.IconDataOrControl] = None
    child: Optional[ft.Control] = None
    active_child: Optional[ft.Control] = None
    switch_label_position: bool = False
    use_rotation_animation: bool = True
    label: Optional[ft.Control] = None
    active_label: Optional[ft.Control] = None
    direction: FabDirection = FabDirection.UP
    close_manually: bool = False
    render_overlay: bool = True
    curve: ft.AnimationCurve = ft.AnimationCurve.FAST_OUT_SLOWIN
    animation_duration: ft.DurationValue = field(
        default_factory=lambda: ft.Duration(milliseconds=150)
    )
    is_open_on_start: bool = False
    close_dial_on_pop: bool = True
    child_margin: ft.MarginValue = field(
        default_factory=lambda: ft.Margin.symmetric(horizontal=16, vertical=0)
    )
    child_padding: ft.PaddingValue = field(
        default_factory=lambda: ft.Padding.symmetric(vertical=5)
    )
    space_between_children: Optional[ft.Number] = None
    spacing: Optional[ft.Number] = None
    animation_curve: Optional[ft.AnimationCurve] = None

    on_open: Optional[ft.ControlEventHandler["FloatingActionButton"]] = None
    on_close: Optional[ft.ControlEventHandler["FloatingActionButton"]] = None
    on_press: Optional[ft.ControlEventHandler["FloatingActionButton"]] = None

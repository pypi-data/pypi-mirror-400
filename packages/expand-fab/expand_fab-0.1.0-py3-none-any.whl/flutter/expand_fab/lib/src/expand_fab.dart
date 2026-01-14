import "package:flutter/material.dart";
import 'package:flet/flet.dart';
import 'package:flutter_speed_dial/flutter_speed_dial.dart';

import './child_fab.dart';

class ExpandFabControl extends StatelessWidget {
  final Control control;

  ExpandFabControl({key, required this.control});
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    var children = control.children("children");
    var visible = control.getBool("visible", true)!;
    var bgColor = control.getColor("bgcolor", context);
    var foregroundColor = control.getColor("foreground_color", context);
    var activeBgColor = control.getColor("active_bgcolor", context);
    var activeForegroundColor =
        control.getColor("active_foreground_color", context);
    var gradient = control.getGradient("gradient", theme);
    var gradientBoxShape =
        control.getBoxShape("gradient_box_shape", BoxShape.rectangle)!;
    var elevation = control.getDouble("elevation", 6.0)!;
    var buttonSize = control.getSize("button_size", Size(56.0, 56.0))!;
    var childrenButtonSize =
        control.getSize("children_button_size", Size(56.0, 56.0))!;
    var mini = control.getBool("mini", false)!;
    var overlayOpacity = control.getDouble("overlay_opacity", 0.8)!;
    var overlayColor = control.getColor("overlay_color", context);
    var heroTag = control.getString("hero_tag");
    var icon = control.getIconData("icon");
    var activeIcon = control.getIconData("active_icon");

    // widget build
    Widget fabButton = SpeedDial(
      children: parseChildDial(children, context),
      visible: visible,
      backgroundColor: bgColor,
      foregroundColor: foregroundColor,
      activeBackgroundColor: activeBgColor,
      activeForegroundColor: activeForegroundColor,
      gradient: gradient,
      gradientBoxShape: gradientBoxShape,
      elevation: elevation,
      buttonSize: buttonSize,
      childrenButtonSize: childrenButtonSize,
      mini: mini,
      overlayOpacity: overlayOpacity,
      overlayColor: overlayColor,
      heroTag: heroTag,
      icon: icon,
      activeIcon: activeIcon,
    );

    return LayoutControl(
      control: control,
      child: fabButton,
    );
  }
}

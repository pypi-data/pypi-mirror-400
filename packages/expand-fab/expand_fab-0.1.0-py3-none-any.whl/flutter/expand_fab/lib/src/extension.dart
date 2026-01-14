import 'package:flet/flet.dart';
import 'package:flutter/material.dart';

import 'expand_fab.dart';

class Extension extends FletExtension {
  @override
  Widget? createWidget(Key? key, Control control) {
    switch (control.type) {
      case "ExpandFab":
        return ExpandFabControl(control: control);
      default:
        return null;
    }
  }
}

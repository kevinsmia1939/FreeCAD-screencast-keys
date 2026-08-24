"""FreeCAD Preferences page."""

from .qt import QtGui, QtWidgets
from .settings import OverlaySettings, load, save


class ColorButton(QtWidgets.QPushButton):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.title = title
        self.color = QtGui.QColor("white")
        self.clicked.connect(self._choose)
        self.setMinimumWidth(100)

    def set_color(self, value):
        color = QtGui.QColor(value)
        if color.isValid():
            self.color = color
        foreground = "#000000" if self.color.lightness() > 145 else "#ffffff"
        self.setText(self.color.name())
        self.setStyleSheet(
            "QPushButton { background: %s; color: %s; padding: 4px; }"
            % (self.color.name(), foreground)
        )

    def _choose(self):
        chosen = QtWidgets.QColorDialog.getColor(self.color, self, self.title)
        if chosen.isValid():
            self.set_color(chosen.name())


class ScreencastKeysPreferencesPage:
    def __init__(self, parent=None):
        self.form = QtWidgets.QWidget(parent)
        self.form.setWindowTitle("General")
        self._build_ui()

    def _build_ui(self):
        root = QtWidgets.QVBoxLayout(self.form)
        root.setContentsMargins(8, 8, 8, 8)

        behavior = QtWidgets.QGroupBox("Behavior")
        behavior_layout = QtWidgets.QFormLayout(behavior)
        self.enabled_now = QtWidgets.QCheckBox("Show Screencast Keys overlay")
        self.enable_startup = QtWidgets.QCheckBox("Enable when FreeCAD starts")
        self.show_mouse_icon = QtWidgets.QCheckBox("Show mouse button status")
        self.show_mouse_labels = QtWidgets.QCheckBox("Show mouse click text (LMB, MMB, RMB)")
        self.repeat_count = QtWidgets.QCheckBox("Combine consecutive events (for example, Tab ×5)")
        behavior_layout.addRow(self.enabled_now)
        behavior_layout.addRow(self.enable_startup)
        behavior_layout.addRow(self.show_mouse_icon)
        behavior_layout.addRow(self.show_mouse_labels)
        behavior_layout.addRow(self.repeat_count)

        appearance = QtWidgets.QGroupBox("Position and appearance")
        form = QtWidgets.QFormLayout(appearance)
        self.corner = QtWidgets.QComboBox()
        for label, value in (
            ("Top left", "top_left"),
            ("Top right", "top_right"),
            ("Bottom left", "bottom_left"),
            ("Bottom right", "bottom_right"),
        ):
            self.corner.addItem(label, value)
        self.keyboard_side = QtWidgets.QComboBox()
        self.keyboard_side.addItem("Left of mouse", "left")
        self.keyboard_side.addItem("Right of mouse", "right")
        self.margin_x = self._spin(0, 500, " px")
        self.margin_y = self._spin(0, 500, " px")
        self.font_size = self._spin(8, 96, " pt")
        self.mouse_size = self._spin(24, 200, " px")
        self.display_time = QtWidgets.QDoubleSpinBox()
        self.display_time.setRange(0.25, 30.0)
        self.display_time.setDecimals(2)
        self.display_time.setSingleStep(0.25)
        self.display_time.setSuffix(" s")
        self.mouse_display_time = QtWidgets.QDoubleSpinBox()
        self.mouse_display_time.setRange(0.1, 30.0)
        self.mouse_display_time.setDecimals(2)
        self.mouse_display_time.setSingleStep(0.1)
        self.mouse_display_time.setSuffix(" s")
        self.mouse_display_time.setToolTip(
            "Keyboard + mouse combinations use the longer of the keyboard and mouse times."
        )
        self.max_history = self._spin(1, 20, " events")
        self.background_opacity = self._spin(0, 100, " %")
        self.background_color = ColorButton("Choose background color", self.form)
        self.text_color = ColorButton("Choose text color", self.form)
        self.accent_color = ColorButton("Choose pressed-button color", self.form)
        form.addRow("Corner:", self.corner)
        form.addRow("Keyboard text position:", self.keyboard_side)
        form.addRow("Distance x from corner :", self.margin_x)
        form.addRow("Distance y from corner:", self.margin_y)
        form.addRow("Keyboard font size:", self.font_size)
        form.addRow("Mouse icon width:", self.mouse_size)
        form.addRow("Keyboard event display time:", self.display_time)
        form.addRow("Mouse click display time:", self.mouse_display_time)
        form.addRow("Maximum history:", self.max_history)
        form.addRow("Background opacity:", self.background_opacity)
        form.addRow("Background color:", self.background_color)
        form.addRow("Text and outline color:", self.text_color)
        form.addRow("Pressed button color:", self.accent_color)

        note = QtWidgets.QLabel(
            "Keyboard and mouse events are observed only while FreeCAD is active. "
            "Keys typed into password fields are replaced by 'Protected input'."
        )
        note.setWordWrap(True)
        note.setEnabled(False)
        root.addWidget(behavior)
        root.addWidget(appearance)
        root.addWidget(note)
        root.addStretch(1)

    @staticmethod
    def _spin(minimum, maximum, suffix):
        widget = QtWidgets.QSpinBox()
        widget.setRange(minimum, maximum)
        widget.setSuffix(suffix)
        return widget

    def loadSettings(self):
        values = load()
        try:
            from .screencastkeys import get_controller
            controller = get_controller()
        except ImportError:
            controller = None
        self.enabled_now.setChecked(controller.enabled if controller else values.enable_on_startup)
        self.enable_startup.setChecked(values.enable_on_startup)
        self.show_mouse_icon.setChecked(values.show_mouse_icon)
        self.show_mouse_labels.setChecked(values.show_mouse_labels)
        self.repeat_count.setChecked(values.repeat_count)
        index = self.corner.findData(values.corner)
        self.corner.setCurrentIndex(max(0, index))
        index = self.keyboard_side.findData(values.keyboard_side)
        self.keyboard_side.setCurrentIndex(max(0, index))
        self.margin_x.setValue(values.margin_x)
        self.margin_y.setValue(values.margin_y)
        self.font_size.setValue(values.font_size)
        self.mouse_size.setValue(values.mouse_size)
        self.display_time.setValue(values.display_time)
        self.mouse_display_time.setValue(values.mouse_display_time)
        self.max_history.setValue(values.max_history)
        self.background_opacity.setValue(values.background_opacity)
        self.background_color.set_color(values.background_color)
        self.text_color.set_color(values.text_color)
        self.accent_color.set_color(values.accent_color)

    def saveSettings(self):
        values = OverlaySettings(
            corner=self.corner.currentData(),
            keyboard_side=self.keyboard_side.currentData(),
            margin_x=self.margin_x.value(),
            margin_y=self.margin_y.value(),
            font_size=self.font_size.value(),
            mouse_size=self.mouse_size.value(),
            display_time=self.display_time.value(),
            mouse_display_time=self.mouse_display_time.value(),
            max_history=self.max_history.value(),
            show_mouse_icon=self.show_mouse_icon.isChecked(),
            show_mouse_labels=self.show_mouse_labels.isChecked(),
            repeat_count=self.repeat_count.isChecked(),
            enable_on_startup=self.enable_startup.isChecked(),
            background_color=self.background_color.color.name(),
            background_opacity=self.background_opacity.value(),
            text_color=self.text_color.color.name(),
            accent_color=self.accent_color.color.name(),
        )
        save(values)
        try:
            from .screencastkeys import get_controller
            controller = get_controller()
            if controller:
                controller.reload_settings()
                controller.set_enabled(self.enabled_now.isChecked())
        except ImportError:
            pass

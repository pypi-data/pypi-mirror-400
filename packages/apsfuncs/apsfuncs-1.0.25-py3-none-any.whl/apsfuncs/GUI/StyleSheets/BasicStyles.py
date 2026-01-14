"""This is a set of standard syles that can be called for a PyQt6 program"""

# Set working colours
PRIMARY = "#2C3E50"
SECONDARY = "#34495E"
LIGHT = "#ECF0F1"
WHITE = "#FFFFFF"
GREY = "#7F8C8D"
BORDER = "#BDC3C7"

# Standard LineEdit
def basic_line_edit(text_colour=PRIMARY, background_colour=WHITE, border_colour=BORDER):
    return f"""
    QLineEdit {{ 
        border: 2px solid {border_colour};
        border-radius: 10px;
        padding: 0 8px;
        background: {background_colour};
        selection-background-color: {background_colour};
        color: {text_colour};
    }}"""

# Standard plain text edit
def basic_text_box(text_colour=PRIMARY, background_colour=WHITE, border_colour=BORDER):
    return f"""
    QPlainTextEdit {{ 
        border: 2px solid {border_colour};
        border-radius: 10px;
        padding: 0 8px;
        background: {background_colour};
        selection-background-color: {background_colour};
        color: {text_colour};
    }}"""

# Standard Label
def basic_label(text_colour=WHITE, background_colour=PRIMARY, border_colour=BORDER):
    return f"""
    QLabel#Basic {{
        color: {text_colour};
        background-color: {background_colour};
        border: 2px solid {border_colour};
        border-color: {border_colour};
        border-radius: 10px;
        font: bold 14px;
        padding: 6px;
    }}"""

# Standard Frame
def basic_frame(background_colour=LIGHT):
    return f"""
    QFrame {{
        background-color: {background_colour} 
    }}"""

# Standard button
def basic_button(text_colour=WHITE, background_colour=PRIMARY, hover_background=SECONDARY, disabled_background=GREY, border_colour=BORDER):
    return f"""
    QPushButton:enabled {{
        color: {text_colour};
        background-color: {background_colour};
        border-style: outset;
        border-width: 2px;
        border-radius: 10px;
        border-color: {border_colour};
        font: bold 14px;
        min-width: 10em;
        padding: 6px;
    }}
        
    QPushButton:disabled {{
        color: {text_colour};
        background-color: {disabled_background};
    }}

    QPushButton:hover {{
        color: {text_colour};
        background: {hover_background};
        border-color: {border_colour};
    }}"""

# Title table
def title_label(text_colour=WHITE, background_colour=PRIMARY, border_colour=BORDER):
    return f"""
    QLabel#Title {{
        color: {text_colour};
        background-color: {background_colour};
        border: 2px solid {border_colour};
        border-color: {border_colour};
        border-radius: 10px;
        font: bold 21px;
        padding: 6px;
    }}"""

# Standard QDialog
def basic_dialog(background_colour=PRIMARY):
    return f"""
    QDialog {{
        background-color: {background_colour} 
    }}"""

# Standard QToolbox
def basic_toolbox(background_colour=GREY, tab_background=PRIMARY, border=BORDER, text_colour=WHITE, hovering_colour=SECONDARY):
    return f"""
    QToolBox {{
        background-color: {background_colour};
        border: 1px solid {border};
    }}

    /* Tab buttons */
    QToolBox::tab {{
        background-color: {tab_background};
        color: {text_colour};
        border: 1px solid {border};
        padding: 2px;
        font-weight: bold;
    }}

    /* Selected tab */
    QToolBox::tab:selected {{
        background-color: {tab_background};
        border-bottom: 2px solid {border};
    }}

    /* Hovered tab */
    QToolBox::tab:hover {{
        background-color: {hovering_colour};
    }}"""

# Standard combobox
def basic_combo_box(background_colour=GREY, dropdown_background=PRIMARY, text_colour=WHITE, border=BORDER, abstract_selection=SECONDARY):
    return f"""
    QComboBox {{
    background-color: {background_colour};
    color: {text_colour};
    border: 1px solid {border};
    padding: 4px 6px;
    min-height: 22px;
    }}

    QComboBox::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 22px;
        border-left: 1px solid {border};
        background-color: {dropdown_background};
        color: "{text_colour}";
    }}

    QComboBox QAbstractItemView {{
        background-color: {background_colour};
        color: {text_colour};
        border: 1px solid {border};
        selection-background-color: {dropdown_background};
        selection-color: {abstract_selection};
    }}"""

#  Standard scroll area widget
def scroll_area_widget(background_colour=GREY):
    return f"""
    CustomVScrollWidget QWidget {{
        background-color: {background_colour}
    }}"""
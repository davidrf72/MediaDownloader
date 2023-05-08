from tkinter import Misc
from typing import Any
from customtkinter import CTkFont
import customtkinter as ctk
from tkinter import *

class HeaderItem(ctk.CTkEntry):
    def __init__(self,  master: Misc | None,
             width: int = 140,
             height: int = 28,
             corner_radius: int | None = None,
             border_width: int | None = None,
             bg_color: str | tuple[str, str] = "transparent",
             fg_color: str | tuple[str, str] | None = None,
             border_color: str | tuple[str, str] | None = None,
             text_color: str | tuple[str, str] | None = None,
             placeholder_text_color: str | tuple[str, str] | None = None,
             textvariable: Variable | None = None,
             placeholder_text: str | None = None,
             font: tuple | CTkFont | None = None,
             state: str = NORMAL,
             **kwargs: Any):
        super(HeaderItem, self).__init__(master, width, height, corner_radius, border_width, bg_color,
             fg_color, border_color, text_color, placeholder_text_color, textvariable, placeholder_text,
             font, state, **kwargs)

    pass
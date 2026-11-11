# Base Theme Class
class Theme:
    def __init__(self, name, background, foreground, canvas, accent, border):
        self.name = name
        self.background = background
        self.foreground = foreground
        self.canvas = canvas
        self.accent = accent
        self.border = border


# Light Theme
class LightTheme(Theme):
    def __init__(self):
        super().__init__(
            name="Light",
            background="#E1E2E4",
            foreground="#000000",
            canvas="#F8F9FA",
            accent="#AD1233",
            border="#696E71"
        )


# Dark Theme
class DarkTheme(Theme):
    def __init__(self):
        super().__init__(
            name="Dark",
            background="#202124",
            foreground="#FFFFFF",
            canvas="#F8F9FA",
            accent="#AD1233",
            border="#696E71"
        )


# Global collection of themes
THEMES = {
    "Light": LightTheme(),
    "Dark": DarkTheme()
}

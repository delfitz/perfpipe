BASE00 = 'base00'  # Default Background
BASE01 = 'base01'  # Lighter Background(Used for status bars, line number and f
BASE02 = 'base02'  # Selection Background
BASE03 = 'base03'  # Comments, Invisibles, Line Highlighting
BASE04 = 'base04'  # Dark Foreground(Used for status bars)
BASE05 = 'base05'  # Default Foreground, Caret, Delimiters, Operators
BASE06 = 'base06'  # Light Foreground(Not often used)
BASE07 = 'base07'  # Light Background(Not often used)
BASE08 = 'base08'  # Variables, XML Tags, Markup Link Text, Markup Lists, Diff
BASE09 = 'base09'  # Integers, Boolean, Constants, XML Attributes, Markup Link
BASE0A = 'base0A'  # Classes, Markup Bold, Search Text Background
BASE0B = 'base0B'  # Strings, Inherited Class, Markup Code, Diff Inserted
BASE0C = 'base0C'  # Support, Regular Expressions, Escape Characters, Markup Qu
BASE0D = 'base0D'  # Functions, Methods, Attribute IDs, Headings
BASE0E = 'base0E'  # Keywords, Storage, Selector, Markup Italic, Diff Changed
BASE0F = 'base0F'  # Deprecated, Opening / Closing Embedded Language Tags, e.g

PALENIGHT = 'palenight'


def getTheme(theme):
    return themes[theme]


themes = {
    PALENIGHT: {
        BASE00: '#292D3E',
        BASE01: '#444267',
        BASE02: '#32374D',
        BASE03: '#676E95',
        BASE04: '#8796B0',
        BASE05: '#959DCB',
        BASE06: '#959DCB',
        BASE07: '#FFFFFF',
        BASE08: '#F07178',
        BASE09: '#F78C6C',
        BASE0A: '#FFCB6B',
        BASE0B: '#C3E88D',
        BASE0C: '#89DDFF',
        BASE0D: '#82AAFF',
        BASE0E: '#C792EA',
        BASE0F: '#FF5370',
    }
}

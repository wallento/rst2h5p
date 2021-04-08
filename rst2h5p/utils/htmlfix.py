from html.parser import HTMLParser
from collections import deque

class HTMLLowerCSSParser(HTMLParser):
    def __init__(self, css):
        super().__init__()
        self.code = []
        self.css = css
        self.hierarchy = deque()
    def match_style(self, css, tree):
        match = []
        for selector in css:
            if "." in selector:
                (selem, sclass) = selector.split(".")
            else:
                (selem, sclass) = (selector, "")

            if (len(selem) == 0 or selem == tree[0][0]) and (len(sclass) == 0 or (sclass in tree[0][1])):
                if isinstance(css[selector], list):
                    match.extend(css[selector])
                else:
                    if len(tree) > 1:
                        match.extend(self.match_style(css[selector], tree[1:]))
            else:
                if len(tree) > 1:
                    match.extend(self.match_style(css, tree[1:]))
        return match

    def apply_styles(self, clazz):
        new_clazz = clazz

        style = self.match_style(self.css, list(self.hierarchy))

        return (style, new_clazz)
    def handle_starttag(self, tag, attrs):
        new_attrs = []
        style = []
        clazz = []
        for attr in attrs:
            if attr[0] == "style":
                style.append(attr[1])
            elif attr[0] == "class":
                clazz = attr[1].split(" ")
            else:
                new_attrs.append(attr)
        self.hierarchy.append((tag, clazz))
        (new_styles, new_clazz) = self.apply_styles(clazz)
        style += new_styles
        if len(style) > 0:
            new_attrs.append(("stylez", ";".join(style)))
        if len(new_clazz) > 0:
            new_attrs.append(("class", " ".join(new_clazz)))
        self.code.append("<{}{}>".format(tag, "".join([" {}=\"{}\"".format(a[0], a[1]) for a  in new_attrs])))
    def handle_endtag(self, tag):
        self.code.append("</{}>".format(tag))
        (exp_tag, _) = self.hierarchy.pop()
        assert exp_tag == tag

    def handle_data(self, data):
        self.code.append(data)

    def handle_comment(self, data):
        self.code.append("<!--{}-->".format(data))

    def handle_entityref(self, name):
        self.code.append("&{};".format(name))

    def handle_charref(self, name):
        self.code.append("&#{};".format(name))

    def handle_decl(self, data):
        self.code.append("<!{}>".format(data))

def lowercss(html, cssfixes):
    if not isinstance(html, list):
        html = [html]

    parser = HTMLLowerCSSParser(cssfixes)

    for text in html:
        parser.feed(text)

    parser.close()
    return parser.code


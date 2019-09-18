PACKAGE   = 'tak'
VERSION   = '0.1.0'
TEMPLATES = 'templates'
PROGNAME  = 'tak'

class Title:
    def __init__(self):
        self.who  = []
        self.what = None

class Slide:
    def __init__(self, text = None, image = None, caption = None):
        if text:
            self.isText = True
            self.text   = text
        elif image:
            self.isImage = True
            self.image   = image
            self.caption = caption

class Presentation:
    def __init__(self, title, slides):
        self.title  = title
        self.slides = slides

class TakSyntaxError(Exception):
    def __init__(self, msg, src = None, lineno = None):
        self.msg    = msg
        self.source = src
        self.lineno = lineno

class Input:
    def __init__(self, s):
        self.s = s

    def __enter__(self):
        return self

    def __exit__(self, a, b, c):
        pass

    def peek(self):
        return self.s[0]

    def skip(self, t):
        if self.s.startswith(t):
            self.s = self.s[len(t):]
        else:
            raise TakSyntaxError(f'Expected "{t}"')

    def skipAny(self):
        self.s = self.s[1:]

    def skipManyChar(self, char):
        count = 0
        while self.s[0] == char:
            self.skipAny()
            count += 1
        return count

    def lookahead(self, t):
        return self.s.startswith(t)

    def skipWhitespace(self):
        self.s = self.s.lstrip()

def parse_image(line):
    with Input(line) as input:
        def getQuoted(input):
            def matching(char):
                if char == '(': return ')'
                if char == '{': return '}'
                if char == '[': return ']'
                if char == '<': return '>'
                if char == '|': return char
                if char == ':': return char
                if char == '"': return char
                if char == "'": return char
            beg = input.peek()
            count = input.skipManyChar(beg)
            end = matching(beg) * count
            res = ''
            while not input.lookahead(end):
                res += input.peek()
                input.skipAny()
            input.skip(end)
            input.skipWhitespace()
            return res
        input.skip('## ')
        input.skipWhitespace()
        return (getQuoted(input), getQuoted(input))

def compile(infile):
    source = infile.name
    title  = Title()
    slides = []
    for lineno, line in enumerate(infile.readlines(), start = 1):
        line = line.strip()
        if line:
            if line.startswith('\\'):
                pass
            elif line.startswith('.title '):
                title.what = line[len('.title '):]
            elif line.startswith('.author '):
                title.who.append(line[len('.author '):])
            elif line.startswith('# '):
                slides.append(Slide(text = line[len('# '):]))
            elif line.startswith('## '):
                try:
                    caption, image = parse_image(line)
                    slides.append(
                        Slide(
                            caption = caption,
                            image   = image
                        )
                    )
                except TakSyntaxError as e:
                    e.source = source
                    e.lineno = lineno
                    raise e
            else:
                raise TakSyntaxError('No/Unknown directive.', source, lineno)

    return Presentation(title = title, slides = slides)

def output(p, outfile, templatefile, autoescape = True):
    import jinja2
    env = jinja2.Environment(
        loader     = jinja2.ChoiceLoader([
            jinja2.FileSystemLoader('.'),
            jinja2.PackageLoader(PACKAGE, TEMPLATES)
        ]),
        autoescape = autoescape
    )
    template = env.get_template(templatefile)
    outfile.write(
        template.render(
            title  = p.title,
            slides = p.slides
        )
    )

def run():
    import sys
    import argparse
    import jinja2
    import os.path
    global PROGNAME

    PROGNAME = os.path.basename(sys.argv[0])
    parser = argparse.ArgumentParser(prog = PROGNAME)
    parser.add_argument(
        '-v', '--version',
        action  = 'store_true',
        default = False,
        help    = 'show the version'
    )
    parser.add_argument(
        '-t', '--template',
        default = 'dark.html',
        help    = 'specify the jinja2 template file'
    )
    parser.add_argument(
        '-n', '--no-escape',
        dest    = 'escape',
        action  = 'store_false',
        default = True,
        help    = 'disable sanitizing content for html'
    )
    parser.add_argument(
        'infile',
        default = sys.stdin,
        type    = argparse.FileType('r'),
        nargs   = '?',
        help    = 'the input file',
        metavar = 'INPUT'
    )
    parser.add_argument(
        'outfile',
        default = sys.stdout,
        type    = argparse.FileType('w'),
        nargs   = '?',
        help    = 'the name of the output file',
        metavar = 'OUTPUT'
    )
    args = parser.parse_args()
    if args.version:
        parser.exit(message = PACKAGE + ' ' + VERSION + '\n')

    def eprint(message):
        parser.error(message = message)

    try:
        output(
            compile(args.infile),
            args.outfile,
            args.template,
            args.escape
        )
    except TakSyntaxError as e:
        eprint(f'{e.source}:{e.lineno}: {e.msg}')
    except jinja2.TemplateNotFound:
        eprint('missing template file.')
    except jinja2.TemplateSyntaxError:
        eprint('syntax error in template file.')
    except OSError as e:
        eprint(e.strerror)

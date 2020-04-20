PACKAGE   = 'tak'
VERSION   = '0.2.0'
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
    import yaml
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
        contents = yaml.safe_load(args.infile)
        title = Title()
        for author in contents['authors']:
            title.who.append(author)
        title.what = contents['title']
        slides = []
        for slide in contents['slides']:
            if 'text' in slide.keys():
                slides.append(Slide(text=slide['text']))
            elif 'image' in slide.keys():
                image = slide['image']
                slides.append(
                    Slide(
                        image=image['file'],
                        caption = image['caption']))
        output(
            Presentation(title=title, slides=slides),
            args.outfile,
            args.template,
            args.escape
        )
    except KeyError as e:
        eprint('expected key "%s" not found.' % (e.args[0]))
    except jinja2.TemplateNotFound:
        eprint('missing template file.')
    except jinja2.TemplateSyntaxError:
        eprint('syntax error in template file.')
    except OSError as e:
        eprint(e.strerror)

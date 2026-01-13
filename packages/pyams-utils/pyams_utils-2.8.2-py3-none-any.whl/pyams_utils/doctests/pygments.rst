
===========================
PyAMS_utils pygments module
===========================

PyAMS_utils "pygments" module can be used to add syntax highlighting to any source code,
using the Pygments package.

    >>> from pyramid.testing import setUp, tearDown, DummyRequest
    >>> config = setUp(hook_zca=True)

    >>> from cornice import includeme as include_cornice
    >>> include_cornice(config)
    >>> from cornice_swagger import includeme as include_swagger
    >>> include_swagger(config)
    >>> from pyams_utils import includeme as include_utils
    >>> include_utils(config)


Pygments styles
---------------

A view is used to get CSS styles:

    >>> from pyams_utils.pygments import get_pygments_style_view
    >>> request = DummyRequest(if_modified_since=None)
    >>> get_pygments_style_view(request).body
    b'pre { line-height: 125%; }...'

    >>> from datetime import datetime, timezone
    >>> request = DummyRequest(if_modified_since=datetime.now(timezone.utc))
    >>> get_pygments_style_view(request).status_code
    304


Pygments lexers vocabulary
--------------------------

A vocabulary provides all Pygments lexers:

    >>> from pyams_utils.pygments import PygmentsLexersVocabulary
    >>> vocabulary = PygmentsLexersVocabulary(None)
    >>> len(vocabulary) > 400
    True
    >>> vocabulary._terms[0].value
    'auto'
    >>> vocabulary._terms[0].title
    'Automatic detection'

    >>> vocabulary._terms[1].value
    'abap'
    >>> vocabulary._terms[1].title
    'ABAP (*.abap, *.ABAP)'

    >>> vocabulary._terms[-1].value
    'zone'
    >>> vocabulary._terms[-1].title
    'Zone (*.zone)'


Pygments styles vocabulary
--------------------------

    >>> from pyams_utils.pygments import PygmentsStylesVocabulary
    >>> vocabulary = PygmentsStylesVocabulary(None)
    >>> len(vocabulary) > 30
    True
    >>> vocabulary._terms[0].value
    'abap'
    >>> vocabulary._terms[1].value
    'algol'
    >>> vocabulary._terms[-1].value
    'zenburn'


Source code rendering
---------------------

    >>> from pyams_utils.pygments import render_source, PygmentsCodeRendererSettings
    >>> settings = PygmentsCodeRendererSettings()
    >>> src = '''def test(value):
    ...     print('Getting value...')
    ...     return value + 1
    ... '''
    >>> render_source(src, settings)
    '<div class="source"><pre><span></span><span class="linenos">1</span><span class="nv">def</span><span class="w"> </span><span class="nv">test</span><span class="ss">(</span><span class="nv">value</span><span class="ss">)</span>:\n<span class="linenos">2</span><span class="w">    </span><span class="nv">print</span><span class="ss">(</span><span class="s1">&#39;Getting value...&#39;</span><span class="ss">)</span>\n<span class="linenos">3</span><span class="w">    </span><span class="k">return</span><span class="w"> </span><span class="nv">value</span><span class="w"> </span><span class="o">+</span><span class="w"> </span><span class="mi">1</span>\n</pre></div>\n'

    >>> settings.lexer = 'python'
    >>> render_source(src, settings)
    '<div class="source"><pre><span></span><span class="linenos">1</span><span class="k">def</span> <span class="nf">test</span><span class="p">(</span><span class="n">value</span><span class="p">):</span>\n<span class="linenos">2</span>    <span class="nb">print</span><span class="p">(</span><span class="s1">&#39;Getting value...&#39;</span><span class="p">)</span>\n<span class="linenos">3</span>    <span class="k">return</span> <span class="n">value</span> <span class="o">+</span> <span class="mi">1</span>\n</pre></div>\n'

    >>> settings.display_linenos = False

    >>> from zope.component import queryMultiAdapter
    >>> from pyams_utils.interfaces.text import IHTMLRenderer
    >>> renderer = queryMultiAdapter((src, request), IHTMLRenderer, name='source-code')
    >>> renderer.render()
    '<div class="source"><pre><span></span><span class="linenos">1</span><span class="nv">def</span><span class="w"> </span><span class="nv">test</span><span class="ss">(</span><span class="nv">value</span><span class="ss">)</span>:\n<span class="linenos">2</span><span class="w">    </span><span class="nv">print</span><span class="ss">(</span><span class="s1">&#39;Getting value...&#39;</span><span class="ss">)</span>\n<span class="linenos">3</span><span class="w">    </span><span class="k">return</span><span class="w"> </span><span class="nv">value</span><span class="w"> </span><span class="o">+</span><span class="w"> </span><span class="mi">1</span>\n</pre></div>\n'


Tests cleanup:

    >>> tearDown()

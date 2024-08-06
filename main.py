from fasthtml.common import *
from fastcore.net import urlparse
import httpx

app, rt = fast_app(pico=False, hdrs=(Link(href='style.css', rel='stylesheet'),))

async def fetch_get(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()

def NavTop(back=False):
    return Div(
        Div(
            Div(
                Img(src="https://news.ycombinator.com/y18.svg", cls="logo"),
                A(B('Hacker News'), href='./'),
                A(NotStr('&nbsp;&nbsp;<< back'), href="./") if back else None,
                cls='header-content'
            ),
            A('code', href="https://github.com/pratapvardhan/hackernews-fasthtml"),
            cls='header-content space-between'),
        cls='header')

def HomeRow(data, n='', pl=True):
    domain = urlparse(data['url']).netloc
    link = f'./item?id={data["id"]}'
    return Div(
        Div(
            Span(f'{n}.' if n else None),
            A(data['title'], href=data['url'], cls='st-t'),
            Span(f'({domain})', cls='st-d') if domain else None,
            cls='st'),
        Div(
            f'{data["points"]} points by', A(data['user']),
            A(data['time_ago'], href=link), ' | ', A(f'{data["comments_count"]} comments', href=link),
            cls=f"st-sub {'pl-15p' if pl else ''}"),
        cls='st'
    )

def Comment(data):
    return Div(
        Div(f"• {data.get('user', '[deleted]')} {data['time_ago']}", cls='st-sub'),
        Div(NotStr(data['content']), cls='st-c'),
        *map(Comment, data['comments']),
        cls='st-cb',
        style=f"margin-left: {'20px' if data['level'] else 0};",
    )

def ScrollMore(page):
    return Div('Scroll for more..', hx_get=f"/?page={page}", hx_trigger="intersect once", hx_swap="outerHTML", hx_target="this", cls='st-c')

async def Feed(page=1, top=True):
    sno = (page - 1) * 30 + 1
    data = await fetch_get(f"https://node-hnapi.herokuapp.com/news?page={page}")
    return *[HomeRow(d, n) for n, d in enumerate(data, sno)], ScrollMore(page+1)

@rt("/")
async def get(page: int = 1):
    content = await Feed(page, top=(page == 1))
    return Div(NavTop(), Div(*content, cls='content'), cls='container') if page == 1 else content

@rt("/item") 
async def get(id:int):
    data = await fetch_get(f"https://node-hnapi.herokuapp.com/item/{id}")
    return Div(
        NavTop(back=True),
        Div(
            HomeRow(data, n='', pl=False),
            Div(NotStr(data.get('content', '')), cls='st-g'), Br(),
            *map(Comment, data['comments']),
            style='padding:0 15px;'
        ),
        cls='container'
    )

serve()
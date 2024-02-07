

# @app.route('/getcatalog/', methods=['GET', 'POST'])
# async def getcatalog():
#     name = request.form.get('name')
#     contact_option = request.form.get('option')
#     contact = request.form.get('contact')
#     await add_query(name, contact, 'Получить каталог', contact_option)
#     return redirect('/')


# @app.route('/submitmessage/', methods=['GET', 'POST'])
# async def submitmessage():
#     name = request.form.get('name')
#     contact = request.form.get('email') + ' / ' + request.form.get('phonenumber')
#     message = request.form.get('message')
#     await add_query(name, contact, message, '-')
#     return redirect('/')


# @app.route('/allqueries/')
# async def allqueries():
#     queries = await get_all_queries()
#     return render_template('allqueries.html', queries=queries)


# # @app.route('/catalog/')
# # def catalog():
# #     return render_template('catalog.html')


from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import starlette.status as status
from .library.helpers import *

app = FastAPI(debug=True, ssl_keyfile="app/adamanto.pro.key", ssl_certfile="app/certificate_ca.crt")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
async def on_startup():
    await init_db()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/tech/{tech_name}", response_class=HTMLResponse)
async def tech(request: Request, tech_name: str):
    if tech_name == '1':
        return templates.TemplateResponse("tech1.html", {"request": request})
    elif tech_name == '2':
        return templates.TemplateResponse("tech2.html", {"request": request})
    elif tech_name == '3':
        return templates.TemplateResponse("tech3.html", {"request": request})
    elif tech_name == '4':
        return templates.TemplateResponse("tech4.html", {"request": request})
    

@app.post("/submitmessage")
async def submitmessage(request: Request, response_class=RedirectResponse):
    data = await request.form()
    data = dict(data)
    name = data['name']
    contact = data['email'] + ' / ' + data['phonenumber']
    message = data['message']
    await add_query(name, contact, message, '-')
    return RedirectResponse('/', status_code=status.HTTP_302_FOUND)


@app.post('/getcatalog')
async def getcatalog(request: Request, response_class=RedirectResponse):
    data = await request.form()
    data = dict(data)
    name = data['name']
    contact_option = data['option']
    contact = data['contact']
    await add_query(name, contact, 'Получить каталог', contact_option)
    return RedirectResponse('/', status_code=status.HTTP_302_FOUND)



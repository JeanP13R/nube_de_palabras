from fastapi import FastAPI, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from wordcloud import WordCloud
import nltk
import matplotlib.pyplot as plt
from io import BytesIO
import pdfplumber
from fastapi.middleware.cors import CORSMiddleware 

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], 

    allow_headers=["*"],

)

@app.get("/")
def index():
    return {"message": "Hello, World!"}

nltk.download("stopwords")

app.mount("/templates", StaticFiles(directory="templates"), name="templates")

# Ruta para cargar el archivo PDF
@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    # Leer el archivo PDF
    pdf_content = await file.read()
    
    # Extraer texto del PDF usando pdfplumber
    texto = ""
    with pdfplumber.open(BytesIO(pdf_content)) as pdf:
        for page in pdf.pages:
            texto += page.extract_text() + "\n"

    # Descargamos las palabras irrelevantes en español
    palabras_irrelevantes = nltk.corpus.stopwords.words("spanish")

    # Opcional: agregar más palabras irrelevantes
    palabras_irrelevantes.append("á")

    # Generar la nube de palabras
    wordcloud = WordCloud(stopwords=palabras_irrelevantes, width=800, height=400, background_color='white').generate(texto)

    # Crear una imagen en memoria
    img = BytesIO()
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()

    # Devolver la imagen en formato binario
    return StreamingResponse(img, media_type="image/png")

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
import os
import mimetypes

app = FastAPI()

# Load environment variables
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
MAX_FILE_SIZE = MAX_FILE_SIZE_MB * 1024 * 1024  # in bytes

# Ensure upload folder exists
os.makedirs(UPLOAD_DIR, exist_ok=True)


# Home page
@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
        <head><title>Content Server</title></head>
        <body>
            <h1>🚀 Welcome to My Python Web Server</h1>
            <p>You can upload and view files here.</p>

            <h2>📤 Upload a File</h2>
            <form action="/upload" enctype="multipart/form-data" method="post">
                <input name="file" type="file">
                <input type="submit" value="Upload">
            </form>

            <h2>📂 Uploaded Files</h2>
            <a href="/files">View Uploaded Files</a>
        </body>
    </html>
    """


# Upload file endpoint
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"❌ File too large! Limit is {MAX_FILE_SIZE_MB} MB."
        )

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(contents)

    return {"message": f"✅ File '{file.filename}' uploaded successfully!"}


# List all uploaded files
@app.get("/files", response_class=HTMLResponse)
async def list_files():
    files = os.listdir(UPLOAD_DIR)
    if not files:
        return "<h3>No files uploaded yet.</h3><a href='/'>⬅ Back to Home</a>"

    file_links = "".join(
        [f'<li><a href="/view/{f}" target="_blank">{f}</a></li>' for f in files]
    )
    return f"""
    <html>
        <body>
            <h2>Uploaded Files</h2>
            <ul>{file_links}</ul>
            <a href="/">⬅ Back to Home</a>
        </body>
    </html>
    """


# View a specific file (auto-detect type)
@app.get("/view/{filename}", response_class=HTMLResponse)
async def view_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    mime_type, _ = mimetypes.guess_type(file_path)

    if mime_type and mime_type.startswith("image"):
        return f"<h2>{filename}</h2><img src='/files/{filename}' width='500'>"

    elif mime_type and mime_type.startswith("video"):
        return f"""
        <h2>{filename}</h2>
        <video width="500" controls>
            <source src="/files/{filename}" type="{mime_type}">
            Your browser does not support video playback.
        </video>
        """

    elif mime_type == "application/pdf":
        return f"""
        <h2>{filename}</h2>
        <embed src="/files/{filename}" type="application/pdf" width="800" height="600">
        """

    else:
        return f"<h2>{filename}</h2><a href='/files/{filename}' download>⬇ Download File</a>"


# Serve file content
@app.get("/files/{filename}")
async def get_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")

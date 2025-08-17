# FastAPI Image Processor

A lFastAPI application for uploading and processing images. This API allows users to upload JPEG or PNG images (up to 5 MB), store them temporarily in memory, and convert them to grayscale upon request. The processed grayscale image is saved to the filesystem and returned to the user, with the original image removed from memory after processing.

## Requirements
- Python 3.10+
- FastAPI (`pip install fastapi`)
- Uvicorn (`pip install uvicorn`)
- Pillow (`pip install pillow`)
- python-multipart (`pip install python-multipart`)

## Installation
1. Clone or download the repository.
   ```bash
   git clone https://github.com/N0ad/test_task
   git checkout task_1
   ```
2. Install dependencies:
   ```bash
   pip install fastapi uvicorn pillow python-multipart
   ```
3. Ensure the `images` and `logs` directories are writable (they will be created automatically if they don't exist).

## Running the Application
Run the FastAPI server locally with auto-reload for development:
```bash
uvicorn main:app --reload
```
The API will be available at `http://127.0.0.1:8000`.

## API Endpoints
- **POST /upload**
  - **Description**: Upload a JPEG or PNG image (≤ 5 MB).
  - **Request**: Multipart form-data with a file field.
  - **Response**: JSON with `image_id` and a note for processing.
  - **Errors**:
    - `400`: Unsupported file type (only JPEG/PNG allowed).
    - `413`: File exceeds 5 MB limit.
  - **Example**:
    ```bash
    curl -X POST -F "file=@image.jpg" http://127.0.0.1:8000/upload
    ```
    Response:
    ```json
    {
      "image_id": "abc123...",
      "note": "Use /process?image_id=abc123... to get grayscale PNG version."
    }
    ```

- **GET /process?image_id=<image_id>**
  - **Description**: Convert the uploaded image to grayscale, save it to `./images`, and return the file. The original image is removed from memory.
  - **Response**: Grayscale PNG file.
  - **Errors**:
    - `404`: Image ID not found.
    - `400`: Processing failed.
  - **Example**:
    ```bash
    curl http://127.0.0.1:8000/process?image_id=abc123... --output grayscale.png
    ```

- **GET /ping**
  - **Description**: Health check endpoint.
  - **Response**: `{"status": "ok"}`
  - **Example**:
    ```bash
    curl http://127.0.0.1:8000/ping
    ```

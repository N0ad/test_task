# FastAPI Image Processor

A FastAPI application for uploading and processing images. This API allows users to upload JPEG or PNG images (up to 5 MB), store them temporarily in memory, and convert them to grayscale upon request. The processed grayscale image is saved to the filesystem and returned to the user, with the original image removed from memory after processing.

## Requirements
- Docker
- Docker Compose

## Installation (Docker)
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/N0ad/test_task
   git checkout task_5
   ```

2. **Install Docker and Docker Compose**

## Running the Application (Docker)
### Option 1: Using Docker Compose
1. **Build the Docker Image**:
   Build the Docker image using Docker Compose:
   ```bash
   docker-compose build
   ```

2. **Run the Application**:
   Start the application using Docker Compose:
   ```bash
   docker-compose up -d
   ```
   - The `-d` flag runs the container in detached mode (in the background).
   - The API will be available at `http://localhost:5000` (or the port specified in the `.env` file).

### Option 2: Using Docker Run
1. **Build the Docker Image**:
   Build the Docker image manually:
   ```bash
   docker build -t fastapi-image-processor:latest .
   ```

2. **Run the Application**:
   Start the container using the `docker run` command:
   ```bash
   docker run -d --name fastapi-image-processor --env-file .env -p 5000:5000 -v "$(pwd)/images:/app/images" -v "$(pwd)/logs:/app/logs" --restart unless-stopped fastapi-image-processor:latest
   ```
   - The `-d` flag runs the container in detached mode.
   - The `--env-file .env` loads environment variables from the `.env` file.
   - The `-p 5000:5000` maps port 5000 on the host to port 5000 in the container.
   - The `-v "$(pwd)/images:/app/images"` and `-v "$(pwd)/logs:/app/logs"` mount the local `images` and `logs` directories to the container.
   - The `--restart unless-stopped` ensures the container restarts automatically unless explicitly stopped.
   - The API will be available at `http://localhost:5000` (or the port specified in the `.env` file).


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
    curl -X POST -F "file=@image.jpg" http://localhost:5000/upload
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
    curl http://localhost:5000/process?image_id=abc123... --output grayscale.png
    ```

- **GET /ping**
  - **Description**: Health check endpoint.
  - **Response**: `{"status": "ok"}`
  - **Example**:
    ```bash
    curl http://localhost:5000/ping
    ```

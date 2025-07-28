"""
module: app
"""
import os
import mimetypes
from flask import Flask, jsonify, redirect, render_template, request, Response, abort, send_from_directory

from db_connect import DBConnection
from helpers import build_html


app = Flask(__name__)
app.config['SECRET_KEY'] = 'brian-the-dinosaur'


@app.route('/', methods=['GET', 'POST'])
def index():
    """

    :return:
    """
    return redirect('/ajax')


@app.route('/ajax', methods=['GET', 'POST'])
def ajax():
    """

    :return:
    """
    form_data = request.form
    return render_template('ajax_test.html', form_data=form_data)


@app.route('/form', methods=['POST'])
def form():
    """
    Method to handle HTML form.
    :return: A string containing HTML build from the output of processing the form.
    """
    if not request:
        return 'Error: no request data'

    request_data = request.get_json()
    q = request_data['query']
    search_table = request_data['tables']
    search_columns = request_data['columns']

    db_conn = DBConnection()
    out_data = db_conn.search(user_query=q, table=search_table, columns=search_columns)

    db_conn.close()

    return jsonify({'html': build_html(db_conn.current_schema, out_data, q)})

@app.route('/stream/<directory>/<filename>',methods=['GET'])
def stream(directory, filename):
    """
        Streams an audio file from the configured directory to the browser client.
        This function is designed to handle HTTP 'Range' requests, which are essential
        for features like seeking (fast-forward/rewind) and resuming playback in audio players.
        """
    audio_dir = os.path.expanduser("~/lanmount/music/"+f"{directory}")
    filepath = os.path.join(audio_dir, filename)

    # Check if the requested file actually exists on the server.
    if not os.path.exists(filepath):
        # If not, return a 404 Not Found error.
        abort(404, description="File not found")

    # Guess the MIME type of the file based on its extension.
    # This tells the browser what type of content it's receiving (e.g., audio/mpeg for MP3).
    mime_type = mimetypes.guess_type(filename)[0]
    if mime_type is None:
        # If the MIME type cannot be guessed, use a generic binary type.
        mime_type = 'application/octet-stream'

    # Get the total size of the file in bytes. This is needed for Content-Length and Content-Range headers.
    file_size = os.path.getsize(filepath)

    # Check for the 'Range' header in the client's request.
    # This header indicates that the client wants only a portion of the file.
    range_header = request.headers.get('Range', None)

    if range_header:
        # --- Handle Partial Content (Range) Requests ---
        # Example Range header formats:
        # "bytes=0-1023" (first 1024 bytes)
        # "bytes=1024-" (from byte 1024 to the end)
        # "bytes=-500" (last 500 bytes)

        try:
            # Extract the byte range string (e.g., "0-1023" or "1024-")
            byte_range_str = range_header.split('=')[1]

            # Initialize start and end bytes. Default to the full file if parts are missing.
            start_byte, end_byte = 0, file_size - 1

            # Parse the start and end bytes from the range string
            parts = byte_range_str.split('-')
            if parts[0]:
                start_byte = int(parts[0])
            if parts[1]:
                end_byte = int(parts[1])
            else:
                # If "bytes=START-" format, stream from START to the end of the file
                end_byte = file_size - 1

            # Validate the requested range to ensure it's within the file's bounds and makes sense.
            if start_byte >= file_size or start_byte > end_byte:
                # Return 416 Range Not Satisfiable if the range is invalid.
                return "Range Not Satisfiable", 416, {'Content-Range': f'bytes */{file_size}'}

            # Calculate the length of the requested chunk.
            length = end_byte - start_byte + 1

            # Define a generator function to read the file in small chunks.
            # This is efficient as it doesn't load the entire file into memory at once.
            def generate_chunks():
                with open(filepath, 'rb') as f:
                    f.seek(start_byte)  # Move the file pointer to the start of the requested range
                    remaining_bytes = length
                    chunk_size = 8192  # Define a suitable chunk size (e.g., 8KB) for streaming

                    while remaining_bytes > 0:
                        # Read a chunk, ensuring we don't read more than 'remaining_bytes'
                        chunk = f.read(min(chunk_size, remaining_bytes))
                        if not chunk:  # Break if end of file is reached prematurely
                            break
                        yield chunk  # Yield the chunk to the response stream
                        remaining_bytes -= len(chunk)  # Update remaining bytes

            # Create a Flask Response object for partial content.
            # Status code 206 indicates Partial Content.
            response = Response(generate_chunks(), 206)

            # Set crucial HTTP headers for partial content streaming:
            response.headers.set('Content-Type', mime_type)  # The MIME type of the audio
            response.headers.set('Content-Length', str(length))  # The size of the *partial* content
            response.headers.set('Content-Range',
                                 f'bytes {start_byte}-{end_byte}/{file_size}')  # The byte range being sent
            response.headers.set('Accept-Ranges', 'bytes')  # Inform the client that the server supports byte ranges

            return response
        except:
            return "Streaming error"

    else:
        # --- Handle Full Content Requests ---
        # If no 'Range' header is present, the client is requesting the entire file.
        # Use Flask's send_from_directory for efficient serving of the full file.
        return send_from_directory(
            audio_dir,
            filename,
            mimetype=mime_type,
            as_attachment=False  # 'False' means display/play in the browser; 'True' forces a download dialog.
        )


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

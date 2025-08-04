from flask import Flask, request, jsonify, send_file
import requests
from PIL import Image, ImageDraw
from io import BytesIO

app = Flask(__name__)

@app.route('/draw', methods=['POST'])
def draw_boxes():
    try:
        data = request.get_json()
        image_url = data.get('imageUrl')
        boxes = data.get('boxes', [])

        if not image_url or not isinstance(boxes, list):
            return jsonify({"error": "Invalid input. 'imageUrl' and a 'boxes' list are required."}), 400

        # Download the image from the URL
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        image = Image.open(response.raw).convert("RGB")

        # Prepare to draw on the image
        draw = ImageDraw.Draw(image)

        # Draw each bounding box
        for item in boxes:
            box = item.get('boundaries')
            if box:
                # Draw the rectangle with a bright green outline
                draw.rectangle(
                    [box['x_min'], box['y_min'], box['x_max'], box['y_max']],
                    outline="lime",
                    width=5  # Adjust line thickness
                )
                # Optional: Add a label
                draw.text(
                    (box['x_min'] + 5, box['y_min'] + 5),
                    item.get('item_type', 'fruit'),
                    fill="white"
                )

        # Save the modified image to a memory buffer
        img_io = BytesIO()
        image.save(img_io, 'PNG')
        img_io.seek(0)

        # Send the image back as a file
        return send_file(img_io, mimetype='image/png')

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Find this at the bottom of your app.py
if __name__ == '__main__':
    # OLD way:
    # app.run(debug=True, port=5001)

    # NEW way for deployment:
    import os
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)
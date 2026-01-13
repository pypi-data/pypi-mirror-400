from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/data", methods=["GET"])
def get_data():
    data = [
        {"id": 1, "title": "Post 1", "body": "This is the first post."},
        {"id": 2, "title": "Post 2", "body": "This is the second post."},
        {"id": 3, "title": "Post 3", "body": "This is the third post."},
    ]
    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True, port=5000)

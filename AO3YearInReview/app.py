from queue import Queue
from threading import Thread

from flask import (
    Flask,
    request,
    jsonify,
    send_from_directory,
    Response,
    send_file
)
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

import json
import sys
import os
from ao3_scraper import scrape_ao3_history
from image_generator import generate_all_stat_images


# --------------------
# Flask app setup
# --------------------

app = Flask(
    __name__,
    static_folder="public",
    static_url_path="/static"
)

# IMPORTANT: tell Flask it is mounted under a prefix
app.config["APPLICATION_ROOT"] = "/AO3YearInReview"

# Respect reverse proxy headers
app.wsgi_app = ProxyFix(app.wsgi_app, x_prefix=1)

CORS(app)

print("Python version:", sys.version)
print("Flask and scraper loaded successfully")


# --------------------
# Routes
# --------------------

@app.route("/")
def index():
    """
    Serve the frontend index.html.
    This works both locally and under /AO3YearInReview/.
    """
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "timestamp": __import__("datetime").datetime.now().isoformat()
    })


@app.route("/api/debug", methods=["GET"])
def debug():
    file_type = request.args.get("file", "login")

    if file_type == "item":
        debug_file = "/tmp/cc-agent/ao3_first_item_debug.html"
    else:
        debug_file = "/tmp/cc-agent/ao3_login_page_debug.html"

    if os.path.exists(debug_file):
        with open(debug_file, "r", encoding="utf-8") as f:
            content = f.read()
        return jsonify({
            "found": True,
            "content": content,
            "length": len(content),
            "file": debug_file
        })

    return jsonify({
        "found": False,
        "message": f"Debug file not found: {debug_file}"
    })


@app.route("/api/stats-image/<image_type>", methods=["GET"])
def get_stats_image(image_type):
    image_files = {
        "ships": "top_ships.png",
        "tags": "top_tags.png",
        "fandoms": "top_fandoms.png",
        "overall": "overall_stats.png"
    }

    if image_type not in image_files:
        return jsonify({"error": "Invalid image type"}), 400

    image_path = os.path.join("/tmp/ao3_stats", image_files[image_type])

    if not os.path.exists(image_path):
        return jsonify({
            "error": "Image not found. Please run scraper first."
        }), 404

    return send_file(image_path, mimetype="image/png")


# --------------------
# Stats calculation
# --------------------

def calculate_statistics(history_items):
    stats = {
        "totalFics": len(history_items),
        "totalWords": 0,
        "topTags": [],
        "topShips": [],
        "topFandoms": [],
        "longestFic": {
            "title": "",
            "wordCount": 0,
            "author": "",
            "url": ""
        }
    }

    tag_counts = {}
    ship_counts = {}
    fandom_counts = {}

    for item in history_items:
        word_count = item.get("wordCount", 0)
        stats["totalWords"] += word_count

        if word_count > stats["longestFic"]["wordCount"]:
            stats["longestFic"] = {
                "title": item.get("title", ""),
                "wordCount": word_count,
                "author": item.get("author", ""),
                "url": item.get("url", "")
            }

        for tag in item.get("tags", []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

        for ship in item.get("relationships", []):
            ship_counts[ship] = ship_counts.get(ship, 0) + 1

        for fandom in item.get("fandoms", []):
            fandom_counts[fandom] = fandom_counts.get(fandom, 0) + 1

    stats["topTags"] = [
        {"tag": tag, "count": count}
        for tag, count in sorted(
            tag_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
    ]

    stats["topShips"] = [
        {"ship": ship, "count": count}
        for ship, count in sorted(
            ship_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
    ]

    stats["topFandoms"] = [
        {"fandom": fandom, "count": count}
        for fandom, count in sorted(
            fandom_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
    ]

    return stats


# --------------------
# Scraping routes
# --------------------

@app.route('/api/scrape-stream', methods=['GET'])
def scrape_stream():
    username = request.args.get('username')
    password = request.args.get('password')
    year = request.args.get('year')

    if not username or not password:
        return Response(
            'event: error\ndata: {"error":"Username and password required"}\n\n',
            mimetype='text/event-stream'
        )

    def generate():
        q = Queue()

        def run_scraper():
            try:
                def on_progress(data):
                    q.put(('progress', data))

                items = scrape_ao3_history(
                    username,
                    password,
                    year if year else None,
                    on_progress=on_progress,
                    retries=3
                )

                stats = calculate_statistics(items)

                try:
                    generate_all_stat_images(stats)
                    stats['imagePaths'] = {
                        'ships': '/api/stats-image/ships',
                        'tags': '/api/stats-image/tags',
                        'fandoms': '/api/stats-image/fandoms',
                        'overall': '/api/stats-image/overall'
                    }
                except Exception as img_err:
                    print("Image generation error:", img_err)
                    stats['imagePaths'] = {}

                q.put(('complete', {'items': items, 'statistics': stats}))

            except Exception as e:
                q.put(('error', {'error': str(e)}))

        Thread(target=run_scraper, daemon=True).start()

        # Immediately tell the client we're alive
        yield 'event: status\ndata: {"message":"started"}\n\n'

        while True:
            event, payload = q.get()
            yield f'event: {event}\ndata: {json.dumps(payload)}\n\n'
            if event in ('complete', 'error'):
                break

    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
        }
    )



@app.route("/api/scrape", methods=["POST"])
def scrape():
    data = request.json or {}
    username = data.get("username")
    password = data.get("password")
    year = data.get("year")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    try:
        history_items = scrape_ao3_history(
            username,
            password,
            year if year else None
        )

        statistics = calculate_statistics(history_items)

        try:
            generate_all_stat_images(statistics)
            statistics["imagePaths"] = {
                "ships": "/api/stats-image/ships",
                "tags": "/api/stats-image/tags",
                "fandoms": "/api/stats-image/fandoms",
                "overall": "/api/stats-image/overall"
            }
        except Exception:
            statistics["imagePaths"] = {}

        return jsonify({
            "items": history_items,
            "statistics": statistics
        })

    except Exception as e:
        return jsonify({
            "error": str(e) or "Failed to scrape history"
        }), 500


# --------------------
# Local dev only
# --------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    print(f"Server running on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)

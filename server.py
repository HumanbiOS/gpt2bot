from sanic.response import json
from sanic import Sanic
import ujson as js
import asyncio
import time
from gpt2bot import get_response

app = Sanic(name="HumanBios-AI")


@app.route('/api/get_response', methods=['POST'])
async def api_get_response(request):
    data = js.loads(request.json)
    resp = await get_response(data['user_id'], data['text']) 
    return json({
        "status": 200,
        "timestamp": time.monotonic(),
        "text": resp
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

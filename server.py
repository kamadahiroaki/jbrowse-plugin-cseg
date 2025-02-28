from flask import Flask, request, send_file
from flask_cors import CORS
import matplotlib.pyplot as plt
import io

app = Flask(__name__)
CORS(app)  # CORSを有効化

@app.route('/render_cseg')
def render_cseg():
    ref_name = request.args.get('region', 'chr1')
    start = int(request.args.get('start', 0))
    end = int(request.args.get('end', 1000))

    fig, ax = plt.subplots(figsize=(10, 2))
    ax.set_xlim(start, end)
    ax.set_ylim(0, 10)

    # 例: 親1の領域（青）、親2の領域（赤）
    ax.fill_between([start, end], 0, 5, color="lightblue", alpha=0.5)
    ax.fill_between([start, end], 5, 10, color="lightcoral", alpha=0.5)

    # 例: SNP マーカー（濃い青・濃い赤）
    snp_positions = [start + (end - start) * i / 10 for i in range(1, 10)]
    ax.scatter(snp_positions, [2] * len(snp_positions), color="blue", label="SNP (P1)")
    ax.scatter(snp_positions, [7] * len(snp_positions), color="red", label="SNP (P2)")

    ax.legend()
    plt.axis("off")

    # 画像をバッファに保存
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format="png", bbox_inches="tight", dpi=100)
    img_buf.seek(0)
    plt.close(fig)  # メモリリークを防ぐ
    
    response = send_file(img_buf, mimetype="image/png")
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

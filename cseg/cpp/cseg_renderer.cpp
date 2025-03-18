#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <vector>
#include <string>
#include <fstream>
#include <sstream>
#include <algorithm>

namespace py = pybind11;

struct Color {
    uint8_t r, g, b;
};

const Color COLORS[] = {
    {200, 200, 200},  // 0: 薄い灰色
    {255, 0, 0},      // 1: 赤
    {0, 0, 255},      // 2: 青
    {255, 100, 100},  // 3: 薄い赤（より濃く）
    {100, 100, 255}   // 4: 薄い青（より濃く）
};

py::array_t<uint8_t> create_cseg_image(
    const std::string& cseg_file,
    const std::string& region_ref,
    int64_t region_start,
    int64_t region_end,
    int canvas_width,
    int sample_height
) {
    // ファイルを開いてサンプル数を取得
    std::ifstream file(cseg_file);
    if (!file) {
        throw std::runtime_error("Could not open file");
    }

    std::string line;
    std::getline(file, line);
    std::istringstream iss(line);
    std::string token;
    int n_samples = -2;  // ref_nameとpositionの2列を引く
    while (std::getline(iss, token, '\t')) {
        n_samples++;
    }

    if (n_samples <= 0) {
        throw std::runtime_error("Invalid file format");
    }

    // 画像の高さを計算
    int canvas_height = n_samples * sample_height;

    // 画像バッファを作成
    auto result = py::array_t<uint8_t>({canvas_height, canvas_width, 3});
    auto buf = result.mutable_unchecked<3>();
    
    // 優先度バッファを作成
    std::vector<uint8_t> priorities(canvas_width * canvas_height, 255);

    // 画像を白で初期化
    for (int y = 0; y < canvas_height; ++y) {
        for (int x = 0; x < canvas_width; ++x) {
            for (int c = 0; c < 3; ++c) {
                buf(y, x, c) = 255;
            }
        }
    }

    // スケール係数を計算
    double scale = static_cast<double>(canvas_width) / (region_end - region_start);

    // ファイルを先頭から読み直し
    file.clear();
    file.seekg(0);

    std::vector<uint8_t> values(n_samples);
    while (std::getline(file, line)) {
        std::istringstream iss(line);
        std::string ref, pos;
        
        // ref_nameとpositionを読む
        if (!std::getline(iss, ref, '\t') || !std::getline(iss, pos, '\t')) {
            continue;
        }

        // ref_nameが一致しない場合はスキップ
        if (ref != region_ref) {
            continue;
        }

        // 位置を解析
        int64_t start, end;
        size_t dash_pos = pos.find('-');
        if (dash_pos != std::string::npos) {
            start = std::stoll(pos.substr(0, dash_pos));
            end = std::stoll(pos.substr(dash_pos + 1));
        } else {
            start = end = std::stoll(pos);
        }

        // 領域が重ならない場合はスキップ
        if (start > region_end || end < region_start) {
            continue;
        }

        // x座標を計算
        int x1, x2;
        if (start == end) {
            int x = static_cast<int>((start - region_start) * scale);
            x = std::min(x, canvas_width - 1);
            x1 = x;
            x2 = x + 1;
        } else {
            x1 = std::max(0, static_cast<int>((start - region_start) * scale));
            x2 = std::min(canvas_width, static_cast<int>((end - region_start) * scale + 1));
        }

        if (x2 <= x1) {
            continue;
        }

        // 値を読み込む
        for (int i = 0; i < n_samples; ++i) {
            std::string value_str;
            if (!std::getline(iss, value_str, '\t')) {
                break;
            }
            values[i] = std::stoi(value_str);
        }

        // 各サンプルについて処理
        for (int sample_idx = 0; sample_idx < n_samples; ++sample_idx) {
            uint8_t value = values[sample_idx];
            if (value > 4) {
                continue;
            }

            // サンプルのy座標範囲
            int y1 = sample_idx * sample_height;
            int y2 = y1 + sample_height;

            // この値の優先度（1=2が最優先、3=4が次、0が最低）
            uint8_t current_priority;
            switch (value) {
                case 1:
                case 2:
                    current_priority = 1;  // 最高優先度
                    break;
                case 3:
                case 4:
                    current_priority = 2;  // 中優先度
                    break;
                default:
                    current_priority = 5;  // 最低優先度
            }

            // この領域を処理
            for (int y = y1; y < y2; ++y) {
                for (int x = x1; x < x2; ++x) {
                    int idx = y * canvas_width + x;
                    if (priorities[idx] > current_priority) {
                        priorities[idx] = current_priority;
                        buf(y, x, 0) = COLORS[value].r;
                        buf(y, x, 1) = COLORS[value].g;
                        buf(y, x, 2) = COLORS[value].b;
                    }
                }
            }
        }
    }

    return result;
}

PYBIND11_MODULE(cseg_renderer, m) {
    m.doc() = "CSEG renderer implementation in C++";
    m.def("create_cseg_image", &create_cseg_image, "Create image from CSEG file",
        py::arg("cseg_file"),
        py::arg("region_ref"),
        py::arg("region_start"),
        py::arg("region_end"),
        py::arg("canvas_width") = 1600,
        py::arg("sample_height") = 5
    );
}

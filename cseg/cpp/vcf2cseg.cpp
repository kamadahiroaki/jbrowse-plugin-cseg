#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <iostream>
#include <string>
#include <vector>
#include <sstream>

namespace py = pybind11;

using namespace std;

const int numFields = 10;

class VcfRecord
{
public:
    string contig;
    int pos;
    string id;
    string ref;
    string alt;
    string qual;
    string filter;
    string info;
    string format;
    vector<string> samples;
};

class CsegRecord
{
public:
    string contig;
    string pos;
    vector<string> genotypes;
};

string convertGenotype(const string &genotype)
{
    if (genotype == "0")
    {
        return "1";
    }
    else if (genotype == "1")
    {
        return "2";
    }
    else
    {
        return "0";
    }
}

// contigごとのデータを処理する関数
void processContigData(const string &contig, const vector<VcfRecord> &contigData, stringstream &output)
{
    vector<CsegRecord> contigCsegData;
    for (int i = 0; i < contigData.size(); i++)
    {
        CsegRecord csegRecord;
        csegRecord.contig = contigData[i].contig;
        csegRecord.pos = to_string(contigData[i].pos);
        for (int j = 0; j < contigData[i].samples.size(); j++)
        {
            csegRecord.genotypes.push_back(contigData[i].samples[j]);
        }
        contigCsegData.push_back(csegRecord);
        if (i < contigData.size() - 1)
        {
            if (contigData[i].pos < contigData[i + 1].pos - 1)
            {
                CsegRecord interval;
                interval.contig = contigData[i].contig;
                interval.pos = to_string(contigData[i].pos + 1) + "-" + to_string(contigData[i + 1].pos - 1);
                for (int j = 0; j < contigData[i].samples.size(); j++)
                {
                    interval.genotypes.push_back("0");
                }
                contigCsegData.push_back(interval);
            }
        }
    }
    for (int j = 0; j < contigCsegData[0].genotypes.size(); j++)
    {
        int lastpos = -1;
        for (int i = 0; i <= contigCsegData.size(); i++)
        {
            if (lastpos < 0)
            {
                if (i < contigCsegData.size() && contigCsegData[i].genotypes[j] != "0")
                {
                    lastpos = i;
                }
            }
            else if (i == contigCsegData.size() || contigCsegData[i].genotypes[j] != "0")
            {
                // 値が異なる場合は白（"0"）を設定
                if (i < contigCsegData.size() && contigCsegData[i].genotypes[j] != contigCsegData[lastpos].genotypes[j])
                {
                    for (int k = lastpos + 1; k < i; k++)
                    {
                        contigCsegData[k].genotypes[j] = "0";
                    }
                }
                // 値が同じ場合は薄い色（+2）を設定
                else
                {
                    string baseValue = (i < contigCsegData.size()) ? contigCsegData[i].genotypes[j] : contigCsegData[lastpos].genotypes[j];
                    for (int k = lastpos + 1; k < i; k++)
                    {
                        contigCsegData[k].genotypes[j] = to_string(stoi(baseValue) + 2);
                    }
                }
                lastpos = i;
            }
        }
    }

    // 結果を出力
    for (const auto &record : contigCsegData)
    {
        output << record.contig << "\t" << record.pos;
        for (const auto &genotype : record.genotypes)
        {
            output << "\t" << genotype;
        }
        output << "\n";
    }
}

string process_vcf_chunk(const string& vcf_chunk) {
    stringstream output;
    string line;
    string currentContig;
    vector<VcfRecord> currentContigData;
    istringstream iss(vcf_chunk);

    try {
        while (getline(iss, line)) {
            if (line.empty() || line[0] == '#') {
                continue;
            }

            vector<string> fields;
            string field;
            istringstream line_iss(line);

            while (getline(line_iss, field, '\t')) {
                fields.push_back(field);
            }

            if (fields.size() >= numFields) {
                VcfRecord record;
                record.contig = fields[0];
                record.pos = stoi(fields[1]);
                record.id = fields[2];
                record.ref = fields[3];
                record.alt = fields[4];
                record.qual = fields[5];
                record.filter = fields[6];
                record.info = fields[7];
                record.format = fields[8];
                for (size_t i = numFields - 1; i < fields.size(); i++) {
                    record.samples.push_back(convertGenotype(fields[i]));
                }

                if (currentContig.empty()) {
                    currentContig = record.contig;
                }

                // 新しいcontigが来たら、前のcontigのデータを処理
                if (currentContig != record.contig) {
                    if (!currentContigData.empty()) {
                        processContigData(currentContig, currentContigData, output);
                        currentContigData.clear();
                    }
                    currentContig = record.contig;
                }

                currentContigData.push_back(record);
            }
        }

        // 最後のcontigのデータを処理
        if (!currentContigData.empty()) {
            processContigData(currentContig, currentContigData, output);
        }

        return output.str();

    } catch (const std::exception& e) {
        throw std::runtime_error(string("Error processing VCF chunk: ") + e.what());
    }
}

PYBIND11_MODULE(vcf2cseg_cpp, m) {
    m.doc() = "VCF to CSEG converter"; // optional module docstring
    m.def("process_vcf_chunk", &process_vcf_chunk, "Process a chunk of VCF data",
          py::arg("vcf_chunk"));
}

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
                    for (int k = lastpos + 1; k < i; k++)
                    {
                        contigCsegData[k].genotypes[j] = to_string(stoi(contigCsegData[i].genotypes[j]) + 2);
                    }
                    lastpos = i;
                }
            }
            else if (i == contigCsegData.size() || contigCsegData[i].genotypes[j] == contigCsegData[lastpos].genotypes[j])
            {
                for (int k = lastpos + 1; k < i; k++)
                {
                    contigCsegData[k].genotypes[j] = to_string(stoi(contigCsegData[lastpos].genotypes[j]) + 2);
                }
                lastpos = i;
            }
            else if (contigCsegData[i].genotypes[j] != "0")
            {
                lastpos = i;
            }
        }
    }
    for (int i = 0; i < contigCsegData.size(); i++)
    {
        output << contigCsegData[i].contig << "\t" << contigCsegData[i].pos << "\t";
        for (int j = 0; j < contigCsegData[i].genotypes.size(); j++)
        {
            output << contigCsegData[i].genotypes[j];
            if (j < contigCsegData[i].genotypes.size() - 1)
            {
                output << "\t";
            }
        }
        output << endl;
    }
}

string convert_vcf_to_cseg(const string& vcf_content) {
    stringstream output;
    string line;
    string currentContig;
    vector<VcfRecord> currentContigData;
    istringstream iss(vcf_content);
    size_t lineCount = 0;

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

                // 新しいcontigが来たら、前のcontigのデータを処理
                if (!currentContig.empty() && currentContig != fields[0]) {
                    processContigData(currentContig, currentContigData, output);
                    currentContigData.clear();
                }

                currentContig = fields[0];
                currentContigData.push_back(record);
            }

            lineCount++;
            if (lineCount % 1000 == 0) {
                // メモリ使用量を確認し、必要に応じて中間処理を行う
                if (currentContigData.size() > 10000) {
                    processContigData(currentContig, currentContigData, output);
                    currentContigData.clear();
                    currentContig = "";
                }
            }
        }

        // 最後のcontigのデータを処理
        if (!currentContigData.empty()) {
            processContigData(currentContig, currentContigData, output);
        }

        return output.str();
    }
    catch (const std::exception& e) {
        throw std::runtime_error(string("Error processing VCF at line ") + to_string(lineCount) + ": " + e.what());
    }
}

PYBIND11_MODULE(vcf2cseg_cpp, m) {
    m.doc() = "VCF to CSEG converter";
    
    py::class_<VcfRecord>(m, "VcfRecord")
        .def(py::init<>())
        .def_readwrite("contig", &VcfRecord::contig)
        .def_readwrite("pos", &VcfRecord::pos)
        .def_readwrite("id", &VcfRecord::id)
        .def_readwrite("ref", &VcfRecord::ref)
        .def_readwrite("alt", &VcfRecord::alt)
        .def_readwrite("qual", &VcfRecord::qual)
        .def_readwrite("filter", &VcfRecord::filter)
        .def_readwrite("info", &VcfRecord::info)
        .def_readwrite("format", &VcfRecord::format)
        .def_readwrite("samples", &VcfRecord::samples);
    
    py::class_<CsegRecord>(m, "CsegRecord")
        .def(py::init<>())
        .def_readwrite("contig", &CsegRecord::contig)
        .def_readwrite("pos", &CsegRecord::pos)
        .def_readwrite("genotypes", &CsegRecord::genotypes);
    
    m.def("convert_vcf_to_cseg", &convert_vcf_to_cseg, "Convert VCF content to CSEG format",
          py::arg("vcf_content"));
    
    m.def("main", []() {
        string input;
        string line;
        while (getline(cin, line)) {
            input += line + "\n";
        }
        
        try {
            string output = convert_vcf_to_cseg(input);
            cout << output;
            return 0;
        } catch (const exception& e) {
            cerr << "Error: " << e.what() << endl;
            return 1;
        }
    }, "Command line interface for VCF to CSEG conversion");
}

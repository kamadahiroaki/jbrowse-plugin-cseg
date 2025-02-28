#include <iostream>
#include <string>
#include <vector>
#include <sstream>

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
void processContigData(const string &contig, const vector<VcfRecord> &contigData)
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
        }
    }
    for (int i = 0; i < contigCsegData.size(); i++)
    {
        cout << contigCsegData[i].contig << "\t" << contigCsegData[i].pos << "\t";
        for (int j = 0; j < contigCsegData[i].genotypes.size(); j++)
        {
            cout << contigCsegData[i].genotypes[j];
            if (j < contigCsegData[i].genotypes.size() - 1)
            {
                cout << "\t";
            }
        }
        cout << endl;
    }

    // for (int j = 0; j < contigCsegData[0].genotypes.size(); j++)
    // {

    //     cout << contigCsegData[0].contig << "\t" << contigCsegData[0].pos << "\t";
    //     for (int i = 0; i < contigCsegData.size(); i++)
    //     {
    //         cout << contigCsegData[i].genotypes[j];
    //         if (i < contigCsegData.size() - 1)
    //         {
    //             cout << "\t";
    //         }
    //     }
    //     cout << endl;
    // }
}

int main()
{
    string line;
    string currentContig;
    vector<VcfRecord> currentContigData;

    while (getline(cin, line))
    {
        vector<string> fields;
        string field;
        istringstream iss(line);

        if (line[0] == '#')
        {
            continue;
        }

        while (getline(iss, field, '\t'))
        {
            fields.push_back(field);
        }

        if (fields.size() >= numFields)
        {
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
            for (size_t i = numFields - 1; i < fields.size(); i++)
            {
                record.samples.push_back(convertGenotype(fields[i]));
            }
            // 新しいcontigが来たら、前のcontigのデータを処理
            if (!currentContig.empty() && currentContig != fields[0])
            {
                processContigData(currentContig, currentContigData);
                currentContigData.clear();
            }

            currentContig = fields[0];
            currentContigData.push_back(record);
        }
    }

    // 最後のcontigのデータを処理
    if (!currentContigData.empty())
    {
        processContigData(currentContig, currentContigData);
    }

    return 0;
}

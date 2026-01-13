#include <iostream>
#include <string>
#include <vector>
using namespace std;

class Element
{
public:
    string name;
    int begin;
    int end;
    int step;
    int precise;
    double current_f;
};

class Material
{
private:
    /* data */
public:
    vector<string> elements;
    vector<int> fractions;
    Material(/* args */);
    ~Material();
    int sum()
    {
        int x = 0;
        for (auto i : fractions)
        {
            x += i;
        }
        return x;
    }
    int push(string element, int fraction)
    {
        elements.push_back(element);
        fractions.push_back(fraction);
        return 1;
    }
};

Material::Material(/* args */)
{
}

Material::~Material()
{
}

int combination(vector<Element> elements, int max, string fileName = "")
{
    if (fileName == "")
    {
        fileName = "EleComb.csv";
    }
    vector<Material> materials;
    for (auto &element : elements)
    {
        for (int current = element.begin; current <= element.end; current += element.step)
        {
        }
    }
}

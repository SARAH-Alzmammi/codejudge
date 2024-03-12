#include <iostream>


using namespace std;

int main() {
    cout << "Snape: \"This task requires your utmost attention to detail. Do not disappoint me.\"\n";

    float length, width, area;

    cout << "Enter the exact length of the classroom: ";
    cin >> length;

    cout << "Enter the exact width of the classroom: ";
    cin >> width;

    area = length * width;

    cout << fixed << setprecision(2);
    cout << "Total available floor area: " << area << " square meters. Ensure it is used wisely.\n";

    return 0;
}
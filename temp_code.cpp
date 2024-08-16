#include <iostream>
#include <string>
using namespace std;

// Function to expand around center and check for palindrome
string expandAroundCenter(const string& s, int left, int right) {
    while (left >= 0 && right < s.length() && s[left] == s[right]) {
        left--;
        right++;
    }
    // Return the substring that is palindromic
    return s.substr(left + 1, right - left - 1);
}

// Function to find the longest palindromic substring
string longestPalindromicSubstring(const string& s) {
    if (s.empty()) return "";
    
    string longest = s.substr(0, 1); // A single character is a palindrome
    for (int i = 0; i < s.length(); i++) {
        // Find longest odd-length palindrome
        string oddPalindrome = expandAroundCenter(s, i, i);
        if (oddPalindrome.length() > longest.length()) {
            longest = oddPalindrome;
        }

        // Find longest even-length palindrome
        string evenPalindrome = expandAroundCenter(s, i, i + 1);
        if (evenPalindrome.length() > longest.length()) {
            longest = evenPalindrome;
        }
    }
    return longest;
}

int main() {
    string input;
    
    getline(cin, input);

    string result = longestPalindromicSubstring(input);
    cout << result << endl
    return 0;
}

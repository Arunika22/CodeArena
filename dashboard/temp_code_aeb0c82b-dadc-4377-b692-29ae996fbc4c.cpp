#include <bits/stdc++.h> 

using namespace std; 
/* Iterative function to reverse digits of num*/
int reverseDigits(int num) 
{ 
  	bool flag = 0;
  	if(num < 0){
      num*=-1;
      flag=1;
    }
	int rev_num = 0; 
	while (num > 0) { 
		rev_num = rev_num * 10 + num % 10; 
		num = num / 10; 
	} 
  if(flag == 1){
    rev_num*=-1;
  }
	return rev_num; 
} 

/*Driver program to test reverseDigits*/
int main() 
{ 
	int num;
  	cin>>num;
	cout <<reverseDigits(num); 
	getchar()
	return 0; 
} 


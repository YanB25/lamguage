# lamguage
## what is it?
lamguage(lambda-language) is a toy language implemented by Python (for fun).  

[this site](http://lisperator.net/pltut/) introduces how to implement your own language, but it is implemented in Javascript.  

This repo provide a python version.
## how to run
```
# input file
f = function(i) {
    if i % 2 == 0 {1;}
    else {0;};
};

fac = function(i) {
    if i == 0 {1;}
    else {i * fac(i-1);}
};

gcd = function(a, b) {
    if a == 0 {
        b;
    } else if b == 0 {
        a;
    } else {
        gcd(b, a % b);
    }
};

print(f(4));
print(f(5));
print(fac(5));
print(gcd(25, 25));
```

``` shell
python interpreter.py
```

output is
```
1
0
120
25
```
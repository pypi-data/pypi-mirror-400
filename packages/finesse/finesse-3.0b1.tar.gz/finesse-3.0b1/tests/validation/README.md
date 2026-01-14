# Validation Tests Readme
The purpose of the validation tests is to ensure that Finesse3 produces scientifically accurate results in known limit cases. To do this we compare against a mixture of known analytic solutions, known numerical results and experimental data.

## Validation Testing Overview
We have constructed the tests inside jupyter notebooks as these allow us to mix our analytic solutions with our code. If you can avoid embedding images into the notebooks it makes the `git diff` easier. One workaround is to save graphs as seperate files and load them using markdown.

### Return Codes
By returning a specific code for a specific type of error, it is possible to classify errors quickly. One way of doing this is to call `sys.exit(<CODE>)`. A table listing the return codes is below, please add to this as required.

#### Reserved Codes
**0**: _All Ok_. Test executed sucessfully, all checks were passed and within tolerance settings.
**1**: _Unexpected Error_. Something unexpected went wrong, this is the default error code for python.

#### 10 Series Codes
Code executed successfully, but did not pass the basic physics checks. Powers should be positive and real etc.

#### 20 Series Codes
The code executed successfully, but returned the wrong output. 20 is reserved for the _main test_, 21-22 are for other physics tests.

#### Output of the Relative Differance
This can be outputted to BEST using ...


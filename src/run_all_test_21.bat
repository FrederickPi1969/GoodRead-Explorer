@echo off
set "sep================================================================================================="
echo %sep%
echo.
echo  ----  Running Server Test Cases  ----
echo.
python server_test.py
echo %sep%
echo. & echo. & echo. 
echo %sep%
echo.
echo  ----  Running Interpreter Test Cases  ----
echo.
python interpreter_test.py
echo %sep%
echo All test finished!
pause 
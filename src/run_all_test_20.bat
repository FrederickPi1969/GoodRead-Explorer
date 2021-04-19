@echo off
set "sep================================================================================================="
echo %sep%
python update_db_test.py
echo %sep%
echo. & echo. & echo. 
echo %sep%
python book_scraper_test.py
echo %sep%
echo. & echo. & echo. 
echo %sep%
python author_scraper_test.py
echo %sep%
echo. & echo. & echo. 
echo All test finished!
pause 
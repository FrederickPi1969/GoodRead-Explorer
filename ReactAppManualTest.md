# React Single-Page-App Manual Test

Table of Contents
-----------------

* [Introduction](#Introduction)
* [Requirements](#Requirements)
* [Get Test](#GetTest)
* [Put Test](#PutTest)
* [Post Test](#PostTest)
* [Get Test](#DeleteTest)
* [Top-K Test](#TopKTest)
* [Overflow Test](OverflowTest)

## Introduction

Assignment-2.2 implements a single-page-application implemented with React.js ( which can be found in `goodread_visualizer` directory) that provides the following functinality:

- `GET` Request Visualizer
  - (i) Find one book/author with provided ID;
  - (ii) Do elastic search with provided query string.
- `PUT` Request Visualizer
  - Provide a form to change values of existing objects in database.
- `POST` Request Visualizer
  - (i) Provide book/author form to insert one new instance into the database.
  - (ii) Provide scrape form to send request to backend server to scrape new data.
- `Delete` Requets Visualizer
  - Delete one book/author with provided ID.
- Top-K Book Visualizer
  - Provide a K-adjustable visualzer (bar chart) for demonstrating the top K rated books implemented with d3.js.
- Top-K Author Visualizer
  - Provide a K-adjustable visualzer (bar chart) for demonstrating the top K rated authors implemented with d3.js.

![](image/ReactAppManualTest/1615786400340.png)

Environment
-----------

JavaScript

- react.js
- d3.js
- mateiral UI
- react-paginate
- react-json-to-table

OS

- Windows

Notice these are only environment where this software got developed and is guranteed to run. They are not meant to be hard requirements.

Also notice one will have to have access to the author's remote MongoDB to actually run with existing DB. Otherwise please configure the MongoDB setting properly to run!

## Get Test

![](image/ReactAppManualTest/1615786475051.png)

### Test -1.1 Find Valid Book

![](image/ReactAppManualTest/1615786529571.png)

![](image/ReactAppManualTest/1615786553651.png)

JSON Correctly fetched and rendered!

### Test -1.2 Find Non-Existing Book

![](image/ReactAppManualTest/1615787809629.png)

![](image/ReactAppManualTest/1615787830466.png)We've got good error report.

### Test -1.3 Elastic Search One Result

![](image/ReactAppManualTest/1615787920168.png)

![](image/ReactAppManualTest/1615787944193.png)

![](image/ReactAppManualTest/1615788018816.png)

There's only one page of results, which is what we expect.


### Test -1.4 Elastic Search Many Results

![](image/ReactAppManualTest/1615788084466.png)

![](image/ReactAppManualTest/1615788145731.png)

![](image/ReactAppManualTest/1615788110415.png)

We got 6 pages of results, which is what we expected.

### Test - 1.5 Bad Elastic Query

![](image/ReactAppManualTest/1615788252520.png)

![](image/ReactAppManualTest/1615788286266.png)

We then get the correct error report.

### Test - 1.6 Elastic Query 0 Result

![](image/ReactAppManualTest/1615788347077.png)

![](image/ReactAppManualTest/1615788363470.png)

Again, good error report.

## Put Test

### Test - 2.1 Existing Book, Good Update JSON

Initial values as below:

![](image/ReactAppManualTest/1615788937014.png)

Update `book_id` to `duckduckgo`

![](image/ReactAppManualTest/1615788966050.png)

![](image/ReactAppManualTest/1615788998962.png)

![](image/ReactAppManualTest/1615789016443.png)

Good success report & value successfully update!

### Test - 2.2 Existing Book, Malformatted Input

![](image/ReactAppManualTest/1615789151953.png)

We got a alert window for the malformatted input & request won't be sent.

### Test - 2.3 Existing Book, Non-Existing Update Key

![](image/ReactAppManualTest/1615789256442.png)

![](image/ReactAppManualTest/1615789282991.png)

Correct error report!

### Test - 2.4 Existing Book, Empty Update Dict

![](image/ReactAppManualTest/1615789353478.png)

![](image/ReactAppManualTest/1615789367972.png)


### Test - 2.5 Updating Non-Existing Book

![](image/ReactAppManualTest/1615789437313.png)

![](image/ReactAppManualTest/1615789481948.png)

## Post Test

![](image/ReactAppManualTest/1615790119232.png)


### Test - 3.1 Upload Many Books

![](image/ReactAppManualTest/1615790182532.png)

According to Bailey Tichner's anwer on campuswire, users should send post request to `api/{books, authors}` directly, instead of filling forms.

### Test - 3.2 Upload One Valid Book

![](image/ReactAppManualTest/1615790495756.png)

![](image/ReactAppManualTest/1615790530268.png)

This is the book form user will have to fill.

![](image/ReactAppManualTest/1615790551808.png)

![](image/ReactAppManualTest/1615790585660.png)

We get correct success message & we can find this in book database with correct information!


### Test - 3.3 Upload One Valid Author

![](image/ReactAppManualTest/1615790819255.png)

![](image/ReactAppManualTest/1615790838209.png)

![](image/ReactAppManualTest/1615790858497.png)

![](image/ReactAppManualTest/1615790910009.png)

### Test - 3.4 Bad Upload Form Submission

Submitting blank form:

![](image/ReactAppManualTest/1615791006104.png)


Submitting non-convertable numeric string in `rating_value/rating_count/review_count`.

![](image/ReactAppManualTest/1615791071522.png)


### Test - 3.5 Bad Scrape Form Submission

Bad numeric string

![](image/ReactAppManualTest/1615791206316.png)

Bad URL

![](image/ReactAppManualTest/1615791263773.png)

### Test - 3.6 Good Scrape Form Submission

![](image/ReactAppManualTest/1615791318607.png)

![](image/ReactAppManualTest/1615791331464.png)

![](image/ReactAppManualTest/1615791367770.png)

Server log implies the request is successful &

We've got good success report.


## Delete Test

### Test - 4.1 Delete Existing Book

![](image/ReactAppManualTest/1615788447402.png)

![](image/ReactAppManualTest/1615788528055.png)

![](image/ReactAppManualTest/1615788581654.png)

Notice book with id 3735293 can be found using get id (Test 1.1).

Now we've got correct success message & book has been removed.

### Test - 4.2 Delete Non-Existing Book

![](image/ReactAppManualTest/1615788812053.png)

![](image/ReactAppManualTest/1615788828606.png)

Correct error report. 

## Top-K Test

### Test - 5.1 Functionality of Top-K Books

5 books

![](image/ReactAppManualTest/1615789771408.png)



10 books

![](image/ReactAppManualTest/1615789565134.png)

20 books

![](image/ReactAppManualTest/1615789808215.png)

Route is update correctly.

Users can use the slider to real-timely adjust `K`.

Xtick is clickable.


### Test - 5.2 Functionality of Top-K Authors

10 authors

![](image/ReactAppManualTest/1615789849758.png)

20 authors

![](image/ReactAppManualTest/1615789885408.png)


Route is update correctly.

Users can use the slider to real-timely adjust `K`.

Xtick is clickable.

## Overflow Test

### Test 6.1 OK/FAIL Scences


![](image/ReactAppManualTest/1615791680026.png)

![](image/ReactAppManualTest/1615792154662.png)

![](image/ReactAppManualTest/1615791985874.png)

![](image/ReactAppManualTest/1615792098177.png)

### Test 6.2 Scollable Rendered JSON

![](image/ReactAppManualTest/1615791733718.png)

![](image/ReactAppManualTest/1615791814255.png)

### Test 6.3 Scollable Top-K Visualization

![](image/ReactAppManualTest/1615791933374.png)

### Test 6.4 Scalable Forms

![](image/ReactAppManualTest/1615792046804.png)

![](image/ReactAppManualTest/1615792206417.png)

![](image/ReactAppManualTest/1615792252677.png)


### Test 6.5 Adaptable Buttons

![](image/ReactAppManualTest/1615792309786.png)

![](image/ReactAppManualTest/1615792336348.png)

![](image/ReactAppManualTest/1615792368311.png)

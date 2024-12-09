# value-finder-core
### Summary
I've been playing around with lots of ideas that really need to determine the fair "value" of  a generic item to know if something is worth buying or can be resold or will it retain its value etc. 
This is a more generic version of the code that I've written to find the fair "value" for a different project.


### Possible improvements:
- Make the percentage profit adjustable.
- Add a lower bound for results that come back 
- Shouldn't really need priority to be provided in the initial file when we (can) dynamically generate it 
- There are definitely inefficiencies in the validations steps that need looking at.


### Detailed Explanation of structure
1.)  Grab the JSON file with the list of search terms and check for duplicate searches and remove them.
2.) Check whether any of the searches are a shortened version of another search and give the longer one a higher priority.
3.) Then uses beautiful soup to grab the first page (240 items) of results for a given search and sorts them into an object this is then saved as a separate JSON 
4.) The point is to stop overlap between similar products so next well look for exact text match in the results and make sure that each ebay item ID belongs to a single search
5.) Then this overwrites the existing ebay result json. The reason we save here is we can rerun the filter steps without having to pull all the data again 
6.) Then we apply some logic to produce data that can be used to produce a box plot which is a good way you visualise the data you can often spot kind of "bubbles" of sale prices if there are variations of a product that are being caught under a single search. ( All this data is again saved to a JSON)
7.) The final step is to produce some statistical values that can then be used to determine what a "good price" would be to both buy and sell that product for.

### Variable Naming Convention

Generally the variable names are camel case with the first character determining the variable type. This is hangover from naming conventions from a previous jobs coding standards.
It is a little flawed in that a python variable can change type line by line but in well written code this should be a non-issue.

variables beginning: 
c - String - "Character"
b - Logical - "Boolean"
o - Object
a - List - "Array"
i - Int
pd - pandas Object (its useful to be able to distinguish)

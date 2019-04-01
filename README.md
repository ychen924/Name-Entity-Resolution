# Name-Entity-Resolution

In this project, there are two datasets that describe the same entities. My goal is to identify which entity in one dataset is the same as an entity in the other dataset. Our datasets were provided by Foursquare and Locu, and contain descriptive information about various venues such as venue names and phone numbers.



## Data Preprocessing

I processed data to standardize all data/values in the two datasets. For example, for attribute ‘phone’, foursquare dataset has ‘phone’ in the format of ‘(xxx) xxx-xxxx’, while locu has a format of ‘xxxxxxxxxx’. By standardizing phone number in the format of ‘xxxxxxxxxx’, I can easily compare the two strings. I also apply the standardization to other features, including converting all strings to upper case, removing special case, etc. 

## Matching Features

I used Levenshtein distance to evaluate the similarity of two strings. After I made the comparison, I assigned the similarity with different scores and append it to a vector table. Attributes like ‘name’, ‘longitude’, ‘latitude’, ‘phone’, and ‘website’ are important factors to determine if the two venues are the same, so I assigned larger scores if two match to these features.

## Classify match and non-match venues

I applied perceptron method to classify matched pairs and unmatched venues, and generated matches file on test datasets. 


## Results
```
Recall： 92.08%
```

```
Precision：98.66%
```

```
F1score： 95.26%
```


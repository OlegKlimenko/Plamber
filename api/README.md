# API documentation (v.1)

This is the api documentation of the existing endpoints for interaction with our application.
All endpoints are separated in logical sections with descriptions and code snippet examples.

You can get more about our project at: https://plamber.com.ua/about

## Start Page endpoints

### Login

The login interaction endpoint.

#### `POST <host>/api/v1/user-login/`

Request payload example:
```JSON
{
  "app_key": "<application_key>",
  "username": "<username>",
  "password": "<password>"
}
```

Success response status  `200`. Response data example:
```JSON
{
  "detail": "successful",
  "data": {
    "token": "<user_token>"
  }
}
```

Incorrect username/password response status `404`. Response data example:
```JSON
{
  "detail": "not authenticated",
  "data": {
    "token": null/false
  }
}
```

Notes:
* The `token` param in the response body example is the token which returned to the user after
  successful authentication process passed. This token must be used for further requests which requires authentication.

### Restore data

Endpoint for restoring user data by sending email to user's inbox with restore instructions.

#### `POST  <host>/api/v1/send-mail/`

Request payload example:
```JSON
{
  "app_key": "<application_key>",
  "email": "<email_to_restore>"
}
```

Success response status `200`. Response data example:
```JSON
{
  "detail": "successful",
  "data": {}
}
```

Email not exists response status `404`. Response data example:
```JSON
{
  "detail": "not exists",
  "data": {}
}
```

### Registration check if _user exists_

There is a validation endpoint to check that entered username is not exists in the application 
to restrict duplicates of usernames (i.e. username is unique)

#### `POST <host>/api/v1/is-user-exists/`

Request payload example:
```JSON
{
  "app_key": "<application_key>",
  "username": "<username>"
}
```

Success response status `200` (user exists/not exists). Response data example:
```JSON
{
  "detail": "successful",
  "data": {
    "user": true/false
  }
}
```

Notes:
* If `user`: true, means that user already exists and app must not proceed registration, allow otherwise.

### Registration check if _email exists_

There is a validation endpoint to check that entered email is not exists in the application 
to restrict duplicates of emails (i.e. email is unique and one user can have only one email and vice-versa)

#### `POST <host>/api/v1/is-mail-exists/`

Request payload example:
```JSON
{
  "app_key": "<application_key>",
  "email": "<email>"
}
```

Success response status `200` (email exists/not exists). Response data example:
```JSON
{
  "detail": "successful",
  "data": {
    "email": true/false
  }
}
```

Notes:
* If `email`: true, means that email already exists and app must not proceed registration, allow otherwise.

### Registration

The final success registration step endpoint.

#### `POST <host>/api/v1/sign-in/`

Request payload example:
```JSON
{
  "app_key": "<application_key>",
  "username": "<username>",
  "email": "<email>",
  "passw1": "<password>"
}
```

Success response status `200`. Response data example:
```JSON
{
  "detail": "successful",
  "data": {
    "token": "<user_token>"
  }
}
```

Not allowed username response status `400` (username must not contain 'admin' substring). Response data example:
```JSON
{
  "detail": "not allowed username",
  "data": {}
}
```

Notes:
* Returns a `<user_token>` which must be stored on the device and used for further requests.

## Home Page endpoints

### Home

Returns the home page data (list of books added by user).

#### `POST <host>/api/v1/home/`

Request payload example:
```JSON
{
  "app_key": "<application_key>",
  "user_token": "<user_token>"
}
```

Success response status `200`. Response data example:
```JSON
{
  "detail": "successful", 
  "data": [
    {
      "id": 123,
      "book_name": "gdfgdfg",
      "id_author": "dfgdfg",
      "id_category": "IT",
      "description": "dfgdfgd",
      "language": "RU",
      "photo": "/media/book_cover/book_18_OuJbZjX.png",
      "book_file": "/media/book_file/berezina_n_a_vyshaya_matematika_kl_aORmYFV.pdf",
      "who_added": "admin",
      "upload_date": "2017-08-10T11:06:55.383732",
      "private_book": false,
      "extension": "FB2"
    },
    {
      "id": 12,
      "book_name": "adgsdg",
      "id_author": "sfdgdsfg",
      "id_category": "IT",
      "description": "sfgsdg",
      "language": "RU",
      "photo": "/media/book_cover/book_1_k7zYDEH.png",
      "book_file": "/media/book_file/smert-bezbiletniku_YupcOlr.pdf",
      "who_added": "admin",
      "upload_date": "2017-08-10T09:49:17.289792",
      "private_book": true,
      "extension": "PDF"
    }
  ]
}
```

Error response status `404` (user with token not exists). Response data example:
```JSON
{
  "details": "not exists"
}
```

### Recommendations

Recommendations endpoint returns the user list of books which system generates by specific algorithm.

#### `POST <host>/api/v1/recommend/`

Request payload example:
```JSON
{
  "app_key": "<application_key>",
  "user_token": "<user_token>"
}
```

Success response status `200`. Response data example:
```JSON
{
  "detail": "successful", 
  "data": [
    {
      "id": 11,
      "book_name": "gdfgdfg",
      "id_author": "dfgdfg",
      "id_category": "IT",
      "description": "dfgdfgd",
      "language": "RU",
      "photo": "/media/book_cover/book_18_OuJbZjX.png",
      "book_file": "/media/book_file/berezina_n_a_vyshaya_matematika_kl_aORmYFV.pdf",
      "who_added": "admin",
      "upload_date": "2017-08-10T11:06:55.383732",
      "private_book": false,
      "extension": "FB2"
    },
    {
      "id": 10,
      "book_name": "adgsdg",
      "id_author": "sfdgdsfg",
      "id_category": "IT",
      "description": "sfgsdg",
      "language": "RU",
      "photo": "/media/book_cover/book_1_k7zYDEH.png",
      "book_file": "/media/book_file/smert-bezbiletniku_YupcOlr.pdf",
      "who_added": "admin",
      "upload_date": "2017-08-10T09:49:17.289792",
      "private_book": true,
      "extension": "PDF"
    }
  ]
}
```

Error response status `404` (user with token not exists). Response data example:
```JSON
{
  "details": "not exists"
}
```

### Uploads

Returns the list of books which were uploaded by authenticated user.

#### `POST <host>/api/v1/uploaded/`

Request payload example:
```JSON
{
  "app_key": "<application_key>",
  "user_token": "<user_token>"
}
```

Success response status `200`. Response data example:
```JSON
{
  "detail": "successful", 
  "data": [
    {
      "id": 13,
      "book_name": "gdfgdfg",
      "id_author": "dfgdfg",
      "id_category": "IT",
      "description": "dfgdfgd",
      "language": "RU",
      "photo": "/media/book_cover/book_18_OuJbZjX.png",
      "book_file": "/media/book_file/berezina_n_a_vyshaya_matematika_kl_aORmYFV.pdf",
      "who_added": "admin",
      "upload_date": "2017-08-10T11:06:55.383732",
      "private_book": false,
      "extension": "PDF"
    },
    {
      "id": 12,
      "book_name": "adgsdg",
      "id_author": "sfdgdsfg",
      "id_category": "IT",
      "description": "sfgsdg",
      "language": "RU",
      "photo": "/media/book_cover/book_1_k7zYDEH.png",
      "book_file": "/media/book_file/smert-bezbiletniku_YupcOlr.pdf",
      "who_added": "admin",
      "upload_date": "2017-08-10T09:49:17.289792",
      "private_book": true,
      "extension": "PDF"
    }
  ]
}
```

Error response status `404` (user with token not exists). Response data example:
```JSON
{
  "details": "not exists"
}
```

## Read Book endpoints

### Read Book

Enpoint for directly reading the book. Returns the data of last read page and some meta information.

#### `POST <host>/api/v1/read-book/`

Request payload example:
```JSON
{
  "app_key": "<application_key>",
  "user_token": "<user_token>",
  "book_id": 56
}
```

Success response status `200`. Response data example:
```JSON
{
  "detail": "successful",
  "data": {
    "last_page": 500
  }
}
```

Error response status `404` 
(user with token not exists; book with id not exists; added book with pair user/book_id don't exists). 
Response data example:
```JSON
{
  "details": "not exists"
}
```

Notes:
* The `last_page` is the last read page. 
  By default this value is **1** which created when book added to list of reading books.

### Set Current page

Endpoint for sending request for change current reading page.

#### `POST <host>/api/v1/set-current-page/`

Request payload example:
```JSON
{
  "app_key": "<application_key>",
  "user_token": "<user_token>",
  "book_id": 56,
  "current_page": 155
}
```

Success response status `200`. Response data example:
```JSON
{
  "detail": "successful",
  "data": {}
}
```

Error response status `404` 
(user with token not exists; book with id not exists; added book with pair user/book_id don't exists). 
Response data example:
```JSON
{
  "details": "not exists"
}
```

Notes:
* The `book_id` and `current_page` params are integer values. 
  If push string validation error will be raised.

## Upload Book endpoints

### Generate Authors

Returns the list of existing authors while user enters some author name while fills upload book form. 
This was implemented to reduce name duplication. So user can select one of the existing names instead of adding new author.

#### `POST <host>/api/v1/generate-authors/`

Request payload example:
```JSON
{
  "app_key": "<application_key>",
  "user_token": "<user_token>",
  "author_part": "auth"
}
```

Success response status `200`. Response data example:
```JSON
{
  "detail": "successful",
  "data": [
    "Author 1",
    "Autho 2",
    "new author",
    "auth"
  ]
}
```

Error response status `404` (user with token not exists). Response data example:
```JSON
{
  "details": "not exists"
}
```

Notes:
* The `author_part` is case insensitive parameter. 

### Generate Books

Returns the list of existing books in the system which matches substring entered by user. 
This was implemented to reduce data duplication. So when user tries to upload some new book into the system, 
if this book is already present system will recommend to start reading it instead of uploading the same book again.

#### `<host>/api/v1/generate-books/`

Request payload example:
```JSON
{
  "app_key": "<application_key>",
  "user_token": "<user_token>",
  "book_part": "lo"
}
```

Success response status `200`. Response data example:
```JSON
{
  "detail": "successful", 
  "data": [
    {
      "id": 12,
      "book_name": "loop path",
      "id_author": "dfgdfg",
      "id_category": "IT",
      "description": "dfgdfgd",
      "language": "RU",
      "photo": "/media/book_cover/book_18_OuJbZjX.png",
      "book_file": "/media/book_file/berezina_n_a_vyshaya_matematika_kl_aORmYFV.pdf",
      "who_added": "admin",
      "upload_date": "2017-08-10T11:06:55.383732",
      "private_book": false,
      "extension": "FB2"
    },
    {
      "id": 10,
      "book_name": "close it",
      "id_author": "sfdgdsfg",
      "id_category": "IT",
      "description": "sfgsdg",
      "language": "RU",
      "photo": "/media/book_cover/book_1_k7zYDEH.png",
      "book_file": "/media/book_file/smert-bezbiletniku_YupcOlr.pdf",
      "who_added": "admin",
      "upload_date": "2017-08-10T09:49:17.289792",
      "private_book": true,
      "extension": "PDF"
    }
  ]
}
```

Error response status `404` (user with token not exists). Response data example:
```JSON
{
  "details": "not exists"
}
```

Notes:
* The `book_part` is case insensitive parameter. 
* When the `book_part` param is empty, an empty list will be returned.

### Fetch Languages

Returns the list of available languages for the uploading book.

#### `POST <host>/api/v1/generate-languages/`

Request payload example:
```JSON
{
  "app_key": "<application_key>",
  "user_token": "<user_token>"
}
```

Success response status `200`. Response data example:
```JSON
{
  "data": [
    "RU",
    "UA"
  ],
  "detail": "successful"
}
```

Error response status `404` (user with token not exists). Response data example:
```JSON
{
  "details": "not exists"
}
```

### Upload Book

The final step of the uploading book with full filled data in the request payload.

#### `POST <host>/api/v1/upload-book/`

Request must be formed as the multipart form data. Fields list:

* **app_key** - The key of the application
* **user_token** - The access user token which we are sending for all requests
* **book_name** - The name of the book
* **author** - Author name
* **category** - The name of the category. The list of categories you can get from categories list API.
* **about** - The description of the book
* **language** - Language to be set for the book
* **book_file** - The book file
* **private_book** - Boolean param.

Success response status `200`. Response data example:
```JSON
{
  "detail": "successful",
  "data": {
    "book": {
      "id": 10,
      "book_name": "close it",
      "id_author": "sfdgdsfg",
      "id_category": "IT",
      "description": "sfgsdg",
      "language": "RU",
      "photo": "/media/book_cover/book_1_k7zYDEH.png",
      "book_file": "/media/book_file/smert-bezbiletniku_YupcOlr.pdf",
      "who_added": "admin",
      "upload_date": "2017-08-10T09:49:17.289792",
      "private_book": true,
      "extension": "PDF"
    }
  }
}
```

Error response status `404` (user with token not exists). Response data example:
```JSON
{
  "details": "not exists"
}
```

Notes:
* After success uploading the book, the system automatically creates relation `Added Book` 
  (i.e. it is pointed as added to list of reading books)

## Library endpoints

### Categories

Returns the list of categories defined in the app.

#### `POST <host>/api/v1/categories/`

Request payload example:
```JSON
{
  "app_key": "<application_key>",
  "user_token": "<user_token>"
}
```

Success response status `200`. Response data example:
```JSON
{
  "data": [
    {
      "id": 1,
      "category_name": "IT",
      "url": "/api/v1/category/1/"
    }
  ],
  "detail": "successful"
}
```

Error response status `404` (user with token not exists). Response data example:
```JSON
{
  "details": "not exists"
}
```

### Selected Category

Returns the list of the books related to the selected category.

#### `POST <host>/api/v1/category/`

Request payload example:
```JSON
{
  "app_key": "<application_key>",
  "user_token": "<user_token>",
  "page": 1,
  "category_id": 15
}
```

Success response status `200`. Response data example:
```JSON
{
  "detail": "successful",
  "data": {
    "next_page": 3,
    "books": [
      {
        "id": 13,
        "book_name": "dlkrgjdflkgjfg",
        "id_author": "DNO",
        "id_category": "IT",
        "description": "dfgdfdfg",
        "language": "RU",
        "photo": "/media/book_cover/book_10_E9gNMYD.png",
        "book_file": "/media/book_file/Evgeniy_Leonidovich_Tverdohlebov_Idealizm_i_nacional-kommunizm_jvH0EXy.pdf",
        "who_added": "admin",
        "upload_date": "2017-08-10T10:08:58.435996",
        "private_book": false,
        "extension": "PDF"
      },
      {
        "id": 10,
        "book_name": "DNO",
        "id_author": "DNO",
        "id_category": "IT",
        "description": "fgdfgdfg",
        "language": "RU",
        "photo": "/media/book_cover/book_2_UBRcqbg.png",
        "book_file": "/media/book_file/polnyj-ahtung-ili-velikaya-tajnaya-kniga-ni-o-chem-i-obo-vsem-srazu_RNLsjR3.pdf",
        "who_added": "admin",
        "upload_date": "2017-08-10T09:50:57.081944",
        "private_book": false,
        "extension": "FB2"
      }
    ]
  }
}
```

Error response status `404` (user with token not exists). Response data example:
```JSON
{
  "details": "not exists"
}
```

Notes:
* The `next_page` param is used for pagination; it can't be less than **1**; 
  if there is no next page, the value will be **0**

### Book Search

Returns the list of the books related to the search term filled in the payload.

#### `POST <host>/api/v1/search-book/`

Request payload example:
```JSON
{
  "app_key": "<application_key>",
  "user_token": "<user_token>",
  "page": 1,
  "search_term": "<term>"
}
```

Success response status `200`. Response data example:
```JSON
{
  "detail": "successful",
  "data": {
    "next_page": 3,
    "books": [
      {
        "id": 13,
        "book_name": "dlkrgjdflkgjfg",
        "id_author": "DNO",
        "id_category": "IT",
        "description": "dfgdfdfg",
        "language": "RU",
        "photo": "/media/book_cover/book_10_E9gNMYD.png",
        "book_file": "/media/book_file/Evgeniy_Leonidovich_Tverdohlebov_Idealizm_i_nacional-kommunizm_jvH0EXy.pdf",
        "who_added": "admin",
        "upload_date": "2017-08-10T10:08:58.435996",
        "private_book": false,
        "extension": "PDF"
      },
      {
        "id": 10,
        "book_name": "DNO",
        "id_author": "DNO",
        "id_category": "IT",
        "description": "fgdfgdfg",
        "language": "RU",
        "photo": "/media/book_cover/book_2_UBRcqbg.png",
        "book_file": "/media/book_file/polnyj-ahtung-ili-velikaya-tajnaya-kniga-ni-o-chem-i-obo-vsem-srazu_RNLsjR3.pdf",
        "who_added": "admin",
        "upload_date": "2017-08-10T09:50:57.081944",
        "private_book": false,
        "extension": "FB2"
      }
    ]
  }
}
```

Error response status `404` (user with token not exists). Response data example:
```JSON
{
  "details": "not exists"
}
```

Notes:
* The search priority is as follows:
  1) `search_term` fully matches with book name
  2) `search_term` is substring of the book name
  3) `search_term` fully matches with author name
  4) `search_term` is substring of the author name
* The `next_page` param is used for pagination; it can't be less than **1**; 
  if there is no next page, the value will be **0**

## Selected Book endpoints

### Selected Book

Returns the detailed info related to the selected book.

#### `POST <host>/api/v1/book/`

Request payload example:
```JSON
{
  "app_key": "<application_key>",
  "user_token": "<user_token>",
  "book_id": 3
}
```

Success response status `200`. Response data example:
```JSON
{
  "detail": "successful",
  "data": {
    "book_rating": 10.0,
    "is_added_book": true,
    "book_rated_count": 1,
    "user_reading_count": 1,
    "comments": [
      {
        "user": "admin",
        "user_photo": "/media/user/user_1.png",
        "text": "FFFF",
        "posted_date": "2017-11-06"
      },
      {
        "user": "admin",
        "user_photo": "/media/user/user_1.png",
        "text": "slkfjskdfsdf",
        "posted_date": "2017-09-30"
      }
    ],
    "book": {
      "id": 1,
      "book_name": "adgsdg",
      "id_author": "sfdgdsfg",
      "id_category": "IT",
      "description": "sfgsdg",
      "language": "RU",
      "photo": "/media/book_cover/book_1_k7zYDEH.png",
      "book_file": "/media/book_file/smert-bezbiletniku_YupcOlr.pdf",
      "who_added": "admin",
      "upload_date": "2017-08-10T09:49:17.289792",
      "private_book": false,
      "extension": "PDF"
    }
  }
}
```

Error response status `404` (user with token not exists; book not exists). Response data example:
```JSON
{
  "details": "not exists"
}
```

Notes:
* `book_rating`: the rating of the books which set by the users. 
   It is a floating point value from **1** to **10**. if 0 no one rated this book at the moment.
* `is_added_book`: boolean value - if **true** current user is reading this book.
* `book_rated_count`: integer value - how many users rated this book.
* `comments`: list with comments which include usernames, user's photo, texts and time when posted.
* `book`: regular book object, nothing special.
* `user_reading_count`: how much users currently added this book to his own library to read.

### Add Book (to list of reading books)

Endpoint for adding books to user's list of reading books.

#### `POST <host>/api/v1/add-book-home/`

Request payload example:
```JSON
{
  "app_key": "<application_key>",
  "user_token": "<user_token>",
  "book_id": 3
}
```

Success response status `200`. Response data example:
```JSON
{
  "detail": "success",
  "data": {}
}
```

Error response status `404` (user with token not exists; book not exists). Response data example:
```JSON
{
  "details": "not exists"
}
```

### Remove Book (from list of reading books)

Endpoint for removing books from user's list of reading books.

#### `POST <host>/api/v1/remove-book-home/`

Request payload example:
```JSON
{
  "app_key": "<application_key>",
  "user_token": "<user_token>",
  "book_id": 3
}
```

Success response status `200`. Response data example:
```JSON
{
  "detail": "success",
  "data": {}
}
```

Error response status `404` (user with token not exists; book not exists; book/user pair not exists). 
Response data example:
```JSON
{
  "details": "not exists"
}
```

### Change Rating

Endpoint for changing rating by logged user on the selected book.

#### `POST <host>/api/v1/change-rating/`

Request payload example:
```JSON
{
  "app_key": "<application_key>",
  "user_token": "<user_token>",
  "book_id": 3,
  "rating": 7
}
```

Success response status `200`. Response data example:
```JSON
{
  "detail": "success",
  "data": {
    "book_rated_count": 1,
    "book_rating": 9.0
  }
}
```

Error response status `404` (user with token not exists; book not exists; book/user pair not exists). 
Response data example:
```JSON
{
  "details": "not exists"
}
```

Notes:
* Request param `rating` must be between **1** and **10** values.

### Add Comment

Endpoint for creating a new comment for selected book at detailed book info.

#### `POST <host>/api/v1/comment-add/`

Request payload example:
```JSON
{
  "app_key": "<application_key>",
  "user_token": "<user_token>",
  "book_id": 3,
  "text": "<comment text>"
}
```

Success response status `200`. Response data example:
```JSON
{
  "detail": "success",
  "data": {
    "user": "admin",
    "user_photo": "/media/user/user_1.png",
    "text": "lol kek 4eburek",
    "posted_date": "2017-11-23"
  }
}
```

Error response status `404` (user token not exists; book with id not exists). Response data example:
```JSON
{
  "details": "not exists"
}
```

## Profile endpoints

### User Profile

Returns user's profile related data.

#### `POST <host>/api/v1/my-profile/`

Request payload example:
```JSON
{
  "app_key": "<application_key>",
  "user_token": "<user_token>"
}
```

Success response status `200`. Response data example:
```JSON
{
  "detail": "successful",
  "data": {
    "profile": {
      "id": 10,
      "username": "<some_username>",
      "email": "<some_email>",
      "user_photo": "/media/user/user_1.png"
    }
  }
}
```

Error response status `404` (user token not exists). Response data example:
```JSON
{
  "details": "not exists"
}
```

### Change Password

Endpoint for changing user's password.

#### `POST <host>/api/v1/change-password/`

Request payload example:
```JSON
{
  "app_key": "<application_key>",
  "user_token": "<user_token>",
  "prev_password": "<old_user_password>",
  "new_password": "<new_user_password>"
}
```

Success response status `200`. Response data example:
```JSON
{
  "detail": "successful",
  "data": {}
}
```

Success response status `200` but error in logic. Response data example:
```JSON
{
  "detail": "old password didn't match",
  "data": {}
}
```

Error response status `404` (user token not exists). Response data example:
```JSON
{
  "details": "not exists"
}
```

Notes:
* The `prev_password` and `new_password` length must be in range 6-16 symbols.

### Upload Avatar

The endpoint for updating user's profile photo.

#### `POST <host>/api/v1/upload-avatar/`

Request must be formed as the multipart form data. Fields list:

* **app_key** - The key of the application
* **user_token** - The access user token which we are sending for all requests
* **file** - The physical file of the user

Success response status `200`. Response data example:
```JSON
{
  "detail": "successful",
  "data": {
    "profile_image": "<url_for_image>"
  }
}
```

Error response status `404` (user token not exists). Response data example:
```JSON
{
  "details": "not exists"
}
```

Error response status `404` (User tried to upload not an image as an avatar). Response data example:
```JSON
{
  "detail": "tried to upload not an image",
  "data": {}
}
```

## Other endpoints

### Send Support Message

Endpoint for sending support messages from users to administrators of the system.

#### `POST <host>/api/v1/send-support-message/`

Request payload example:
```JSON
{
  "app_key": "<application_key>",
  "email": "<user's email>",
  "text": "text message"
}
```

Success response status `200`. Response data example:
```JSON
{
  "detail": "successful",
  "data": {}
}
```

Notes:
* The `text` param max length is **5000** symbols.

### Fetch Reminders

Returns the list of reminders needed to appear in the app to remind do some actions.

#### `POST <host>/api/v1/get-reminders/`

Request payload example:
```JSON
{
  "app_key": "<application_key>",
  "user_token": "<user_token>"
}
```

Success response status `200`. Response data example:
```JSON
{
  "detail": "successful",
  "data": {
    "vk": true,
    "twitter": true,
    "fb_page": true,
    "disabled_all": false,
    "app_rate": true,
    "fb_group": true
  }
}
```

Error response status `404` (user token not exists). Response data example:
```JSON
{
  "details": "not exists"
}
```

### Update Reminders

Updates the state of the reminders after user's action.

#### `POST <host>/api/v1/update-reminder/`

Request payload example:
```JSON
{
  "app_key": "<application_key>",
  "user_token": "<user_token>",
  "field": "twitter",
  "value": false
}
```

Success response status `200`. Response data example:
```JSON
{
    "detail": "successful"
}
```

Error response status `404` (user token not exists). Response data example:
```JSON
{
  "details": "not exists"
}
```

Notes:
* The `field` payload attribute must be one of the keys listed in **Fetch Reminders** response.

## Request Payload validations

Every request payload is validated with validation mechanism by different rules. 
Some of them require any specific data type or, for example, length constraints etc. 

This section represents examples of outputs if any of these Forms 
raised validation exception.

Each response with raised validation exception will return `400` (Bad Request) status code.

### Invalid JSON

```JSON
{
  "detail": "JSON parse error - Expecting property name enclosed in double quotes: line 4 column 1 (char 79)"
}
```

### Missing Params

```JSON
{
  "detail": {
    "book_id": [
      "This field is required."
    ],
    "rating": [
      "This field is required."
    ]
  },
  "data": {}
}
```

### String Length Constraints

#### Too Short String

```JSON
{
  "detail": {
    "username": [
      "Ensure this field has at least 2 characters."
    ]
  },
  "data": {}
}
```

#### Too Long String
```JSON
{
  "detail": {
    "username": [
      "Ensure this field has no more than 30 characters."
    ]
  },
  "data": {}
}
```

### String Regex Constraint

```JSON
{
  "detail": {
    "username": [
      "This value does not match the required pattern."
    ]
  },
  "data": {}
}
```

### Min/Max Numerical Value Constraints

#### Min

```JSON
{
  "detail": {
    "rating": [
      "Ensure this value is greater than or equal to 1."
    ]
  },
  "data": {}
}
```

#### Max

```JSON
{
  "detail": {
    "rating": [
      "Ensure this value is less than or equal to 10."
    ]
  },
  "data": {}
}
```

### Numerical Value Constraint

```JSON
{
  "detail": {
    "rating": [
        "A valid integer is required."
    ]
  },
  "data": {}
}
```

### UUID Value Constraint
```JSON
{
  "detail": {
    "user_token": [
        "\"7d84cbb8-9c9c-c5bc6ea72cce\" is not a valid UUID."
    ]
  },
  "data": {}
}
```

### NOTES

* All `parameters` listed in each payload example are mandatory. There are no optional parameters.
* Each request payload must contain `app_key`. 
  This key is provided by the administrator of the app to allow requests only from trusted client apps.
* Each request payload (which requires user authentication in the request) must contain `user_token`. 
  This token is generated by the system to authenticate user.
# Vibraille Backend Service
#### Authored: Rick Tesmond

#### Contact: richard.d.tesmond@vanderbilt.edu

This backend services provides functionality to convert images to two braille formats: unicode and\
binary, with the intent that this information can be used by haptic drivers. It also handles CRUD \
functionality on Note objects (stored instances of image to braille conversions), as well as user authentication and management.

-----
### Tech stack:
- Django Rest Framework
- AWS Textract and AWS S3
- Postgresql
- SimpleJWT
### How to run locally
1. Ensure you have a version of Python 3.9 installed
2. Create a virtual environment and install the requirements using pip: `pip install -r requirements.txt`
3. Start virtual environment
4. Initialize django models by running: `python manage.py makemigrations`
5. Migrate the new migrations to the backend db: `python manage.py migrate`
6. Optional - create superuser for you local server by running: `python manage.py createsuperuser`
    1. Follow the prompts from the CLI
    2. Creates a new admin level account
    
7. Run your local server: `python manage.py runserver`
    1. Defaults to port 127.0.0.1:8000

### Querying the endpoints manually using CURL:
#### Registration:
`curl -X POST -H "Content-Type: application/json" -d '{"username": "whatever", "email":"you@want.com", "phone_number": "+1(300)123-0000", "password":"itsapass"}' http://localhost:8000/register/`

#### Verifying the email/phone using verification strings from registration
`curl -X PUT -H "Content-Type: application/json" -d '{"phone_number": 13000000, "verify_str":"<value from reg>"}' http://localhost:8000/verify/phone`
`curl -X PUT -H "Content-Type: application/json" -d '{"email": 13000000, "verify_str":"<value from reg>"}' http://localhost:8000/verify/email`

#### Login
`curl  -X POST  -H "Content-Type: application/json"  -d '{"email": "you@want.com", "password": "itsapass"}' http://localhost:8000/login/`

*Make sure you record the access token returned, it is needed for all further queries!!!*

#### Create a Note/Translation using an image
`curl -X POST -H "Authorization: Bearer <access token from login>" -F "img=@<path to your image>"  http://localhost:8000/notes/translate/`

#### View all Notes you've created
`curl -X GET -H "Authorization: Bearer <access token>" http://localhost:8000/notes/`

#### View specific Notes you've created
`curl -X GET -H "Authorization: Bearer <access token>" http://localhost:8000/notes/1/`

#### Edit the title of your first Note
`curl -X PUT -d '{"title": "here we are"}' -H "Content-Type: application/json" -H "Authorization: Bearer <access token>" http://localhost:8000/notes/1/edit`

#### Delete your first Note
`curl -X DELETE -H "Authorization: Bearer <access token>" http://localhost:8000/notes/1/delete`

-----
#API Guide:

## /register/
### Registers a new user.
<table>
  <tr>
   <td>Accepted Methods
   </td>
   <td>POST
   </td>
  </tr>
  <tr>
   <td>Content-Type
   </td>
   <td>application/json
   </td>
  </tr>
  <tr>
   <td>Bearer Token Needed
   </td>
   <td>NO
   </td>
  </tr>
  <tr>
   <td>Success vs. Failure
   </td>
   <td>201, 400
   </td>
  </tr>
  <tr>
   <td>Expected Request Data
   </td>
   <td>{
<p>
    "username": string,
<p>
    "email": string,
<p>
    "phone_number": string,
<p>
    "password": string
<p>
}
   </td>
  </tr>
  <tr>
   <td>Return Data
   </td>
   <td>{
<p>
    "username": string,
<p>
    "email": string,
<p>
    "verification_strings": {
<p>
          "verify_email": string,
<p>
          "verify_phone": string
<p>
    }
<p>
}
   </td>
  </tr>
</table>


## /verify/phone/
### Endpoint for verification of a user’s phone.
<table>
  <tr>
   <td>Accepted Methods
   </td>
   <td>PUT
   </td>
  </tr>
  <tr>
   <td>Content-Type
   </td>
   <td>application/json
   </td>
  </tr>
  <tr>
   <td>Bearer Token Needed
   </td>
   <td>NO
   </td>
  </tr>
  <tr>
   <td>Success vs. Failure
   </td>
   <td>200, 400
   </td>
  </tr>
  <tr>
   <td>Expected Request Data
   </td>
   <td>{
<p>
    “phone_number”: string
<p>
    "verify_str": string,
<p>
}
   </td>
  </tr>
  <tr>
   <td>Return Data
   </td>
   <td>None. If successfully verified it will return 200 responses; 400 responses if not.
   </td>
  </tr>
</table>

## /verify/email/
### Endpoint for verification of a user’s email.
<table>
  <tr>
   <td>Accepted Methods
   </td>
   <td>PUT
   </td>
  </tr>
  <tr>
   <td>Content-Type
   </td>
   <td>application/json
   </td>
  </tr>
  <tr>
   <td>Bearer Token Needed
   </td>
   <td>NO
   </td>
  </tr>
  <tr>
   <td>Success vs. Failure
   </td>
   <td>200, 400
   </td>
  </tr>
  <tr>
   <td>Expected Request Data
   </td>
   <td>{
<p>
    “email”: string,
<p>
    "verify_str": string,
<p>
}
   </td>
  </tr>
  <tr>
   <td>Return Data
   </td>
   <td>None. If successfully verified it will return 200 responses; 400 responses if not.
   </td>
  </tr>
</table>


## /verify/refresh/
### Endpoint for refreshing a user’s verification codes.
<table>
  <tr>
   <td>Accepted Methods
   </td>
   <td>PUT
   </td>
  </tr>
  <tr>
   <td>Content-Type
   </td>
   <td>application/json
   </td>
  </tr>
  <tr>
   <td>Bearer Token Needed
   </td>
   <td>NO
   </td>
  </tr>
  <tr>
   <td>Success vs. Failure
   </td>
   <td>200, 400
   </td>
  </tr>
  <tr>
   <td>Expected Request Data 
<p>
(Option to pass either phone number or email)
   </td>
   <td>{
<p>
    “phone_number”: string |
<p>
    “email”: string
<p>
}
   </td>
  </tr>
  <tr>
   <td>Return Data
   </td>
   <td>{
<p>
    “verification_phone”: string
<p>
    “verification_email”: string
<p>
}
   </td>
  </tr>
</table>

## /login/
### Login…

<table>
  <tr>
   <td>Accepted Methods
   </td>
   <td>POST
   </td>
  </tr>
  <tr>
   <td>Content-Type
   </td>
   <td>application/json
   </td>
  </tr>
  <tr>
   <td>Bearer Token Needed
   </td>
   <td>NO
   </td>
  </tr>
  <tr>
   <td>Success vs. Failure
   </td>
   <td>200, 400/500
   </td>
  </tr>
  <tr>
   <td>Expected Request Data
<ul>

<li>Can use any options (username, email, phone) in conjunction with password
</li>
</ul>
   </td>
   <td>{
<p>
    "username": string |
<p>
    "email": string |
<p>
    "phone_number": string |
<p>
    "password": string
<p>
}
   </td>
  </tr>
  <tr>
   <td>Return Data
   </td>
   <td>{
<p>
    "refresh": string,
<p>
    "access": string,
<p>
    "user": {
<p>
        "verify_email": string,
<p>
        "verify_phone": string,
<p>
        "id": int,
<p>
        "email": string,
<p>
        "phone_number": string,
<p>
        "username": string
<p>
    }
<p>
}
   </td>
  </tr>
</table>


## /login/refresh/
### Renews an JWT access token.
<table>
  <tr>
   <td>Accepted Methods
   </td>
   <td>POST
   </td>
  </tr>
  <tr>
   <td>Content-Type
   </td>
   <td>application/json
   </td>
  </tr>
  <tr>
   <td>Bearer Token Needed
   </td>
   <td>NO
   </td>
  </tr>
  <tr>
   <td>Success vs. Failure
   </td>
   <td>200, 400/500
   </td>
  </tr>
  <tr>
   <td>Expected Request Data
<ul>

<li>Send associated refresh token
</li>
</ul>
   </td>
   <td>{
<p>
    "refresh": string
<p>
}
   </td>
  </tr>
  <tr>
   <td>Return Data
   </td>
   <td>{
<p>
    "access": string
<p>
}
   </td>
  </tr>
</table>

## /notes/
### Returns all notes created by the current user.
<table>
  <tr>
   <td>Accepted Methods
   </td>
   <td>GET
   </td>
  </tr>
  <tr>
   <td>Content-Type
   </td>
   <td>application/json
   </td>
  </tr>
  <tr>
   <td>Bearer Token Needed
   </td>
   <td>YES
   </td>
  </tr>
  <tr>
   <td>Success vs. Failure
   </td>
   <td>200, 404
   </td>
  </tr>
  <tr>
   <td>Expected Request Data
   </td>
   <td>NA
   </td>
  </tr>
  <tr>
   <td>Return Data
<ul>

<li>Returns escaped list of Notes associated with this user.

<li>“Fields” has all the important stuff
</li>
</ul>
   </td>
   <td>[{"model": string, "pk": int,
<p>
  "fields": {
<p>
       "created": date,
<p>
       "title": string,
<p>
       "img": string,
<p>
       "img_name": string,
<p>
       "ascii_text": string,     
<p>
       "braille_format": string,
<p>
      “braille_binary”: string,
<p>
      "user": int,
<p>
    }
<p>
}]
   </td>
  </tr>
</table>


## /notes/translate/
### Translates an image into braille format and creates a Note object.
<table>
  <tr>
   <td>Accepted Methods
   </td>
   <td>POST
   </td>
  </tr>
  <tr>
   <td>Content-Type
   </td>
   <td>Still testing, but multipart/form-data works
   </td>
  </tr>
  <tr>
   <td>Bearer Token Needed
   </td>
   <td>YES
   </td>
  </tr>
  <tr>
   <td>Success vs. Failure
   </td>
   <td>201, 500
   </td>
  </tr>
  <tr>
   <td>Expected Request Data
<ul>

<li>Only need to send the photo
</li>
</ul>
   </td>
   <td>“img”:&lt;path to your file>
   </td>
  </tr>
  <tr>
   <td>Return Data
   </td>
   <td>{
<p>
    “id”: int,
<p>
    “user”: int,
<p>
    "created": string,
<p>
    "title": string,
<p>
    "img": string,
<p>
    "img_name": string,
<p>
    "ascii_text": string,
<p>
    "braille_format": string
<p>
    “braille_binary”: string
<p>
}
   </td>
  </tr>
</table>


## /notes/&lt;id>/
### Get the details on a given Note.
<table>
  <tr>
   <td>Accepted Methods
   </td>
   <td>GET
   </td>
  </tr>
  <tr>
   <td>Content-Type
   </td>
   <td>application/json
   </td>
  </tr>
  <tr>
   <td>Bearer Token Needed
   </td>
   <td>YES
   </td>
  </tr>
  <tr>
   <td>Success vs. Failure
   </td>
   <td>200, 404
   </td>
  </tr>
  <tr>
   <td>Expected Request Data
   </td>
   <td>NA - just specify note ID in URL
   </td>
  </tr>
  <tr>
   <td>Return Data
<ul>

<li>“Fields” has all the important stuff
</li>
</ul>
   </td>
   <td>[{"model": string, "pk": int,
<p>
  "fields": {
<p>
       "created": date,
<p>
       "title": string,
<p>
       "img": string,
<p>
       "img_name": string,
<p>
       "ascii_text": string,     
<p>
       "braille_format": string,
<p>
       “braille_binary”: string,
<p>
       "user": int,
<p>
    }
<p>
}]
   </td>
  </tr>
</table>


## /notes/&lt;id>/edit
### Edit a specific Note. Title is the only edit-appropriate field in Notes.
<table>
  <tr>
   <td>Accepted Methods
   </td>
   <td>PUT
   </td>
  </tr>
  <tr>
   <td>Content-Type
   </td>
   <td>application/json
   </td>
  </tr>
  <tr>
   <td>Bearer Token Needed
   </td>
   <td>YES
   </td>
  </tr>
  <tr>
   <td>Success vs. Failure
   </td>
   <td>200, 401, 404
   </td>
  </tr>
  <tr>
   <td>Expected Request Data
<ul>

<li>Title should be the new title you want on Note.

<li>Title is the only editable field.
</li>
</ul>
   </td>
   <td>{
<p>
    “title”: string
<p>
}
   </td>
  </tr>
  <tr>
   <td>Return Data
   </td>
   <td>[{"model": string, "pk": int,
<p>
  "fields": {
<p>
       "created": date,
<p>
       "title": string,
<p>
       "img": string,
<p>
       "img_name": string,
<p>
       "ascii_text": string,     
<p>
       "braille_format": string,
<p>
       “braille_binary”: string,
<p>
       "user": int,
<p>
    }
<p>
}]
   </td>
  </tr>
</table>

## /notes/&lt;id>/delete
### Delete a specific Note
<table>
  <tr>
   <td>Accepted Methods
   </td>
   <td>DELETE
   </td>
  </tr>
  <tr>
   <td>Content-Type
   </td>
   <td>application/json
   </td>
  </tr>
  <tr>
   <td>Bearer Token Needed
   </td>
   <td>YES
   </td>
  </tr>
  <tr>
   <td>Success vs. Failure
   </td>
   <td>200, 401
   </td>
  </tr>
  <tr>
   <td>Expected Request Data
   </td>
   <td>NA - just specify note ID in URL
   </td>
  </tr>
  <tr>
   <td>Return Data
   </td>
   <td>Status Codes
   </td>
  </tr>
</table>


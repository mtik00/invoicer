# invoicer
Python web app for keeping track of invoices

# Configuration
Create a file named `application.cfg` in your instance folder (which is a
Python file).

Set the following parameters:
*   `SECRET_KEY`: You should always create your own secret key
*   `USERNAME`: The one and only username used for login
*   `PASSWORD_HASH`: The one and only password used for login.  This is an
    *argon2* hash of the password.  Once you install the project requirements,
    you can generate this with the following code:  
    `python -c "from argon2 import PasswordHasher; ph = PasswordHasher(); print ph.hash('mysecretpassword')"`
*   `WKHTMLTOPDF`: The path to the `wkhtmltopdf` binary used for converting the
    HTML invoice to a PDF.
*   `NAME` (optional): Your full name.  This is used as the `<title>` for the
    generated HTML invoice.

Override any other configuration parameters as you see fit.

# PDF Generation
PDFs are generated using [wkhtmltopdf](https://wkhtmltopdf.org/).  You'll need
to install that application and set the `WKHTMLTOPDF` configuration parameter
to its path.

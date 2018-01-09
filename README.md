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
*   `SESSION_TIMEOUT_MINUTES`: The number of minutes before you are
    automatically logged out.  Set this to `None` or `0` to stay logged in.
*   `WKHTMLTOPDF`: The path to the `wkhtmltopdf` binary used for converting the
    HTML invoice to a PDF.
*   `NAME` (optional): Your full name.  This is used as the `<title>` for the
    generated HTML invoice.

Override any other configuration parameters as you see fit.

# PDF Generation
PDFs are generated using [wkhtmltopdf](https://wkhtmltopdf.org/).  You'll need
to install that application and set the `WKHTMLTOPDF` configuration parameter
to its path.

# Initialization
To initialize the application, follow these steps:
*   Create a virtual env and run `pip install -r requirements.txt`
*   Create the instance folder and `instance/application.cfg`
*   Run `flask initdb` (you may want to skip adding sample data)
*   Run the application: `flask run`
*   Open the browser
*   Edit your profile: `http://127.0.0.1:5000/profile/update`
*   Create your *billable units*: `http://127.0.0.1:5000/units`
*   Add a customer: `http://127.0.0.1:5000/customers`
*   Add a new invoice: `http://127.0.0.1:5000/invoice/new`
*   Add new items to the invoice: `http://127.0.0.1:5000/invoice/1/items/new`

# Invoice Submission
Once you have added all of the items, you can click the `Submit Invoice` button.
This is available if you have set up your email server, and the customer has
an email address.

You can only submit the invoice once.  This is to prevent multiple emails to
your customer.  If you need to submit it again, download the PDF and send it
yourself.

The default is to CC `app.config['EMAIL_USERNAME']`.

If `FLASK_DEBUG` is set, only `app.config['EMAIL_USERNAME']` is used.  Customer
email addresses are ignored.

Be sure to check the `Submit` modal dialog for confirmation on where the email
will be sent!